import unittest

from arcimoto_lambda_utility.command.test import TestSuiteDependenciesSchema

from tests.dependencies import DependenciesConfigFile


class TestFileExists(unittest.TestCase):

    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        cls.DependenciesFileObject = DependenciesConfigFile()
        cls.TestSuiteObject = TestSuiteDependenciesSchema()
        cls.TestSuiteObject.mute_set(True)

    @classmethod
    def tearDownClass(cls):
        cls.DependenciesFileObject.schema_file_remove()

    # test successes
    def test_file_exists_success_file_does_exist(self):
        self.DependenciesFileObject.schema_file_create()
        self.assertTrue(self.TestSuiteObject.file_exists())
        self.DependenciesFileObject.schema_file_remove()

    def test_file_exists_success_file_does_not_exist(self):
        self.assertFalse(self.TestSuiteObject.file_exists())

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
