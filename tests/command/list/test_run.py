import argparse
import unittest

from arcimoto_lambda_utility import command

from tests.dependencies import DependenciesConfigFile

from tests.command_args import ListCommandArgs


class TestRun(unittest.TestCase):

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
    def test_run_success_no_input(self):
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        ListCommandObject = command.list.Command(parser)
        try:
            ListCommandObject.run(self.args, True)
        except Exception as e:
            self.fail(f'test failed unexpectedly: {e}')

    def test_run_success_input_global_dependencies(self):
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        ListCommandObject = command.list.Command(parser)
        self.args.global_dependencies = True
        try:
            ListCommandObject.run(self.args, True)
        except Exception as e:
            self.fail(f'test failed unexpectedly: {e}')

    def test_run_success_input_common_config(self):
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        ListCommandObject = command.list.Command(parser)
        self.args.common_config = True
        try:
            ListCommandObject.run(self.args, True)
        except Exception as e:
            self.fail(f'test failed unexpectedly: {e}')

    def test_run_success_input_bundle(self):
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        ListCommandObject = command.list.Command(parser)
        self.args.bundle = 'tests'
        try:
            ListCommandObject.run(self.args, True)
        except Exception as e:
            self.fail(f'test failed unexpectedly: {e}')

    def test_run_success_input_include_filepath(self):
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        ListCommandObject = command.list.Command(parser)
        self.args.include_filepath = True
        try:
            ListCommandObject.run(self.args, True)
        except Exception as e:
            self.fail(f'test failed unexpectedly: {e}')

    def test_run_success_input_exclude_tests(self):
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        ListCommandObject = command.list.Command(parser)
        self.args.exclude_tests = True
        try:
            ListCommandObject.run(self.args, True)
        except Exception as e:
            self.fail(f'test failed unexpectedly: {e}')

    def test_run_success_input_tests_only(self):
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        ListCommandObject = command.list.Command(parser)
        self.args.tests_only = True
        try:
            ListCommandObject.run(self.args, True)
        except Exception as e:
            self.fail(f'test failed unexpectedly: {e}')

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
