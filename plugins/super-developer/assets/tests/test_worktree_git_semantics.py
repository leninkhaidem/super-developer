"""Git command-semantics checks for the worktree/probe envelope.

These are behavioral: each test drives real git in a throwaway repository and
asserts the *observable* outcome of the command recipes the prompts prescribe
(ref creation/teardown ordering, --no-track isolation, portable index digests,
moved-base rejection). They stay valid across any rewording of the prompts.

Prompt wording itself is deliberately untested here; see test_skill_prompts.py
for the content-agnostic structural checks.
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


if __name__ == "__main__":
    unittest.main()
