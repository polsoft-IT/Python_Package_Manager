import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch, Mock

import python_package_manager as ppm


class TestCLIIntegration(unittest.TestCase):
    def test_list_categories(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = ppm.main(["--list-categories"])
        output = buf.getvalue()
        self.assertIn("Kompilatory i Transpilatory", output)
        self.assertEqual(rc, 0)

    def test_list_packages_all(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = ppm.main(["--list-packages"])
        output = buf.getvalue()
        # Expect at least one known package across categories
        self.assertIn("pyinstaller", output)
        self.assertEqual(rc, 0)

    def test_list_packages_by_category(self):
        buf = io.StringIO()
        cat = "GUI (Interfejsy graficzne)"
        with redirect_stdout(buf):
            rc = ppm.main(["--list-packages", cat])
        output = buf.getvalue()
        self.assertIn("wxPython", output)
        self.assertEqual(rc, 0)

    @patch("subprocess.run")
    def test_scan_installed_mocked(self, mock_run):
        # Mock pip list --format=json
        fake = Mock()
        fake.stdout = json.dumps([{"name": "examplepkg", "version": "0.1.0"}])
        fake.returncode = 0
        mock_run.return_value = fake

        buf = io.StringIO()
        with redirect_stdout(buf):
            ppm._cli_scan_installed()
        output = buf.getvalue()
        self.assertIn("examplepkg: 0.1.0", output)


if __name__ == "__main__":
    unittest.main()
