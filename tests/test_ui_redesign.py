"""Unit tests verifying UI/UX Redesign for Claim Details Modal and Cross-Source Comparison Dashboard."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = REPO_ROOT / "frontend"


class TestUIUXRedesign(unittest.TestCase):
    """Test suite ensuring frontend layout, tables, badges, and responsive attributes comply with redesign requirements."""

    def setUp(self):
        self.html_content = (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")
        self.css_content = (FRONTEND_DIR / "style.css").read_text(encoding="utf-8")
        self.js_content = (FRONTEND_DIR / "app.js").read_text(encoding="utf-8")

    def test_modal_container_and_id_badge(self):
        """Ensure modal has enlarged container class and styled claim ID badge."""
        self.assertIn("modal-claim-details-card", self.html_content)
        self.assertIn("claim-id-badge", self.html_content)
        self.assertIn("modal-details-id", self.html_content)

        # CSS verification
        self.assertIn("95vw", self.css_content)
        self.assertIn("1500px", self.css_content)

    def test_summary_cards_grid(self):
        """Ensure the 5 summary metric cards exist with proper IDs and grid styling."""
        required_metric_ids = [
            "verif-metric-status",
            "verif-metric-score",
            "verif-metric-matched",
            "verif-metric-mismatched",
            "verif-metric-missing",
        ]
        for metric_id in required_metric_ids:
            with self.subTest(metric_id=metric_id):
                self.assertIn(f'id="{metric_id}"', self.html_content)

        self.assertIn("verif-summary-cards-grid", self.html_content)
        self.assertIn("verif-summary-card", self.html_content)

        # CSS grid rules
        self.assertIn("grid-template-columns: repeat(5, minmax(0, 1fr))", self.css_content)

    def test_findings_table_structure_and_colgroup(self):
        """Ensure findings table uses semantic table, colgroup with exact percentages, and 7 required columns."""
        self.assertIn("findings-table", self.html_content)
        self.assertIn('<table class="data-table findings-table"', self.html_content)
        self.assertIn("<colgroup>", self.html_content)

        # Approximate/Exact widths: 17%, 14%, 14%, 14%, 11%, 8%, 22%
        expected_widths = ["17%", "14%", "14%", "14%", "11%", "8%", "22%"]
        col_matches = re.findall(r'<col style="width:\s*([^;"]+);?"', self.html_content)
        self.assertEqual(len(col_matches), 7)
        self.assertEqual(col_matches, expected_widths)

        # Header titles
        expected_headers = [
            "Comparison",
            "Field",
            "Source A Value",
            "Source B Value",
            "Status",
            "Severity",
            "Explanation",
        ]
        for header in expected_headers:
            with self.subTest(header=header):
                self.assertIn(f">{header}</th>", self.html_content)

    def test_no_unwanted_text_wrapping_rules(self):
        """Ensure word-break: break-all and bad text-wrapping rules are neutralized for tokens & badges."""
        self.assertIn(".val-token", self.css_content)
        self.assertIn("white-space: nowrap", self.css_content)
        self.assertIn("hyphens: none", self.css_content)

        # Check badge classes
        status_classes = [
            "badge-status-match",
            "badge-status-mismatch",
            "badge-status-missing",
            "badge-status-inconclusive",
            "badge-status-na",
        ]
        for sc in status_classes:
            with self.subTest(status_class=sc):
                self.assertIn(sc, self.css_content)

        severity_classes = [
            "badge-sev-low",
            "badge-sev-medium",
            "badge-sev-high",
            "badge-sev-critical",
        ]
        for sc in severity_classes:
            with self.subTest(severity_class=sc):
                self.assertIn(sc, self.css_content)

    def test_js_row_generation(self):
        """Ensure app.js generates structured tokens, badges, and cell containers."""
        self.assertIn("cmp-container", self.js_content)
        self.assertIn("field-title", self.js_content)
        self.assertIn("val-token", self.js_content)
        self.assertIn("status-badge", self.js_content)
        self.assertIn("severity-badge", self.js_content)
        self.assertIn("expl-text", self.js_content)

    def test_footer_download_buttons_preserved(self):
        """Ensure Download Receipt and Download Report buttons are retained with proper targets."""
        self.assertIn('id="btn-modal-receipt"', self.html_content)
        self.assertIn('id="btn-modal-report"', self.html_content)
        self.assertIn('id="btn-modal-close"', self.html_content)


if __name__ == "__main__":
    unittest.main()
