"""Smoke tests for check_new.py core functions.

Run: python3 -m unittest tests.test_check_new
"""

import os
import sys
import tempfile
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

_tmpdir = tempfile.mkdtemp()
os.environ["DATA_DIR"] = _tmpdir

import check_new


class TestIsRelevant(unittest.TestCase):
    def test_webflow_is_relevant(self):
        self.assertTrue(check_new.is_relevant("Webflow Developer"))

    def test_shopify_is_relevant(self):
        self.assertTrue(check_new.is_relevant("Shopify Developer"))

    def test_nocode_is_relevant(self):
        self.assertTrue(check_new.is_relevant("No-code Developer"))

    def test_empty_title_not_relevant(self):
        self.assertFalse(check_new.is_relevant(""))

    def test_unrelated_title_not_relevant(self):
        self.assertFalse(check_new.is_relevant("Restaurant Manager"))

    def test_react_developer_excluded(self):
        self.assertFalse(check_new.is_relevant("React Developer"))

    def test_python_developer_excluded(self):
        self.assertFalse(check_new.is_relevant("Python Developer"))

    def test_backend_excluded(self):
        self.assertFalse(check_new.is_relevant("Backend Engineer"))


class TestGetExistingUrls(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.md_path = os.path.join(self.tmpdir, "vacancies.md")
        self._orig = check_new.MD_FILE
        check_new.MD_FILE = self.md_path

    def tearDown(self):
        check_new.MD_FILE = self._orig
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_missing_file_returns_empty_set(self):
        self.assertEqual(check_new.get_existing_urls(), set())

    def test_extracts_urls_from_md(self):
        with open(self.md_path, "w", encoding="utf-8") as f:
            f.write("- [A](https://djinni.co/jobs/1)\n- [B](https://jobs.dou.ua/vacancies/2/)\n")
        urls = check_new.get_existing_urls()
        self.assertIn("https://djinni.co/jobs/1", urls)
        self.assertIn("https://jobs.dou.ua/vacancies/2/", urls)


class TestAddVacancyToMd(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.md_path = os.path.join(self.tmpdir, "vacancies.md")
        self._orig = check_new.MD_FILE
        check_new.MD_FILE = self.md_path
        with open(self.md_path, "w", encoding="utf-8") as f:
            f.write("## Djinni.co\n\n## DOU.ua\n\n")

    def tearDown(self):
        check_new.MD_FILE = self._orig
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_adds_new_vacancy(self):
        check_new.add_vacancy_to_md("Djinni.co", "Webflow Dev", "https://djinni.co/jobs/999")
        with open(self.md_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("[Webflow Dev](https://djinni.co/jobs/999)", content)

    def test_skips_duplicate_url(self):
        check_new.add_vacancy_to_md("Djinni.co", "Dev One", "https://djinni.co/jobs/1")
        check_new.add_vacancy_to_md("Djinni.co", "Dev Duplicate", "https://djinni.co/jobs/1")
        with open(self.md_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content.count("https://djinni.co/jobs/1"), 1)
        self.assertNotIn("Dev Duplicate", content)


if __name__ == "__main__":
    unittest.main()
