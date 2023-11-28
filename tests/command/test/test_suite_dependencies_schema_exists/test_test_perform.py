import unittest

from arcimoto_lambda_utility.command.test import TestSuiteDependenciesSchemaExists

from tests.dependencies import DependenciesConfigFile


class TestTestPerform(unittest.TestCase):

    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        cls.DependenciesFileObject = DependenciesConfigFile()
        cls.TestSuiteObject = TestSuiteDependenciesSchemaExists()
        cls.TestSuiteObject.mute_set(True)

    @classmethod
    def tearDownClass(cls):
        cls.DependenciesFileObject.dependencies_remove_file()

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
        try:
            result = self.TestSuiteObject.test_perform()
        except Exception as e:
            self.fail(f'test failed: {e}')
        self.assertFalse(result)

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
