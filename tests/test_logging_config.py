import logging
import os
import tempfile
import unittest

from logging_config import setup_logger

import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)


class TestLoggingConfig(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()

        self.logger = logging.getLogger("FALCON")

        # Remove handlers left over from other tests.
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)

        self.logger.setLevel(logging.NOTSET)

        self.logger = setup_logger(self.temp_directory.name)

    def tearDown(self):
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)

        self.logger.setLevel(logging.NOTSET)
        self.temp_directory.cleanup()

    def test_creates_log_directory_and_file(self):
        log_file = os.path.join(
            self.temp_directory.name,
            "logs",
            "falcon.log"
        )

        self.logger.info("Test log entry")

        for handler in self.logger.handlers:
            handler.flush()

        self.assertTrue(os.path.isdir(os.path.dirname(log_file)))
        self.assertTrue(os.path.isfile(log_file))

    def test_writes_messages_to_log_file(self):
        self.logger.info("FALCON test event")

        for handler in self.logger.handlers:
            handler.flush()

        log_file = os.path.join(
            self.temp_directory.name,
            "logs",
            "falcon.log"
        )

        with open(log_file, "r", encoding="utf-8") as file:
            content = file.read()

        self.assertIn("INFO", content)
        self.assertIn("FALCON test event", content)

    def test_setup_does_not_duplicate_handlers(self):
        original_handler_count = len(self.logger.handlers)

        same_logger = setup_logger(self.temp_directory.name)

        self.assertIs(same_logger, self.logger)
        self.assertEqual(
            len(same_logger.handlers),
            original_handler_count
        )


if __name__ == "__main__":
    unittest.main()
