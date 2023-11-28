import unittest

from arcimoto_lambda_utility.command import test

from tests.command_args import TestCommandArgs


class TestRunTests(unittest.TestCase):

    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        cls.args = TestCommandArgs()
        cls.TestSuiteObject = test.TestSuite()
        cls.TestSuiteObject.mute_set(True)
        cls.entity_name = cls.args.function_name
        cls.TestSuiteObject.test_suite_name = f'{cls.entity_name}_test_suite_1'

    # test successes
    def test_run_tests_success(self):
        try:
            self.TestSuiteObject.run_tests()
        except Exception as e:
            self.fail(f'test suite failed: {e}')

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
