"""Focused semantic contract checks for lifecycle design and smell guidance.

All upstream overlap/license inputs are the persisted WP1 offline oracle. This
module performs no network or machine-local cache access.
"""

from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PLUGIN_ROOT.parents[1]
SHARED = PLUGIN_ROOT / "references/clean-code-rules.md"

GUARDED_PASSAGES = (
    ("506af72b38cbbacb716ebfb2de4e706cdb78fcdfde112dc4d4bb6e92495d0ae0", "Depth is a property of the interface, not the implementation."),
    ("943db8639a9661e11f6ee91451f55380e8d15b79002094043edf25d55240a140", "Imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep."),
    ("a021841b2a4db505b3ad4beb9444b18f36cac0d1c2f018ec875e4cc0faae7b08", "The interface is the test surface. Callers and tests cross the same seam."),
    ("080f19e78685da39aff365e6fda622e40dfa6ff7529b2366496b4c84c3d278c6", "One adapter means a hypothetical seam. Two adapters means a real one."),
    ("699d17242fb3a7b96f9b52f7afb0fd771896f38342f318bb0b42c4ee6b69da6b", "Accept dependencies, don't create them."),
    ("06b9d04a72b06f1bd2f5235482bc636f029af9e7771744e060d0487f5fa9bfbe", "Return results, don't produce side effects."),
    ("c5a37831b165e38d061232d04d0fabe28eb011aaea44fbab32e21e7f0652f018", "a function, variable, or type whose name doesn't reveal what it does or holds."),
    ("ddbfeeae1c4ea480fe27452e2b49b8e57b8c5aeb06abb4772abeb7a53d283d17", "the same logic shape appears in more than one hunk or file in the change."),
    ("0954d020ea8b7451e98aa5fef2c5d5ac20ba1394b539d13f17c9b512d1f7058b", "one logical change forces scattered edits across many files in the diff."),
    ("bf676e7cfddb78dce3fa3997eb6c7737b872e05a05481ada15fa9015059ea9d4", "abstraction, parameters, or hooks added for needs the spec doesn't have."),
)

MIT_PAYLOAD = """MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
MIT_SHA256 = "0e7ac423bf2c6e223b7c5b156f8cf72da49d748e56a1641402c31f22ad07dbb5"

SMELL_ANCHORS = {
    "Mysterious Name": (("name", "domain meaning"), ("rename", "intent")),
    "Duplicated Code": (("logic", "changed locations"), ("centralize", "drift")),
    "Feature Envy": (("another owner's data",), ("owning Module", "Locality")),
    "Data Clumps": (("fields", "parameters", "together"), ("cohesive type", "invariant")),
    "Primitive Obsession": (("primitive", "domain meaning", "invalid states"), ("domain type", "misuse")),
    "Repeated Switches": (("dispatch", "recurs"), ("centralize", "material risk")),
    "Shotgun Surgery": (("logical change", "many locations"), ("Module", "Seam", "local")),
    "Divergent Change": (("unrelated reasons",), ("responsibilities", "change cost")),
    "Speculative Generality": (("hooks", "accepted requirement"), ("delete", "inline")),
    "Message Chains": (("internal structure",), ("Interface operation", "coupling")),
    "Middle Man": (("delegates", "Leverage"), ("deletion test", "real Seam")),
    "Refused Bequest": (("inherited behavior",), ("composition", "smaller", "Interface")),
}

CONSUMERS = {
    "conceptualize": "skills/conceptualize/SKILL.md",
    "planner": "skills/implementation-plan/SKILL.md",
    "preflight": "skills/implementation-plan/references/design-preflight.md",
    "plan-review": "skills/review-plan/references/plan-review-rubrics.md",
    "package": "skills/implement/references/package-agent-contract.md",
    "repair": "skills/implement/references/repair-agent-contract.md",
    "fix-implementer": "skills/review-code/references/fix-implementer-contract.md",
}


class LifecycleDesignGuidanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.shared = SHARED.read_text(encoding="utf-8")

    def assert_groups(self, text: str, groups: tuple[tuple[str, ...], ...], label: str) -> None:
        for group in groups:
            self.assertTrue(all(term in text for term in group), f"{label}: missing semantic group {group}")

    def test_complete_core_model_and_semantic_anchors(self) -> None:
        required = {
            "Module", "Interface", "Implementation", "Depth", "deep module", "shallow module",
            "Seam", "Adapter", "Leverage", "Locality", "deletion test",
        }
        self.assertEqual({term for term in required if term not in self.shared}, set())
        groups = (
            ("function", "class", "package", "tier-spanning", "scale-agnostic"),
            ("invariants", "ordering", "error modes", "configuration", "performance characteristics"),
            ("Adapter", "role", "not a synonym for Implementation"),
            ("Depth", "Interface", "Leverage", "not implementation size"),
            ("Leverage", "capability", "unit of Interface learned"),
            ("Locality", "change", "defects", "knowledge", "verification"),
            ("external", "internal", "Seams"),
            ("Vanishing complexity", "pass-through", "redistributed", "callers"),
            ("Interface", "test surface", "callers", "tests", "same Seam"),
            ("One Adapter", "hypothetical", "two independent Adapters", "real Seam"),
            ("accept volatile dependencies", "return observable results", "Interfaces small"),
            ("fewer methods", "simpler parameters", "hidden incidental complexity"),
        )
        self.assert_groups(self.shared, groups, "core model")
        self.assertIn("Slice **Interface contract**", self.shared)
        self.assertIn("not necessarily a Module Interface", self.shared)
        self.assert_groups(self.shared, (("without exposing internals", "for tests"),), "test-only Interface")

    def test_all_smells_have_detection_and_calibrated_response(self) -> None:
        names = list(SMELL_ANCHORS)
        for index, (name, groups) in enumerate(SMELL_ANCHORS.items()):
            start = self.shared.index(f"**{name}:**")
            end = self.shared.find("\n- **", start + 5)
            section = self.shared[start : end if end >= 0 else len(self.shared)]
            self.assert_groups(section, groups, name)
        self.assertEqual(self.shared.count("\n- **") >= len(names), True)
        calibration = (
            ("MUST be considered", "not automatically a defect"),
            ("repository or requirement evidence", "material in-scope risk"),
            ("unrelated", "brownfield cleanup", "Right-sized complexity"),
        )
        self.assert_groups(self.shared, calibration, "calibration")

    def test_delegated_workers_receive_and_read_shared_owner(self) -> None:
        preflight = (PLUGIN_ROOT / CONSUMERS["preflight"]).read_text(encoding="utf-8")
        assignment = preflight.split("## Challenger Assignment", 1)[1].split("## Bounded Output", 1)[0]
        self.assert_groups(
            assignment,
            (
                ("Shared clean-code contract", "${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md"),
                ("Read and apply", "complete shared", "Module", "Interface", "Seam", "Adapter"),
                ("Depth", "Leverage", "Locality", "every smell", "evidence-calibrated"),
                ("planner", "persist"),
            ),
            "Challenger Assignment routing",
        )

        fix = (PLUGIN_ROOT / CONSUMERS["fix-implementer"]).read_text(encoding="utf-8")
        required_packet = fix.split("## Required Packet", 1)[1].split("## Write and Side-Effect Boundary", 1)[0]
        ordered_workflow = fix.split("## Ordered Workflow", 1)[1].split("## Pipeline Freshness Handback", 1)[0]
        self.assert_groups(
            required_packet,
            (("shared clean-code contract path", "${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md"),),
            "Fix Implementer Required Packet routing",
        )
        self.assert_groups(
            ordered_workflow.lower(),
            (("before any repair", "read and apply", "supplied shared clean-code contract", "self-review"),),
            "Fix Implementer Ordered Workflow routing",
        )

    def test_stage_owned_routes_use_shared_owner(self) -> None:
        route_terms = {
            "conceptualize": ("material Module/Interface", "Seam", "deletion-test", "Skip this ceremony"),
            "planner": ("complete shared Module/Interface/Seam model", "all smell heuristics", "only material"),
            "preflight": ("shallow/pass-through Modules", "wide/leaky Interfaces", "hypothetical Seams", "tests reaching past the Interface"),
            "plan-review": ("complete shared Module/Interface/Seam model", "all smell heuristics", "deep/local/testable"),
            "package": ("complete shared", "all smell heuristics", "before handoff"),
            "repair": ("complete shared codebase-design model", "all smell heuristics", "directly affected Interfaces"),
            "fix-implementer": ("complete shared codebase-design model", "every smell", "directly affected Interfaces"),
        }
        for role, relative in CONSUMERS.items():
            text = (PLUGIN_ROOT / relative).read_text(encoding="utf-8")
            self.assertTrue(all(term in text for term in route_terms[role]), f"missing {role} route")
        for relative in CONSUMERS.values():
            text = (PLUGIN_ROOT / relative).read_text(encoding="utf-8")
            self.assertFalse(all(name in text for name in SMELL_ANCHORS), f"duplicated smell glossary in {relative}")

    def test_aggregate_handoff_grammar_and_scope(self) -> None:
        grammar = "design_and_smell_review: complete; material_findings=none|fixed:<items>; justified_non_actions=none|<evidence>"
        not_applicable = "design_and_smell_review: not_applicable; reason=<concrete reason>"
        for role in ("package", "repair", "fix-implementer"):
            text = (PLUGIN_ROOT / CONSUMERS[role]).read_text(encoding="utf-8")
            self.assertEqual(text.count(grammar), 1, f"{role}: aggregate grammar must occur once")
            self.assertEqual(text.count(not_applicable), 1, f"{role}: mechanical alternative must occur once")
            self.assertIn("unresolved_concerns", text)
        scope_terms = (
            "changed behavior", "directly affected Interfaces", "Seams", "Adapters", "callers", "tests",
            "evidence", "unrelated", "per-smell evidence rows", "test-only variation",
        )
        self.assertTrue(all(term in self.shared for term in scope_terms))

    def test_review_verifier_and_audit_authority_stays_finite(self) -> None:
        review = (PLUGIN_ROOT / "skills/review-code/SKILL.md").read_text(encoding="utf-8")
        verifier = (PLUGIN_ROOT / "skills/implement/references/package-verification.md").read_text(encoding="utf-8")
        audit = (PLUGIN_ROOT / "skills/audit/SKILL.md").read_text(encoding="utf-8")
        audit_worker = (PLUGIN_ROOT / "skills/audit/references/audit-subagent-contract.md").read_text(encoding="utf-8")
        self.assertTrue(all(x in review for x in ("two tiers", "BLOCKING", "ADVISORY", "Skeptic", "Fix Verification", "integration-first", "clean-code-rules.md")))
        self.assertTrue(all(x in verifier for x in ("closed and frozen", "Acceptance Checklist", "blocking", "advisory")))
        self.assertTrue(all(x in audit for x in ("finite", "SPEC `## Acceptance`", "read-only", "package-local verification")))
        self.assertTrue(all(x in audit_worker for x in ("Final audit is a completeness reconciler", "not a full second package verifier")))
        self.assertFalse((PLUGIN_ROOT / "skills/codebase-design").exists())

    def test_pinned_attribution_and_offline_notice_guard(self) -> None:
        expected_urls = (
            "https://raw.githubusercontent.com/mattpocock/skills/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/engineering/codebase-design/SKILL.md",
            "https://raw.githubusercontent.com/mattpocock/skills/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/engineering/code-review/SKILL.md",
            "https://raw.githubusercontent.com/mattpocock/skills/84fdeffd12f2ee307994d1eb6feb48173b6e0502/LICENSE",
        )
        self.assertIn("Matt Pocock's skills repository", self.shared)
        self.assertIn("MIT licensed", self.shared)
        self.assertTrue(all(url in self.shared for url in expected_urls))

        matches = []
        for expected_digest, literal in GUARDED_PASSAGES:
            raw = literal.encode("utf-8")
            self.assertEqual(hashlib.sha256(raw).hexdigest(), expected_digest)
            normalized = literal.strip(" \t\r\n")
            if normalized in self.shared:  # deliberately case/punctuation/internal-whitespace sensitive
                matches.append(normalized)

        payload = MIT_PAYLOAD.encode("utf-8")
        self.assertEqual(len(payload), 1068)
        self.assertTrue(MIT_PAYLOAD.endswith("\n"))
        self.assertFalse(MIT_PAYLOAD.endswith("\n\n"))
        self.assertEqual(hashlib.sha256(payload).hexdigest(), MIT_SHA256)
        notice = REPO_ROOT / "THIRD_PARTY_NOTICES.md"
        if not matches:
            self.assertFalse(notice.exists(), "notice must be absent when no guarded passage is retained")
        else:
            self.assertTrue(notice.is_file(), "retained guarded passage requires the canonical MIT notice")
            notice_text = notice.read_text(encoding="utf-8")
            self.assertIn(MIT_PAYLOAD, notice_text)
            block_start = notice_text.index(MIT_PAYLOAD)
            block = notice_text[block_start : block_start + len(MIT_PAYLOAD)]
            self.assertEqual(hashlib.sha256(block.encode("utf-8")).hexdigest(), MIT_SHA256)

    def test_readme_inventory_and_no_full_sentence_snapshot_style(self) -> None:
        readme = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("test_lifecycle_design_guidance.py", readme)
        source = Path(__file__).read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"MD_LINE_CAP\s*=", source))


if __name__ == "__main__":
    unittest.main()
