from time import sleep
import unittest
import warnings

from arcimoto_aws_services.lambda_service import LambdaService
from arcimoto_lambda_utility.command.test import TestSuiteLambda

from tests.command_args import TestCommandArgs
from tests.LambdaHelper import LambdaHelper


class TestRun(unittest.TestCase):

    args = None
    default_description = 'default description from unit tests'
    function_name = None
    LambdaServiceObject = None
    TestSuiteObject = None
    unit_test_function_name = None

    @classmethod
    def setUpClass(cls):
        warnings.filterwarnings(
            'ignore',
            category=ResourceWarning
        )
        cls.args = TestCommandArgs()
        cls.function_name = cls.args.function_name
        cls.unit_test_function_name = f'test_{cls.function_name}'

        cls.TestHelperObject = LambdaHelper()
        cls.LambdaServiceObject = LambdaService(verbose=False)

        cls.TestHelperObject.dependencies_create_file(cls.function_name)
        cls.TestSuiteObject = TestSuiteLambda(cls.function_name)
        cls.TestSuiteObject.mute_set(True)

        # cls.TestHelperObject.create_tests_files_with_unit_test_lambda(cls.function_name)

        # create regular lambda, attach global_dependencies layer and create dev alias
        cls.TestHelperObject.lambda_with_dev_alias_create(cls.function_name)
        cls.TestHelperObject.dependencies_create_file(cls.function_name)
        cls.LambdaServiceObject.add_layers(
            function_name=cls.function_name,
            mute=True
        )
        # create unit test lambda, attach global_dependencies layer and create dev alias
        cls.TestHelperObject.lambda_with_dev_alias_create(cls.unit_test_function_name)
        cls.TestHelperObject.dependencies_create_file(cls.unit_test_function_name)
        cls.LambdaServiceObject.add_layers(
            function_name=cls.unit_test_function_name,
            mute=True
        )
        cls.args.payload_set()

    @classmethod
    def tearDownClass(cls):
        cls.TestHelperObject.dependencies_remove_file()
        cls.TestHelperObject.remove_tests_folder()
        cls.TestHelperObject.dependencies_remove_file()
        cls.LambdaServiceObject.delete(
            function_name=cls.function_name,
            mute=True
        )
        cls.LambdaServiceObject.delete(
            function_name=cls.unit_test_function_name,
            mute=True
        )

    # test successes
    def test_run_success(self):
        self.assertTrue(self._lambda_unit_test_invoke())

    # test errors
    # None

    def _lambda_unit_test_invoke(self):
        invoked = False
        count = 0
        fail_count = 10
        while not invoked and count < fail_count:
            sleep(5)
            try:
                result = self.TestSuiteObject.run(self.args.payload)
                invoked = True
                return result
            except self.LambdaServiceObject.client.exceptions.ResourceConflictException as e:
                # lambda not ready to invoke yet
                count += 1
                if not invoked and count == fail_count:
                    self.fail(f'Unable to invoke lambda: {e}')
                continue
            except Exception as e:
                self.fail(f'test failed unexpectedly: {e}')


if __name__ == '__main__':
    unittest.main()
