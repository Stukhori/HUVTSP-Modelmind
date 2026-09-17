import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"


class ModelMindUIContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = (TEMPLATES / "base.html").read_text(encoding="utf-8")
        cls.index = (TEMPLATES / "index.html").read_text(encoding="utf-8")
        cls.result = (TEMPLATES / "result.html").read_text(encoding="utf-8")
        cls.multi = (TEMPLATES / "result_multi.html").read_text(encoding="utf-8")
        cls.css = (STATIC / "style.css").read_text(encoding="utf-8")
        cls.js = (STATIC / "app.js").read_text(encoding="utf-8")
        cls.app = (ROOT / "app.py").read_text(encoding="utf-8")

    def test_all_pages_use_shared_application_shell(self):
        for template in (self.index, self.result, self.multi):
            self.assertIn('{% extends "base.html" %}', template)
        self.assertIn('class="site-header"', self.base)
        self.assertIn('id="main-content"', self.base)

    def test_templates_do_not_depend_on_remote_ui_assets(self):
        combined = "\n".join((self.base, self.index, self.result, self.multi))
        self.assertNotRegex(combined, r"fonts\.googleapis\.com|cdnjs\.cloudflare\.com")

    def test_home_keeps_required_upload_contract(self):
        self.assertIn('action="{{ url_for(\'upload_file\') }}"', self.index)
        self.assertRegex(self.index, r'name="excel_file"[^>]+required')
        self.assertRegex(self.index, r'name="user_question"[^>]+required')
        self.assertIn('accept=".xls,.xlsx"', self.index)

    def test_fake_navigation_and_history_are_removed(self):
        self.assertNotIn('class="sidebar"', self.index)
        self.assertNotIn("Sales Data Analysis", self.index)
        self.assertNotIn("Premium", self.index)
        self.assertNotIn("Sign Up", self.index)

    def test_result_routes_remain_reachable(self):
        combined = "\n".join((self.result, self.multi))
        self.assertIn("url_for('ask_another')", combined)
        self.assertIn("url_for('switch_sheet')", combined)
        self.assertIn("url_for('home')", combined)

    def test_multi_sheet_tabs_are_keyboard_accessible(self):
        self.assertIn('role="tablist"', self.multi)
        self.assertIn('role="tab"', self.multi)
        self.assertIn('role="tabpanel"', self.multi)
        for key in ("ArrowLeft", "ArrowRight", "Home", "End"):
            self.assertIn(key, self.js)

    def test_layout_has_wide_and_responsive_contracts(self):
        self.assertIn("width: min(92%, 1440px)", self.css)
        for breakpoint in ("960px", "720px", "640px", "480px"):
            self.assertIn(f"max-width: {breakpoint}", self.css)
        self.assertIn("overflow: auto", self.css)

    def test_interactive_states_have_explicit_focus_and_selection(self):
        self.assertIn(":focus-visible", self.css)
        self.assertIn(".sheet-tab.is-active", self.css)
        self.assertIn(".sheet-button.is-current", self.css)
        self.assertIn(".drop-zone.is-dragging", self.css)

    def test_diagnostics_are_forwarded_to_result_views(self):
        self.assertGreaterEqual(len(re.findall(r"error_report=", self.app)), 6)
        self.assertGreaterEqual(len(re.findall(r"trend_summary=", self.app)), 6)


if __name__ == "__main__":
    unittest.main()
