from copy import deepcopy
import unittest

from arcimoto_lambda_utility.command import test


class TestTestSuiteNameSet(unittest.TestCase):

    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        cls.TestSuiteObject = test.TestSuite()
        cls.TestSuiteObject.mute_set(True)
        cls.test_results = deepcopy(cls.TestSuiteObject.test_suite_output_template)

    # test successes
    def test_test_suite_name_set_success(self):
        try:
            self.TestSuiteObject.test_suite_name_set(self.TestSuiteObject.__class__.__name__)
        except Exception as e:
            self.fail(f'test suite failed: {e}')

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
