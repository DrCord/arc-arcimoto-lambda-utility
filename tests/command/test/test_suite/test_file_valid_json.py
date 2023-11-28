import unittest

from arcimoto_lambda_utility.command import test


class TestFileValidJson(unittest.TestCase):

    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        cls.TestSuiteObject = test.TestSuite()
        cls.TestSuiteObject.mute_set(True)

    # test successes
    def test_file_valid_json_success(self):
        try:
            self.TestSuiteObject.file_valid_json()
        except Exception as e:
            self.fail(f'test suite failed: {e}')

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
