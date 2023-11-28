import argparse
import unittest
import uuid

from arcimoto_lambda_utility.command import dependencies

from tests.dependencies import DependenciesConfigFile

from tests.command_args import (
    CommandArgs,
    DEFAULT_TEST_LAMBDA_NAME,
    DEFAULT_TEST_LAMBDA_ROLE_NAME
)


class TestRun(unittest.TestCase):

    args = None
    parser = None
    default_parser_description = 'Unit test created'
    DependenciesCommandObject = None

    @classmethod
    def setUpClass(cls):
        cls.DependenciesFileObject = DependenciesConfigFile()

        cls.args = CommandArgs()
        cls.function_name = cls.args.function
        cls.args.role = DEFAULT_TEST_LAMBDA_ROLE_NAME

    @classmethod
    def tearDownClass(cls):
        cls.DependenciesFileObject.dependencies_remove_file()

    # test successes
    def test_run_success(self):
        # set up
        args = CommandArgs()
        function_name = args.function_name
        self.DependenciesFileObject.dependencies_create_file(function_name)
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        DependenciesCommandObject = dependencies.Command(parser)
        self.args.description = 'test_run_success'
        self.assertIsInstance(DependenciesCommandObject.run(args, True), list)
        self.DependenciesFileObject.dependencies_remove_file()

    # test errors
    def test_run_error_lambda_name_configuration_not_found(self):
        # set up
        args = CommandArgs()
        function_name = args.function_name
        self.DependenciesFileObject.dependencies_create_file(function_name)
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        DependenciesCommandObject = dependencies.Command(parser)
        args.function_name_set(f'{DEFAULT_TEST_LAMBDA_NAME}-{uuid.uuid4()}')
        with self.assertRaises(KeyError):
            DependenciesCommandObject.run(args, True)
        self.DependenciesFileObject.dependencies_remove_file()


if __name__ == '__main__':
    unittest.main()
