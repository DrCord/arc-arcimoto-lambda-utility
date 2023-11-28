import unittest

from arcimoto_lambda_utility.command.test import TestSuiteDependenciesFile

from tests.dependencies import DependenciesConfigFile


class TestFileExists(unittest.TestCase):

    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        cls.DependenciesFileObject = DependenciesConfigFile()
        cls.TestSuiteObject = TestSuiteDependenciesFile()
        cls.TestSuiteObject.mute_set(True)

    @classmethod
    def tearDownClass(cls):
        cls.DependenciesFileObject.dependencies_remove_file()

    # test successes
    def test_file_exists_success(self):
        self.DependenciesFileObject.dependencies_create_file()
        self.assertTrue(self.TestSuiteObject.file_exists())
        self.DependenciesFileObject.dependencies_remove_file()

    # test failures
    def test_file_exists_failure(self):
        self.assertFalse(self.TestSuiteObject.file_exists())

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
