"""Unit tests verifying UI/UX Redesign for Claim Details Modal and Cross-Source Comparison Dashboard."""

from html.parser import HTMLParser
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = REPO_ROOT / "frontend"


class FindingsTableParser(HTMLParser):
    """Robust HTML parser to inspect the cross-source findings table structure and colgroup."""

    def __init__(self):
        super().__init__()
        self.in_findings_table = False
        self.in_colgroup = False
        self.table_attrs = {}
        self.cols = []
        self.headers = []
        self.current_tag = None
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "table" and attr_dict.get("id") == "table-cross-source-findings":
            self.in_findings_table = True
            self.table_attrs = attr_dict
        elif self.in_findings_table:
            if tag == "colgroup":
                self.in_colgroup = True
            elif tag == "col" and self.in_colgroup:
                self.cols.append(attr_dict)
            elif tag == "th":
                self.current_tag = "th"
                self.current_text = []

    def handle_endtag(self, tag):
        if self.in_findings_table:
            if tag == "colgroup":
                self.in_colgroup = False
            elif tag == "th":
                self.headers.append("".join(self.current_text).strip())
                self.current_tag = None
            elif tag == "table":
                self.in_findings_table = False

    def handle_data(self, data):
        if self.current_tag == "th":
            self.current_text.append(data)


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
        """Ensure findings table uses semantic table, colgroup with valid percentage widths summing to 100%, and 7 required columns."""
        parser = FindingsTableParser()
        parser.feed(self.html_content)

        # 1. Findings table existence and classes
        self.assertTrue(parser.table_attrs, "Findings table with id 'table-cross-source-findings' was not found.")
        table_classes = parser.table_attrs.get("class", "").split()
        self.assertIn("findings-table", table_classes, "Findings table missing 'findings-table' class.")
        self.assertIn("data-table", table_classes, "Findings table missing 'data-table' class.")

        # 2. Colgroup and column count
        self.assertEqual(len(parser.cols), 7, f"Expected 7 <col> definitions in findings table colgroup, found {len(parser.cols)}.")

        # 3. Semantic column classes
        expected_col_classes = [
            "col-cmp",
            "col-field",
            "col-src-a",
            "col-src-b",
            "col-status",
            "col-severity",
            "col-explanation",
        ]
        actual_col_classes = [col.get("class", "") for col in parser.cols]
        self.assertEqual(actual_col_classes, expected_col_classes, "Colgroup column classes do not match expected semantic sequence.")

        # 4. Valid width definitions and percentage check (agnostic of HTML attribute ordering)
        parsed_widths = []
        for i, col in enumerate(parser.cols):
            style = col.get("style", "")
            match = re.search(r"width:\s*(\d+)%", style)
            self.assertIsNotNone(match, f"Column {i} style '{style}' is missing a valid percentage width.")
            parsed_widths.append(int(match.group(1)))

        # Verify width distribution matches active production layout and sums to 100%
        expected_widths = [13, 13, 18, 19, 11, 7, 19]
        self.assertEqual(parsed_widths, expected_widths, f"Column widths {parsed_widths}% do not match expected layout {expected_widths}%.")
        self.assertEqual(sum(parsed_widths), 100, f"Column widths must sum to 100%, got {sum(parsed_widths)}%.")

        # 5. Header titles in semantic thead
        expected_headers = [
            "Comparison",
            "Field",
            "Source A Value",
            "Source B Value",
            "Status",
            "Severity",
            "Explanation",
        ]
        self.assertEqual(parser.headers, expected_headers, "Table headers do not match required sequence and titles.")

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
