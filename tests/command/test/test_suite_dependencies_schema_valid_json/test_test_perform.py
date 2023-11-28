import unittest

from arcimoto_lambda_utility.command.test import TestSuiteDependenciesSchemaValidJson

from tests.dependencies import DependenciesConfigFile


class TestTestPerform(unittest.TestCase):

    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        cls.DependenciesFileObject = DependenciesConfigFile()
        cls.TestSuiteObject = TestSuiteDependenciesSchemaValidJson()
        cls.TestSuiteObject.mute_set(True)

    @classmethod
    def tearDownClass(cls):
        cls.DependenciesFileObject.schema_file_remove()
        cls.DependenciesFileObject.schema_invalid_file_remove()

    # test successes
    def test_test_perform_success(self):
        self.DependenciesFileObject.schema_file_create()
        try:
            result = self.TestSuiteObject.test_perform()
        except Exception as e:
            self.fail(f'test failed: {e}')
        finally:
            self.DependenciesFileObject.schema_file_remove()
        self.assertTrue(result)

    # test failures
    def test_test_perform_failure(self):
        self.DependenciesFileObject.schema_invalid_file_create()
        try:
            result = self.TestSuiteObject.test_perform()
        except Exception as e:
            self.fail(f'test failed: {e}')
        finally:
            self.DependenciesFileObject.schema_invalid_file_remove()
        self.assertFalse(result)

    # test errors
    def test_test_perform_error_file_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            self.TestSuiteObject.test_perform()


if __name__ == '__main__':
    unittest.main()
