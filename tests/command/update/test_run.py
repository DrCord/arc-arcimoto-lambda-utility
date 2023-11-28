import argparse
from time import sleep
import unittest
import warnings

from arcimoto_lambda_utility.command import update
from arcimoto_aws_services.lambda_service import LambdaService

from tests.command_args import UpdateCommandArgs
from tests.LambdaHelper import LambdaHelper


class TestRun(unittest.TestCase):

    default_description = 'Unit test created'
    LambdaServiceObject = None
    _lambdas_created = []
    UpdateCommandObject = None

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
        # always clean up again in case of errors
        cls.TestHelperObject.dependencies_remove_file()
        cls.TestHelperObject.remove_tests_folder()
        for lambda_name in cls._lambdas_created:
            cls.TestHelperObject.lambda_remove(lambda_name)

    # test successes
    def test_run_success_with_code_changed(self):
        self._update_test(True)

    def test_run_success_without_code_changed(self):
        self._update_test(False)

    # test errors
    def test_run_error_lambda_file_not_found(self):
        args = UpdateCommandArgs()
        function_name = args.function_name
        self.TestHelperObject.dependencies_create_file(function_name)
        parser = argparse.ArgumentParser(description=self.default_description)
        UpdateCommandObject = update.Command(parser)
        with self.assertRaises(FileNotFoundError):
            UpdateCommandObject.run(args, True)
        self.TestHelperObject.dependencies_remove_file()

    def test_run_error_lambda_name_not_found(self):
        args = UpdateCommandArgs()
        function_name = args.function_name
        self.TestHelperObject.resources_create(function_name)
        self.LambdaServiceObject.archive_create(
            function_name=function_name,
            mute=True
        )
        parser = argparse.ArgumentParser(description=self.default_description)
        UpdateCommandObject = update.Command(parser)
        with self.assertRaises(self.LambdaServiceObject.client.exceptions.ResourceNotFoundException):
            UpdateCommandObject.run(args, True)
        self.TestHelperObject.resources_remove()

    # helper (non-test) functions
    def _cleanup(self, function_name):
        self._lambda_delete(function_name)
        self.TestHelperObject.resources_remove()
        self.LambdaServiceObject.zip_bytes = None

    def _lambda_create(self, lambda_name):
        args = UpdateCommandArgs()
        self.TestHelperObject.lambda_create(
            lambda_name,
            self.default_description,
            self.LambdaServiceObject.zip_bytes,
            args.role
        )

    def _lambda_delete(self, lambda_name):
        self.TestHelperObject.lambda_remove(lambda_name)

    def _lambda_dev_alias_create(self, lambda_name):
        self.TestHelperObject.lambda_dev_alias_create(lambda_name)

    def _lambda_update_command_run(self, args, fail=True):
        parser = argparse.ArgumentParser(description=self.default_description)
        UpdateCommandObject = update.Command(parser)
        command_run_successfully = False
        count = 0
        fail_count = 10
        while not command_run_successfully and count < fail_count:
            sleep(5)
            try:
                UpdateCommandObject.run(args, True)
                command_run_successfully = True
            except self.LambdaServiceObject.client.exceptions.ResourceConflictException as e:
                # lambda not ready to invoke yet
                count += 1
                if not command_run_successfully and count == fail_count:
                    self.fail(f'Unable to invoke lambda: {e}')
                continue
            except Exception as e:
                if fail:
                    self.fail(f'test failed unexpectedly: {e}')
                else:
                    raise e

    def _update_test(self, code_changed):
        # set up
        args = UpdateCommandArgs()
        function_name = args.function_name
        self.TestHelperObject.lambda_with_dev_alias_create(function_name)
        self._lambdas_created.append(function_name)
        self.TestHelperObject.resources_create(function_name)
        if code_changed:
            self.TestHelperObject.update_tests_lambda_file(function_name)
        # actions
        self._lambda_update_command_run(args)
        # tear down
        self.TestHelperObject.resources_remove()
        self._cleanup(function_name)


if __name__ == '__main__':
    unittest.main()
