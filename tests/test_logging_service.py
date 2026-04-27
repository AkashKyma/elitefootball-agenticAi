import logging
import os
import tempfile
import unittest

from app.services import logging_service


class TestLoggingService(unittest.TestCase):
    def tearDown(self):
        root = logging.getLogger()
        for handler in list(root.handlers):
            root.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass
        logging_service._CONFIGURED = False

    def test_log_event_formats_key_values(self):
        logging_service.configure_logging(force=True)
        logger = logging_service.get_logger("test.logging")
        with self.assertLogs("test.logging", level="INFO") as captured:
            logging_service.log_event(logger, logging.INFO, "scrape.start", source="transfermarkt", headless=True)
        self.assertIn("scrape.start", captured.output[0])

    def test_file_logging_writes_when_enabled(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "scrape.log")
            previous_enabled = logging_service.settings.log_file_enabled
            previous_path = logging_service.settings.log_file_path
            previous_level = logging_service.settings.log_level
            object.__setattr__(logging_service.settings, "log_file_enabled", True)
            object.__setattr__(logging_service.settings, "log_file_path", log_path)
            object.__setattr__(logging_service.settings, "log_level", "INFO")
            try:
                logging_service.configure_logging(force=True)
                logger = logging_service.get_logger("test.file")
                logging_service.log_event(logger, logging.INFO, "storage.write_raw.success", path=log_path)
                for handler in logging.getLogger().handlers:
                    handler.flush()
                with open(log_path, encoding="utf-8") as handle:
                    content = handle.read()
                self.assertIn("storage.write_raw.success", content)
            finally:
                object.__setattr__(logging_service.settings, "log_file_enabled", previous_enabled)
                object.__setattr__(logging_service.settings, "log_file_path", previous_path)
                object.__setattr__(logging_service.settings, "log_level", previous_level)
