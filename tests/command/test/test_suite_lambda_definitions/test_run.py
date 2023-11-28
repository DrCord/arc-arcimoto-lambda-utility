from time import sleep
import unittest
import warnings

from arcimoto_aws_services.lambda_service import LambdaService
from arcimoto_lambda_utility.command.test import TestSuiteLambdaDefinitions

from tests.bundles import TestBundles
from tests.command_args import TestCommandArgs
from tests.command.create.create import TestCreate
from tests.dependencies import DependenciesConfigFile


class TestRun(unittest.TestCase):

    default_description = 'default description from unit tests'
    LambdaServiceObject = None
    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        warnings.filterwarnings(
            'ignore',
            category=ResourceWarning
        )
        cls.args = TestCommandArgs()
        cls.args.function_name = 'None'
        cls.args.test_lambda_definitions = True
        cls.DependenciesFileObject = DependenciesConfigFile()
        cls.DependenciesFileObject.dependencies_create_file()
        cls.DependenciesFileObject.schema_file_create()
        cls.TestCreateObject = TestCreate()
        cls.TestBundlesObject = TestBundles()
        cls.TestBundlesObject.bundle_schema_file_create()

        cls.LambdaServiceObject = LambdaService(
            verbose=False
        )

        cls.TestSuiteObject = TestSuiteLambdaDefinitions(cls.args)
        cls.TestSuiteObject.mute_set(True)
        cls.TestCreateObject.create_tests_files()

    @classmethod
    def tearDownClass(cls):
        cls.DependenciesFileObject.dependencies_remove_file()
        cls.TestCreateObject.remove_tests_folder()
        cls.DependenciesFileObject.schema_file_remove()
        cls.TestBundlesObject.bundle_schema_file_remove()

    # test successes
    def test_run_success(self):
        result = self.TestSuiteObject.run()
        self.assertTrue(result)

    # test errors
    # None

    # helper (non-test) functions
    def lambda_unit_test_invoke(self, args):
        invoked = False
        count = 0
        fail_count = 10
        while not invoked and count < fail_count:
            sleep(5)
            try:
                result = self.TestSuiteObject.run(args.payload)
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
