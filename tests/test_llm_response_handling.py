import unittest
from unittest.mock import patch

from src.llm_client import _message_content_text, available_free_models, nvidia_api_keys
from src.output_formatter import add_title


class NvidiaResponseHandlingTests(unittest.TestCase):
    def test_free_model_pool_only_includes_configured_services(self):
        values = {
            "GROQ_API_KEY": "key",
            "GROQ_MODEL": "fast-model",
            "OPENROUTER_API_KEY": "",
        }
        with patch.dict("os.environ", values, clear=True):
            self.assertEqual(available_free_models(), {
                "Groq · fast-model": "groq::fast-model"
            })

    def test_nvidia_keys_support_three_numbered_keys_and_bearer_prefix(self):
        values = {
            "NVIDIA_API_KEY_1": "first",
            "NVIDIA_API_KEY_2": "Bearer second",
            "NVIDIA_API_KEY_3": "first",
            "OPENAI_API_KEY": "fallback",
        }
        with patch.dict("os.environ", values, clear=True):
            self.assertEqual(nvidia_api_keys("nvidia/nemotron-3.5-lightning-30b-a3b"), [
                "first", "second", "fallback"
            ])

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
