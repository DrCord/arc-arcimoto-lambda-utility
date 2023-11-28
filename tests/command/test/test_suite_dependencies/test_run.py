import unittest

from arcimoto_lambda_utility.command.test import TestSuiteDependencies


class TestRun(unittest.TestCase):

    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        cls.TestSuiteObject = TestSuiteDependencies()
        cls.TestSuiteObject.mute_set(True)

    # test successes
    def test_run_success(self):
        self.assertTrue(self.TestSuiteObject.run())

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
