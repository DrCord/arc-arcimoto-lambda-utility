import logging
import unittest

from arcimoto_lambda_utility.command.command import AbstractCommand
from tests.command_args import CommandArgs


class TestCommandRun(unittest.TestCase):

    AbstractCommandObject = None

    @classmethod
    def setUpClass(cls):
        cls.AbstractCommandObject = AbstractCommand(None)

    # test successes
    def test_run_success(self):
        args = CommandArgs()
        args.verbose = True
        self.AbstractCommandObject.run(args)
        self.assertEqual(self.AbstractCommandObject.logger.level, logging.DEBUG)
