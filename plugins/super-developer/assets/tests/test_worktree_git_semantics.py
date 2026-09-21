"""Git command-semantics checks for the worktree/probe envelope.

Each test drives real git in a throwaway repository and asserts the observable
outcome of a git command recipe hardcoded in this file (ref creation/teardown
ordering, --no-track isolation, portable index digests, moved-base rejection,
and safe local synchronization with a filesystem-only remote).

Scope limit: the recipes are duplicated here, never extracted from the skill
markdown, so these tests do not verify that any prompt still prescribes them.
A prompt could drop --no-track or an ancestry guard and every test here would
still pass. They only pin down what the git commands themselves do.

Prompt content is checked separately; see test_skill_prompts.py for the
content-agnostic structural checks.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class GitEnvelopeSimulationTests(unittest.TestCase):
    def init_repo(self, root: Path) -> None:
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "Contract Test"], check=True)
        (root / "seed").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "seed"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "seed"], check=True)

    def test_removal_precedes_restore_for_tracked_file_to_directory_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            self.init_repo(repo)
            slot = repo / "slot"
            slot.write_text("base\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "slot"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "tracked slot"], check=True)
            paths = Path(temp) / "paths.nul"
            paths.write_bytes(b"slot\0")

            def replace_with_owned_leaf() -> Path:
                slot.unlink()
                slot.mkdir()
                leaf = slot / "owned.tmp"
                leaf.write_text("owned\n", encoding="utf-8")
                return leaf

            leaf = replace_with_owned_leaf()
            restore = [
                "git", "--literal-pathspecs", "-C", str(repo), "restore", "--source=HEAD", "--worktree",
                f"--pathspec-from-file={paths}", "--pathspec-file-nul",
            ]
            subprocess.run(restore, check=True)
            self.assertFalse(leaf.exists(), "Git restore demonstrates the owned-leaf deletion hazard")

            leaf = replace_with_owned_leaf()
            leaf.unlink()
            slot.rmdir()
            subprocess.run(restore, check=True)
            self.assertEqual(slot.read_text(encoding="utf-8"), "base\n")

    def test_no_track_defeats_auto_setup_merge_always(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            worktree = Path(temp) / "probe"
            self.init_repo(repo)
            subprocess.run(["git", "-C", str(repo), "branch", "base"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "branch.autoSetupMerge", "always"], check=True)
            subprocess.run(
                ["git", "-C", str(repo), "worktree", "add", "-q", "--no-track", "-b", "probe/f/q/a1", str(worktree), "base"],
                check=True,
            )
            upstream = subprocess.check_output(
                ["git", "-C", str(repo), "for-each-ref", "--format=%(upstream)", "refs/heads/probe/f/q/a1"], text=True
            ).strip()
            self.assertEqual(upstream, "")
            for key in ("remote", "merge", "pushRemote"):
                result = subprocess.run(
                    ["git", "-C", str(repo), "config", "--get", f"branch.probe/f/q/a1.{key}"],
                    check=False,
                    stdout=subprocess.PIPE,
                    text=True,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")

    def test_probe_creation_and_cleanup_agree_on_the_full_direct_ref(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            worktree = Path(temp) / "probe"
            self.init_repo(repo)
            subprocess.run(["git", "-C", str(repo), "branch", "feature/demo"], check=True)
            expected = subprocess.check_output(
                ["git", "-C", str(repo), "rev-parse", "feature/demo"], text=True
            ).strip()
            script = r'''
set -euo pipefail
BRANCH="probe/demo/q1/a1"
REF="refs/heads/$BRANCH"
test "$(git rev-parse "$BASE_REF")" = "$EXPECTED_BASE_SHA"
git worktree add -q --no-track -b "$BRANCH" "$WT" "$EXPECTED_BASE_SHA"
test "$(git rev-parse "$BASE_REF")" = "$EXPECTED_BASE_SHA"
test "$(git -C "$WT" symbolic-ref -q HEAD)" = "$REF"
test "$(git rev-parse "$REF")" = "$EXPECTED_BASE_SHA"
test -z "$(git config --get "branch.$BRANCH.remote" || :)"
test -z "$(git config --get "branch.$BRANCH.merge" || :)"
test -z "$(git config --get "branch.$BRANCH.pushRemote" || :)"
git worktree remove "$WT"
if git symbolic-ref -q "$REF"; then exit 1; fi
git update-ref --no-deref -d "$REF" "$EXPECTED_BASE_SHA"
test -z "$(git show-ref --verify --hash "$REF" 2>/dev/null || :)"
'''
            result = subprocess.run(
                ["bash", "-c", script],
                cwd=repo,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env={
                    **os.environ,
                    "BASE_REF": "feature/demo",
                    "EXPECTED_BASE_SHA": expected,
                    "WT": str(worktree),
                },
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertFalse(worktree.exists())
            self.assertNotEqual(
                subprocess.run(
                    ["git", "-C", str(repo), "show-ref", "--verify", "--quiet", "refs/heads/probe/demo/q1/a1"],
                    check=False,
                ).returncode,
                0,
            )

    def test_index_digest_uses_portable_non_writing_git_hash_object(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            self.init_repo(repo)
            manifest = Path(temp) / "initial-index.nul"
            manifest.write_bytes(
                subprocess.check_output(["git", "-C", str(repo), "ls-files", "--stage", "-z"])
            )
            before = subprocess.check_output(["git", "-C", str(repo), "count-objects", "-v"], text=True)
            digest = subprocess.check_output(
                ["git", "-C", str(repo), "hash-object", "--no-filters", str(manifest)], text=True
            ).strip()
            after = subprocess.check_output(["git", "-C", str(repo), "count-objects", "-v"], text=True)
            repeated = subprocess.check_output(
                ["git", "-C", str(repo), "hash-object", "--no-filters", str(manifest)], text=True
            ).strip()
            self.assertEqual(digest, repeated)
            self.assertEqual(before, after)

    def test_moved_expected_probe_base_is_rejected_before_worktree_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            worktree = Path(temp) / "probe"
            self.init_repo(repo)
            subprocess.run(["git", "-C", str(repo), "branch", "feature/demo"], check=True)
            expected = subprocess.check_output(
                ["git", "-C", str(repo), "rev-parse", "feature/demo"], text=True
            ).strip()
            (repo / "seed").write_text("moved\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "commit", "-qam", "move base"], check=True)
            subprocess.run(["git", "-C", str(repo), "branch", "-f", "feature/demo", "HEAD"], check=True)
            script = r'''
set -euo pipefail
BRANCH="probe/demo/q1/a1"; REF="refs/heads/$BRANCH"
test "$(git rev-parse "$BASE_REF")" = "$EXPECTED_BASE_SHA"
git worktree add --no-track -b "$BRANCH" "$WT" "$EXPECTED_BASE_SHA"
test "$(git rev-parse "$BASE_REF")" = "$EXPECTED_BASE_SHA"
'''
            result = subprocess.run(
                ["bash", "-c", script],
                cwd=repo,
                check=False,
                env={
                    **os.environ,
                    "BASE_REF": "feature/demo",
                    "EXPECTED_BASE_SHA": expected,
                    "WT": str(worktree),
                },
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(worktree.exists())
            self.assertNotEqual(
                subprocess.run(
                    ["git", "-C", str(repo), "show-ref", "--verify", "--quiet", "refs/heads/probe/demo/q1/a1"],
                    check=False,
                ).returncode,
                0,
            )

    def test_moved_reviewed_base_is_rejected_before_worktree_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            worktree = Path(temp) / "wp-WP2"
            self.init_repo(repo)
            subprocess.run(["git", "-C", str(repo), "branch", "feature/demo"], check=True)
            reviewed = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "feature/demo"], text=True).strip()
            (repo / "seed").write_text("moved\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "commit", "-qam", "move base"], check=True)
            subprocess.run(["git", "-C", str(repo), "branch", "-f", "feature/demo", "HEAD"], check=True)
            script = 'test "$(git rev-parse feature/demo)" = "$REVIEWED_BASE_SHA" && git worktree add --no-track -b wp/demo/WP2 "$WT" "$REVIEWED_BASE_SHA"'
            result = subprocess.run(
                ["bash", "-c", script], cwd=repo, check=False,
                env={**os.environ, "REVIEWED_BASE_SHA": reviewed, "WT": str(worktree)},
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(worktree.exists())
            branch = subprocess.run(
                ["git", "-C", str(repo), "show-ref", "--verify", "--quiet", "refs/heads/wp/demo/WP2"], check=False
            )
            self.assertNotEqual(branch.returncode, 0)


class PrTargetSynchronizationTests(unittest.TestCase):
    """Real Git primitives, not a simulation of GitHub or agent decisions."""

    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.env.update({
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0", "GIT_ALLOW_PROTOCOL": "file",
        })
        self.base = "release/next"
        self.ref = f"refs/heads/{self.base}"
        self.tracking = f"refs/remotes/pr-target/{self.base}"
        self.remote = self.root / "remote.git"
        self.producer = self.root / "remote writer"
        self.repo = self.root / "local"
        self.git(self.root, "init", "--bare", "-q", str(self.remote))
        self.git(self.root, "init", "-q", "-b", self.base, str(self.producer))
        self.commit(self.producer, "seed", "seed\n")
        self.git(self.producer, "remote", "add", "pr-target", str(self.remote))
        self.git(self.producer, "push", "-q", "pr-target", f"HEAD:{self.ref}")
        self.git(self.root, "clone", "-q", "--origin", "pr-target", "--branch", self.base,
                 str(self.remote), str(self.repo))
        self.old = self.sha(self.repo)
        self.commit(self.producer, "accepted", "merged PR\n")
        self.merged = self.sha(self.producer)
        self.git(self.producer, "push", "-q", "pr-target", f"HEAD:{self.ref}")

    def git(self, repo: Path, *args: str, check: bool = True,
            input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-c", "core.hooksPath=/dev/null", "-c", "submodule.recurse=false",
             "-c", "commit.gpgsign=false", "-c", "user.name=Contract Test",
             "-c", "user.email=test@example.com", "-C", str(repo), *args],
            env=self.env, check=check, text=True, input=input_text, capture_output=True, timeout=15,
        )

    def sha(self, repo: Path, ref: str = "HEAD") -> str:
        return self.git(repo, "rev-parse", ref).stdout.strip()

    def commit(self, repo: Path, path: str, content: str) -> None:
        (repo / path).write_text(content, encoding="utf-8")
        self.git(repo, "add", "--", path)
        self.git(repo, "commit", "-qm", path)

    def fetch_target(self) -> str:
        self.git(self.repo, "fetch", "-q", "--no-tags", "--no-recurse-submodules", "--refmap=",
                 "pr-target", f"{self.ref}:{self.tracking}")
        target = self.sha(self.repo, self.tracking)
        self.git(self.repo, "merge-base", "--is-ancestor", self.merged, target)
        return target

    def checked_out_ff(self, worktree: Path, old: str, target: str) -> subprocess.CompletedProcess[str]:
        # Identity/cleanliness/ancestry plus the actual FF primitive; policy must
        # separately resolve occupancy, authority and merge status before this.
        script = r'''
set -euo pipefail
g() { git -c core.hooksPath=/dev/null -c submodule.recurse=false -C "$WT" "$@"; }
test "$(g symbolic-ref -q HEAD)" = "$BASE_REF"
test "$(g rev-parse HEAD)" = "$OLD"
g diff --quiet HEAD --
g diff --cached --quiet
g merge-base --is-ancestor "$OLD" "$TARGET"
g merge --ff-only --no-autostash --no-overwrite-ignore "$TARGET"
test "$(g rev-parse HEAD)" = "$TARGET"
'''
        return subprocess.run(
            ["bash", "-c", script], cwd=self.root,
            env={**self.env, "WT": str(worktree), "BASE_REF": self.ref, "OLD": old, "TARGET": target},
            check=False, text=True, capture_output=True, timeout=15,
        )

    def test_non_main_base_ff_preserves_untracked_ignored_files_and_skips_hooks(self) -> None:
        target = self.fetch_target()
        (self.repo / ".pi").mkdir()
        (self.repo / ".pi/session").write_text("keep\n", encoding="utf-8")
        (self.repo / ".git/info/exclude").write_text("ignored\n", encoding="utf-8")
        (self.repo / "ignored").write_text("keep ignored\n", encoding="utf-8")
        hook = self.repo / ".git/hooks/post-merge"
        hook.write_text('#!/bin/sh\nprintf invoked > "$PWD/hook-ran"\n', encoding="utf-8")
        hook.chmod(0o755)
        result = self.checked_out_ff(self.repo, self.old, target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.sha(self.repo), self.merged)
        self.assertEqual(self.sha(self.repo, self.tracking), target)
        self.assertEqual(self.git(self.repo, "symbolic-ref", "HEAD").stdout.strip(), self.ref)
        self.assertEqual((self.repo / ".pi/session").read_text(), "keep\n")
        self.assertEqual((self.repo / "ignored").read_text(), "keep ignored\n")
        self.assertFalse((self.repo / "hook-ran").exists())

    def test_linked_base_updates_without_switching_or_editing_unrelated_current_branch(self) -> None:
        self.git(self.repo, "switch", "-qc", "feature/topic")
        (self.repo / "seed").write_text("user edit\n", encoding="utf-8")
        before_index = self.git(self.repo, "ls-files", "--stage", "-z").stdout
        checkout = self.root / "base checkout\nwith space"
        self.git(self.repo, "worktree", "add", "-q", str(checkout), self.base)
        records = self.git(self.repo, "worktree", "list", "--porcelain", "-z").stdout.split("\0\0")
        owners = [record for record in records if f"branch {self.ref}\0" in record + "\0"]
        self.assertEqual(len(owners), 1)
        self.assertEqual(owners[0].split("\0")[0], f"worktree {checkout}")
        self.git(self.repo, "config", "remote.pr-target.fetch", f"{self.ref}:refs/heads/feature/topic")
        target = self.fetch_target()
        result = self.checked_out_ff(checkout, self.old, target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.sha(checkout), target)
        self.assertEqual(self.sha(self.repo), self.old)
        self.assertEqual(self.git(self.repo, "symbolic-ref", "HEAD").stdout.strip(), "refs/heads/feature/topic")
        self.assertEqual((self.repo / "seed").read_text(), "user edit\n")
        self.assertEqual(self.git(self.repo, "ls-files", "--stage", "-z").stdout, before_index)

    def test_dirty_and_staged_target_are_preserved(self) -> None:
        target = self.fetch_target()
        (self.repo / "seed").write_text("local changes\n", encoding="utf-8")
        for staged in (False, True):
            with self.subTest(staged=staged):
                if staged:
                    self.git(self.repo, "add", "seed")
                index = self.git(self.repo, "ls-files", "--stage", "-z").stdout
                result = self.checked_out_ff(self.repo, self.old, target)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.sha(self.repo), self.old)
                self.assertEqual((self.repo / "seed").read_text(), "local changes\n")
                self.assertEqual(self.git(self.repo, "ls-files", "--stage", "-z").stdout, index)

    def test_divergence_and_local_ahead_do_not_reset_local_commits(self) -> None:
        target = self.fetch_target()
        self.commit(self.repo, "local", "local commit\n")
        local = self.sha(self.repo)
        result = self.checked_out_ff(self.repo, local, target)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.sha(self.repo), local)
        # A local-ahead ref is likewise not a fast-forward to its older ancestor.
        result = self.checked_out_ff(self.repo, local, self.old)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.sha(self.repo), local)

    def test_untracked_and_ignored_collisions_are_not_overwritten(self) -> None:
        target = self.fetch_target()
        collision = self.repo / "accepted"
        collision.write_text("user data\n", encoding="utf-8")
        for ignored in (False, True):
            with self.subTest(ignored=ignored):
                if ignored:
                    (self.repo / ".git/info/exclude").write_text("accepted\n", encoding="utf-8")
                result = self.checked_out_ff(self.repo, self.old, target)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.sha(self.repo), self.old)
                self.assertEqual(collision.read_text(), "user data\n")

    def test_ignored_directory_collision_preserves_nested_user_data(self) -> None:
        target = self.fetch_target()
        (self.repo / "accepted").mkdir()
        retained = self.repo / "accepted/user-data"
        retained.write_text("keep nested data\n", encoding="utf-8")
        (self.repo / ".git/info/exclude").write_text("accepted/\n", encoding="utf-8")
        result = self.checked_out_ff(self.repo, self.old, target)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.sha(self.repo), self.old)
        self.assertEqual(retained.read_text(), "keep nested data\n")

    def test_unoccupied_ref_ff_create_and_stale_cas_leave_current_head_untouched(self) -> None:
        self.git(self.repo, "switch", "-qc", "feature/topic")
        target = self.fetch_target()
        self.git(self.repo, "merge-base", "--is-ancestor", self.old, target)
        self.git(self.repo, "update-ref", "--no-deref", self.ref, target, self.old)
        stale = self.git(self.repo, "update-ref", "--no-deref", self.ref, self.old, self.old, check=False)
        self.assertNotEqual(stale.returncode, 0)
        self.assertEqual(self.sha(self.repo, self.ref), target)
        self.assertEqual(self.sha(self.repo), self.old)
        self.git(self.repo, "update-ref", "--no-deref", "-d", self.ref, target)
        self.git(self.repo, "update-ref", "--stdin", input_text=f"option no-deref\ncreate {self.ref} {target}\n")
        duplicate = self.git(self.repo, "update-ref", "--stdin", check=False,
                             input_text=f"option no-deref\ncreate {self.ref} {self.old}\n")
        self.assertNotEqual(duplicate.returncode, 0)
        self.assertEqual(self.sha(self.repo, self.ref), target)
        self.assertEqual(self.sha(self.repo), self.old)
        self.assertEqual(self.git(self.repo, "symbolic-ref", "HEAD").stdout.strip(), "refs/heads/feature/topic")

    def test_failed_fetch_or_missing_merge_ancestry_cannot_use_a_stale_snapshot(self) -> None:
        failed = self.git(self.repo, "fetch", "--no-tags", str(self.root / "absent.git"), self.ref, check=False)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(self.sha(self.repo), self.old)
        self.assertEqual(self.sha(self.repo, self.tracking), self.old)
        self.fetch_target()
        omitted_merge = self.git(self.repo, "merge-base", "--is-ancestor", self.merged, self.old, check=False)
        self.assertNotEqual(omitted_merge.returncode, 0)
        self.assertEqual(self.sha(self.repo), self.old)

    def test_live_remote_advance_is_detected_after_local_ff(self) -> None:
        target = self.fetch_target()
        result = self.checked_out_ff(self.repo, self.old, target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.commit(self.producer, "later", "later remote change\n")
        self.git(self.producer, "push", "-q", "pr-target", f"HEAD:{self.ref}")
        live = self.git(self.repo, "ls-remote", "--heads", "pr-target", self.ref).stdout.split()[0]
        self.assertNotEqual(self.sha(self.repo, self.ref), live)
        self.assertEqual(self.sha(self.repo), target, "Keep the completed FF; do not claim final equality or reset")

    def test_occupied_review_destination_retains_detached_recovery_commit(self) -> None:
        checkout = self.root / "pr-review/7"
        self.git(self.repo, "worktree", "add", "-q", "--detach", str(checkout), self.old)
        self.commit(checkout, "recovery", "prior session\n")
        retained = self.sha(checkout)
        attempt = self.git(self.repo, "worktree", "add", "--detach", str(checkout), self.old, check=False)
        self.assertNotEqual(attempt.returncode, 0)
        self.assertEqual(self.sha(checkout), retained)
        self.assertEqual((checkout / "recovery").read_text(), "prior session\n")
        self.assertEqual(self.sha(self.repo), self.old)


if __name__ == "__main__":
    unittest.main()
