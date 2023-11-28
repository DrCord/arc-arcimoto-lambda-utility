import argparse
from time import sleep
import unittest
import warnings

from arcimoto_lambda_utility.command import grant_api

from arcimoto_aws_services.lambda_service import LambdaApiGatewayService

from tests.LambdaHelper import LambdaHelper

from tests.command_args import (
    GrantApiCommandArgs,
    DEFAULT_TEST_API_ID,
    DEFAULT_TEST_API_PATH,
    DEFAULT_TEST_LAMBDA_ENV
)


class TestRun(unittest.TestCase):

    default_description = 'Unit test created'
    parser = None
    default_parser_description = 'Unit test created'
    GrantApiCommandObject = None
    _lambdas_created = []

    @classmethod
    def setUpClass(cls):
        warnings.filterwarnings(
            'ignore',
            category=ResourceWarning
        )
        cls.args = GrantApiCommandArgs()
        cls.TestHelperObject = LambdaHelper()
        cls.LambdaServiceObject = LambdaApiGatewayService(verbose=False)

    @classmethod
    def tearDownClass(cls):
        cls.TestHelperObject.dependencies_remove_file()
        cls.TestHelperObject.remove_tests_folder()
        for lambda_name in cls._lambdas_created:
            cls.TestHelperObject.lambda_remove(lambda_name)

    # test successes
    def test_run_success_policy_does_not_exist(self):
        # set up
        args = GrantApiCommandArgs()
        function_name = args.function_name
        self.TestHelperObject.lambda_with_dev_alias_create(function_name)
        self._lambdas_created.append(function_name)
        # actions
        self.assertTrue(self._lambda_grant_api_command_run(args))
        # tear down
        self._cleanup(function_name)

    def test_run_success_policy_exists(self):
        # set up
        args = GrantApiCommandArgs()
        function_name = args.function_name
        self.TestHelperObject.lambda_with_dev_alias_create(function_name)
        self._lambdas_created.append(function_name)
        self._policy_deploy(args)
        # actions
        self.assertFalse(self._lambda_grant_api_command_run(args))
        # tear down
        self._cleanup(function_name)

    # test errors
    def test_run_error_lambda_name_not_found(self):
        args = GrantApiCommandArgs()
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        GrantApiCommandObject = grant_api.Command(parser)
        with self.assertRaises(self.LambdaServiceObject.client.exceptions.ResourceNotFoundException):
            GrantApiCommandObject.run(args, True)

    def test_run_error_lambda_name_alias_not_found(self):
        # set up
        args = GrantApiCommandArgs()
        function_name = args.function_name
        self.TestHelperObject.resources_create(function_name)
        self.LambdaServiceObject.archive_create(
            function_name=function_name,
            mute=True
        )
        self._lambda_create(function_name)
        self._lambdas_created.append(function_name)
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        GrantApiCommandObject = grant_api.Command(parser)
        # actions
        with self.assertRaises(self.LambdaServiceObject.client.exceptions.ResourceNotFoundException):
            GrantApiCommandObject.run(self.args, True)
        # tear down
        self._cleanup(function_name)

    # helper (non-test) functions
    def _cleanup(self, function_name):
        self._lambda_delete(function_name)
        self.TestHelperObject.resources_remove()
        self.LambdaServiceObject.zip_bytes = None

    def _lambda_create(self, lambda_name):
        args = GrantApiCommandArgs()
        self.TestHelperObject.lambda_create(
            lambda_name,
            self.default_description,
            self.LambdaServiceObject.zip_bytes,
            args.role
        )

    def _lambda_delete(self, lambda_name):
        self.TestHelperObject.lambda_remove(lambda_name)

    def _lambda_grant_api_command_run(self, args, fail=True):
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        GrantApiCommandObject = grant_api.Command(parser)
        invoked = False
        count = 0
        fail_count = 10
        result = None
        while not invoked and count < fail_count:
            sleep(5)
            try:
                result = GrantApiCommandObject.run(args, True)
                invoked = True
            except self.LambdaServiceObject.client.exceptions.ResourceConflictException as e:
                # lambda not ready yet
                count += 1
                if not invoked and count == fail_count:
                    self.fail(f'Unable to grant-api for lambda: {e}')
                continue
            except Exception as e:
                if fail:
                    self.fail(f'test failed unexpectedly: {e}')
                else:
                    raise e

        return result

    def _policy_deploy(self, args):
        lambda_arn = self.LambdaServiceObject.lambda_arn_build(
            args.region,
            args.account_id,
            args.function_name,
            DEFAULT_TEST_LAMBDA_ENV
        )
        api_arn = self.LambdaServiceObject.api_arn_build(
            args.region,
            args.account_id,
            DEFAULT_TEST_API_ID,
            DEFAULT_TEST_API_PATH
        )
        invoked = False
        count = 0
        fail_count = 10
        result = None
        while not invoked and count < fail_count:
            sleep(5)
            try:
                self.LambdaServiceObject.policy_deploy(
                    api_arn=api_arn,
                    lambda_arn=lambda_arn,
                    mute=True
                )
                invoked = True
            except self.LambdaServiceObject.client.exceptions.ResourceConflictException as e:
                # lambda not ready yet
                count += 1
                if not invoked and count == fail_count:
                    raise e
                continue
            except Exception as e:
                raise e

        return result


if __name__ == '__main__':
    unittest.main()
