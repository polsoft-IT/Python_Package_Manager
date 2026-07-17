import unittest

import python_package_manager as ppm


class PackageParserTests(unittest.TestCase):
    def test_parse_pip_freeze_output(self):
        output = """requests==2.31.0
pandas==2.2.3
-e git+https://example.com/repo.git#egg=pytest
foo @ file:///tmp/foo
"""

        parsed = ppm.parse_pip_freeze_output(output)

        self.assertEqual(parsed["requests"], "2.31.0")
        self.assertEqual(parsed["pandas"], "2.2.3")
        self.assertEqual(parsed["pytest"], "")
        self.assertEqual(parsed["foo"], "")

    def test_summarize_install_output(self):
        output = "\n".join([f"line {i}" for i in range(12)])

        summarized = ppm.summarize_install_output(output, max_lines=5)

        self.assertIn("line 0", summarized)
        self.assertIn("line 4", summarized)
        self.assertIn("... (7 more lines)", summarized)


if __name__ == "__main__":
    unittest.main()
