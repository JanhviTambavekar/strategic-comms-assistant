import unittest

from src.llm_client import _message_content_text
from src.output_formatter import add_title


class NvidiaResponseHandlingTests(unittest.TestCase):
    def test_none_content_is_normalised_to_empty_text(self):
        self.assertEqual(_message_content_text({"content": None}), "")

    def test_content_parts_are_joined(self):
        message = {"content": [{"type": "text", "text": "Part one"}, {"text": "Part two"}]}
        self.assertEqual(_message_content_text(message), "Part one\nPart two")

    def test_formatter_does_not_crash_on_missing_strategy(self):
        report = add_title(None, "Research Project", "Example")
        self.assertIn("Example", report)


if __name__ == "__main__":
    unittest.main()
