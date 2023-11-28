import logging
import unittest

from arcimoto_lambda_utility.command.command import AbstractCommand


class TestCommandInit(unittest.TestCase):

    AbstractCommandObject = None

    @classmethod
    def setUpClass(cls):
        cls.AbstractCommandObject = AbstractCommand(None)

    # test successes
    def test_init_success(self):
        self.assertEqual(self.AbstractCommandObject.logger.level, logging.INFO)


if __name__ == '__main__':
    unittest.main()
