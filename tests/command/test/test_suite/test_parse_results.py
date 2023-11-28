import unittest

from arcimoto_lambda_utility.command import test
from tests.command.create.create import TestCreate


class TestParseResults(unittest.TestCase):

    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        cls.TestSuiteObject = test.TestSuite()
        cls.TestCreateObject = TestCreate()

    # test successes
    def test_parse_results_success(self):
        # set up
        test_results = [self.TestSuiteObject.test_suite_output_template]
        # actions and assertions
        try:
            self.TestSuiteObject.parse_results(test_results)
        except Exception as e:
            self.fail(f'test suite failed: {e}')

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
