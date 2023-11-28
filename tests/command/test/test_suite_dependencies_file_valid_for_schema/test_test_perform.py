import unittest

from arcimoto_lambda_utility.command.test import TestSuiteDependenciesFileValidForSchema

from tests.LambdaHelper import LambdaHelper


class TestTestPerform(unittest.TestCase):

    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        cls.LambdaHelperObject = LambdaHelper()
        cls.TestSuiteObject = TestSuiteDependenciesFileValidForSchema()
        cls.TestSuiteObject.mute_set(True)

    @classmethod
    def tearDownClass(cls):
        cls.LambdaHelperObject.dependencies_remove_file()
        cls.LambdaHelperObject.dependencies_invalid_file_remove()
        cls.LambdaHelperObject.schema_file_remove()

    # test successes
    def test_test_perform_success(self):
        self.LambdaHelperObject.dependencies_create_file()
        self.LambdaHelperObject.schema_file_create()
        try:
            result = self.TestSuiteObject.test_perform()
        except Exception as e:
            self.fail(f'test failed: {e}')
        finally:
            self._cleanup()
        self.assertTrue(result)

    # test failures
    def test_test_perform_failure(self):
        dependencies_file_content = {
            'not-global_dependencies': {},
            'etc': {}
        }
        self.LambdaHelperObject.dependencies_create_file(None, dependencies_file_content)
        self.LambdaHelperObject.schema_file_create()
        try:
            result = self.TestSuiteObject.test_perform()
        except Exception as e:
            self.fail(f'test failed: {e}')
        finally:
            self._cleanup()
        self.assertFalse(result)

    # test errors
    def test_test_perform_error_file_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            self.TestSuiteObject.test_perform()

    # helper (non-test) functions
    def _cleanup(self):
        self.LambdaHelperObject.dependencies_remove_file()
        self.LambdaHelperObject.dependencies_invalid_file_remove()
        self.LambdaHelperObject.schema_file_remove()


if __name__ == '__main__':
    unittest.main()
