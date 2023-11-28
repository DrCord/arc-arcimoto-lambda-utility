import argparse
from time import sleep
import unittest
import warnings

from arcimoto_lambda_utility.command import runtime
from arcimoto_aws_services.lambda_service import LambdaService

from tests.command_args import RuntimeCommandArgs
from tests.LambdaHelper import LambdaHelper


class TestRun(unittest.TestCase):

    default_description = 'Unit test created'
    LambdaServiceObject = None
    _lambdas_created = []
    RuntimeCommandObject = None

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
    def test_run_success(self):
        # set up
        args = RuntimeCommandArgs()
        function_name = args.function_name
        self.TestHelperObject.lambda_with_dev_alias_create(function_name)
        self._lambdas_created.append(function_name)
        # actions
        self._lambda_runtime_command_run(args)
        # tear down
        self._cleanup(function_name)

    # test errors
    def test_run_error_lambda_name_not_found(self):
        args = RuntimeCommandArgs()
        parser = argparse.ArgumentParser(description=self.default_description)
        RuntimeCommandObject = runtime.Command(parser)
        with self.assertRaises(self.LambdaServiceObject.client.exceptions.ResourceNotFoundException):
            RuntimeCommandObject.run(args, True)

    # helper (non-test) functions
    def _cleanup(self, function_name):
        self._lambda_delete(function_name)
        self.TestHelperObject.resources_remove()
        self.LambdaServiceObject.zip_bytes = None

    def _lambda_create(self, lambda_name):
        args = RuntimeCommandArgs()
        self.arn = self.TestHelperObject.lambda_create(
            lambda_name,
            self.default_lambda_description,
            self.LambdaServiceObject.zip_bytes,
            args.role
        )

    def _lambda_delete(self, lambda_name):
        self.arn = self.TestHelperObject.lambda_remove(lambda_name)

    def _lambda_dev_alias_create(self, lambda_name):
        self.TestHelperObject.lambda_dev_alias_create(lambda_name)

    def _lambda_runtime_command_run(self, args, fail=True):
        parser = argparse.ArgumentParser(description=self.default_description)
        InvokeCommandObject = runtime.Command(parser)
        invoked = False
        count = 0
        fail_count = 10
        while not invoked and count < fail_count:
            sleep(5)
            try:
                InvokeCommandObject.run(args, True)
                invoked = True
            except self.LambdaServiceObject.client.exceptions.ResourceConflictException as e:
                # lambda not ready to invoke yet
                count += 1
                if not invoked and count == fail_count:
                    self.fail(f'Unable to invoke lambda: {e}')
                continue
            except Exception as e:
                if fail:
                    self.fail(f'test failed unexpectedly: {e}')
                else:
                    raise e


if __name__ == '__main__':
    unittest.main()
