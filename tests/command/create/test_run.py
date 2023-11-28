import argparse
import unittest
import warnings

from arcimoto_lambda_utility.command import create
from arcimoto_aws_services.lambda_service import LambdaService

from tests.LambdaHelper import LambdaHelper

from tests.command_args import CreateCommandArgs


class TestRun(unittest.TestCase):

    parser = None
    default_parser_description = 'Unit test created'
    LambdaServiceObject = None
    TestHelperObject = None
    _lambdas_created = []

    @classmethod
    def setUpClass(cls):
        warnings.filterwarnings(
            'ignore',
            category=ResourceWarning
        )
        cls.TestHelperObject = LambdaHelper()
        cls.LambdaServiceObject = LambdaService(verbose=False)

    @classmethod
    def tearDownClass(cls):
        cls.TestHelperObject.dependencies_remove_file()
        cls.TestHelperObject.remove_tests_folder()
        for lambda_name in cls._lambdas_created:
            cls.TestHelperObject.lambda_remove(lambda_name)

    # test successes
    def test_run_success(self):
        # set up
        args = CreateCommandArgs()
        function_name = args.function_name
        self.TestHelperObject.resources_create(function_name)
        self.LambdaServiceObject.archive_create(
            function_name=function_name,
            mute=True
        )
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        CreateCommandObject = create.Command(parser)
        # actions and assertions
        self.assertTrue(CreateCommandObject.run(args, True))
        self._lambdas_created.append(function_name)
        # tear down
        self._cleanup(function_name)

    # test errors
    def test_run_error_lambda_name_exists(self):
        # set up
        args = CreateCommandArgs()
        function_name = args.function_name
        self.TestHelperObject.lambda_with_dev_alias_create(function_name)
        self._lambdas_created.append(function_name)
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        CreateCommandObject = create.Command(parser)
        self.TestHelperObject.resources_create(function_name)
        # actions
        self.assertIsNone(CreateCommandObject.run(args, True))
        # tear down
        self._cleanup(function_name)

    def test_run_error_dependencies_file_not_found(self):
        args = CreateCommandArgs()
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        CreateCommandObject = create.Command(parser)
        with self.assertRaises(FileNotFoundError):
            CreateCommandObject.run(args, True)
        # tear down
        self._cleanup(args.function_name)

    def test_run_error_lambda_name_configuration_not_found(self):
        args = CreateCommandArgs()
        self.TestHelperObject.resources_create(f'{args.function_name}-will-not-match')
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        CreateCommandObject = create.Command(parser)
        with self.assertRaises(KeyError):
            CreateCommandObject.run(args, True)
        # tear down
        self._cleanup(args.function_name)

    # helper (non-test) functions
    def _cleanup(self, function_name):
        self._lambda_delete(function_name)
        self.TestHelperObject.resources_remove()
        self.LambdaServiceObject.zip_bytes = None

    def _lambda_create(self, lambda_name):
        self.TestInvokeObject.lambda_create(
            lambda_name,
            self.default_description,
            self.LambdaServiceObject.zip_bytes,
            self.args.role
        )

    def _lambda_delete(self, lambda_name):
        self.TestHelperObject.lambda_remove(lambda_name)


if __name__ == '__main__':
    unittest.main()
