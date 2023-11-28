import unittest

from arcimoto_lambda_utility.command import test


class TestMuteSet(unittest.TestCase):

    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        cls.TestSuiteObject = test.TestSuite()

    # test successes
    def test_mute_set_success(self):
        try:
            self.TestSuiteObject.mute_set(True)
        except Exception as e:
            self.fail(f'test suite failed: {e}')

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
