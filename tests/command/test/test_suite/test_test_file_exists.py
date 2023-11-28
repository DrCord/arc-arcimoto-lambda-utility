import unittest

from arcimoto_lambda_utility.command import test


class TestTestFileExists(unittest.TestCase):

    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        cls.TestSuiteObject = test.TestSuite()
        cls.TestSuiteObject.mute_set(True)

    # test successes
    def test_test_file_exists_success(self):
        try:
            self.TestSuiteObject.test_file_exists()
        except Exception as e:
            self.fail(f'test suite failed: {e}')

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
