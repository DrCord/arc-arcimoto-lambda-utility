import unittest

from arcimoto_lambda_utility.command import test

from tests.command_args import TestCommandArgs
from tests.command.create.create import TestCreate


class TestGenerateTestsXmlOutput(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.TestCreateObject = TestCreate()

        cls.args = TestCommandArgs()
        cls.TestSuiteObject = test.TestSuite()
        cls.TestSuiteObject.mute_set(True)
        cls.entity_name = cls.args.function_name

        cls.test_results = {
            f'{cls.entity_name}_test_suite_1': {
                'message': [
                    2
                ]
            },
            f'{cls.entity_name}_test_suite_2': {
                'message': [
                    1
                ]
            }
        }

    @classmethod
    def tearDownClass(cls):
        cls.TestCreateObject.remove_xml_output_folder()

    # test successes
    def test_generate_tests_xml_output_success(self):
        # set up
        self.TestSuiteObject.output_xml_folder_guarantee()
        # actions and assertions
        self.assertIsInstance(
            self.TestSuiteObject.generate_tests_xml_output(
                True,
                self.test_results,
                self.entity_name
            ),
            bytes
        )
        # tear down
        self.TestCreateObject.remove_xml_output_folder()

    def test_generate_tests_xml_output_success_input_test_results_empty(self):
        # set up
        self.TestSuiteObject.output_xml_folder_guarantee()
        self.assertFalse(
            self.TestSuiteObject.generate_tests_xml_output(
                True,
                {},
                self.entity_name
            )
        )
        # tear down
        self.TestCreateObject.remove_xml_output_folder()

    # test failures
    def test_generate_tests_xml_output_failure(self):
        # set up
        self.TestSuiteObject.output_xml_folder_guarantee()
        test_results = {
            f'{self.entity_name}_test_suite_1': {
                'message': [
                    2
                ],
                'issues': {
                    f'{self.entity_name}_test_suite_1_test_1': {
                        'message': 'arcimoto-lambda-utility unit test intentional failure'
                    }
                }
            },
            f'{self.entity_name}_test_suite_2': {
                'message': [
                    1
                ]
            }
        }
        # actions and assertions
        self.assertIsInstance(
            self.TestSuiteObject.generate_tests_xml_output(
                False,
                test_results,
                self.entity_name
            ),
            bytes
        )
        # tear down
        self.TestCreateObject.remove_xml_output_folder()

    def test_generate_tests_xml_output_failure_input_test_results_empty(self):
        # set up
        self.TestSuiteObject.output_xml_folder_guarantee()
        self.assertFalse(
            self.TestSuiteObject.generate_tests_xml_output(
                False,
                {},
                self.entity_name
            )
        )
        # tear down
        self.TestCreateObject.remove_xml_output_folder()

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
