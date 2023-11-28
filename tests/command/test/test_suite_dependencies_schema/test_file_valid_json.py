import unittest

from arcimoto_lambda_utility.command.test import TestSuiteDependenciesSchema

from tests.dependencies import DependenciesConfigFile


class TestFileValidJson(unittest.TestCase):

    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        cls.DependenciesFileObject = DependenciesConfigFile()
        cls.TestSuiteObject = TestSuiteDependenciesSchema()
        cls.TestSuiteObject.mute_set(True)

    @classmethod
    def tearDownClass(cls):
        cls.DependenciesFileObject.schema_file_remove()
        cls.DependenciesFileObject.dependencies_invalid_file_remove()

    # test successes
    def test_file_valid_json_success(self):
        self.DependenciesFileObject.schema_file_create()
        self.assertTrue(self.TestSuiteObject.file_valid_json())
        self.DependenciesFileObject.schema_file_remove()

    def test_file_valid_json_failure(self):
        self.DependenciesFileObject.schema_invalid_file_create()
        self.assertFalse(self.TestSuiteObject.file_valid_json())
        self.DependenciesFileObject.schema_invalid_file_remove()

    # test errors
    def test_file_valid_json_error_file_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            self.TestSuiteObject.file_valid_json()


if __name__ == '__main__':
    unittest.main()
