import os
import unittest

from arcimoto_lambda_utility.command import test
from tests.command.create.create import TestCreate


class TestOutputXmlFolderGuarantee(unittest.TestCase):

    TestSuiteObject = None

    @classmethod
    def setUpClass(cls):
        cls.TestSuiteObject = test.TestSuite()
        cls.TestCreateObject = TestCreate()

    @classmethod
    def tearDownClass(cls):
        cls.TestCreateObject.remove_xml_output_folder()

    # test successes
    def test_output_xml_folder_guarantee_success(self):
        # actions and assertions
        try:
            self.TestSuiteObject.output_xml_folder_guarantee()
        except Exception as e:
            self.fail(f'test suite failed: {e}')
        self.assertTrue(os.path.isdir('test-reports'))
        self.TestCreateObject.remove_xml_output_folder()

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
