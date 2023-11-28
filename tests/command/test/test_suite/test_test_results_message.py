from copy import deepcopy
import unittest

from arcimoto_lambda_utility.command import test


class TestTestResultsMessage(unittest.TestCase):

    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        cls.TestSuiteObject = test.TestSuite()
        cls.TestSuiteObject.mute_set(True)
        cls.test_results = deepcopy(cls.TestSuiteObject.test_suite_output_template)

    # test successes
    def test_test_results_message_success(self):
        try:
            self.TestSuiteObject.test_results_message(self.test_results)
        except Exception as e:
            self.fail(f'test suite failed: {e}')

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
