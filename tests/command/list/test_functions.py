import argparse
import unittest

from arcimoto_lambda_utility import command

from tests.dependencies import DependenciesConfigFile

from tests.command_args import ListCommandArgs


class TestFunctions(unittest.TestCase):

    args = None
    default_parser_description = 'Unit test created'
    ListCommandObject = None

    @classmethod
    def setUpClass(cls):
        cls.args = ListCommandArgs()
        cls.DependenciesFileObject = DependenciesConfigFile()
        cls.DependenciesFileObject.dependencies_create_file()

    @classmethod
    def tearDownClass(cls):
        cls.DependenciesFileObject.dependencies_remove_file()

    # test successes
    def test_functions_success(self):
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        ListCommandObject = command.list.Command(parser)
        ListCommandObject._parse_arguments(self.args, True)
        ListCommandObject._dependencies_load()

        self.assertIsInstance(ListCommandObject.functions, list)

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
