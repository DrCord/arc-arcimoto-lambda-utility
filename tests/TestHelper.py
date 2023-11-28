import json
import os
import os.path
import shutil

from tests.command_args import (
    CommandArgs,
    DEFAULT_TEST_LAMBDA_NAME
)


class TestHelper:

    bundle_json_content = {
        'name': 'tests',
        'vpc': 'none',
        'lambdas': {}
    }
    lambda_name = None

    invalid_json_file_created = False
    invalid_json_content = '{{not-valid-json}'
    invalid_json_file_path = None

    def __init__(self, lambda_name=DEFAULT_TEST_LAMBDA_NAME, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lambda_name = lambda_name

    @property
    def lambda_code_basic(self):
        return '''
def lambda_handler(event_data, lambda_config):
    print("hello Arcimoto!")
    return True
'''

    @property
    def lambda_code_unit_test(self):
        return '''
import logging
import unittest

from arcimoto.exceptions import *
import arcimoto.runtime
import arcimoto.tests

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ArcimotoLambdaUtilityUnitTest_TestCase(unittest.TestCase):

    def test_arcimoto_lambda_utility_unit_test_success(self):
        self.assertTrue(arcimoto.runtime.test_invoke_lambda('alu_unit_test', {}, False))


@arcimoto.runtime.handler
def test_arcimoto_lambda_utility_unit_test():
    return arcimoto.tests.handle_test_result(unittest.TextTestRunner().run(
        unittest.TestLoader().loadTestsFromTestCase(ArcimotoLambdaUtilityUnitTest_TestCase)
    ))


lambda_handler = test_arcimoto_lambda_utility_unit_test

'''

    @property
    def lambda_code_unit_test_failure(self):
        return '''
import logging
import unittest

from arcimoto.exceptions import *
import arcimoto.runtime
import arcimoto.tests

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ArcimotoLambdaUtilityUnitTest_TestCase(unittest.TestCase):

    def test_arcimoto_lambda_utility_unit_test_failure(self):
        self.assertFalse(arcimoto.runtime.test_invoke_lambda('alu_unit_test', {}, False))


@arcimoto.runtime.handler
def test_arcimoto_lambda_utility_unit_test():
    return arcimoto.tests.handle_test_result(unittest.TextTestRunner().run(
        unittest.TestLoader().loadTestsFromTestCase(ArcimotoLambdaUtilityUnitTest_TestCase)
    ))


lambda_handler = test_arcimoto_lambda_utility_unit_test

'''

    def invalid_json_file_create(self, output_file_path):
        # do not proceed if file already exists
        file_exists = os.path.exists(output_file_path)
        if file_exists:
            return

        self.invalid_json_file_path = output_file_path
        with open(self.invalid_json_file_path, 'w') as outfile:
            self.invalid_json_file_created = True
            outfile.write(self.invalid_json_content)

    def invalid_json_file_remove(self):
        # do not proceed if file was not created by this tests helper class
        if self.invalid_json_file_created and self.invalid_json_file_path is not None:
            try:
                os.remove(self.invalid_json_file_path)
            except Exception:
                pass

    def safe_open_w(self, path):
        ''' Open "path" for writing, creating any parent directories as needed.
        '''
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return open(path, 'w')

    def lambda_bundle_json_tests_file_create(self, lambda_name=DEFAULT_TEST_LAMBDA_NAME, file_content=None):
        args = CommandArgs()
        lambda_name = args.function
        if file_content is None:
            self.bundle_json_content['lambdas'][lambda_name] = {
                'tests': []
            }
        else:
            self.bundle_json_content = file_content
        with self.safe_open_w('lambda/tests/bundle.json') as f:
            f.write(json.dumps(self.bundle_json_content))

        return None

    def lambda_tests_file_create(self, lambda_name=DEFAULT_TEST_LAMBDA_NAME, lambda_code=None):
        if lambda_name is None:
            args = CommandArgs()
            lambda_name = args.function

        if lambda_code is not None:
            file_content = lambda_code
        else:
            file_content = self.lambda_code_basic
        with self.safe_open_w(f'lambda/tests/{lambda_name}.py') as f:
            f.write(file_content)

        return None

    def create_tests_files(self, lambda_name=DEFAULT_TEST_LAMBDA_NAME):
        self.lambda_tests_file_create(lambda_name)
        self.lambda_bundle_json_tests_file_create(lambda_name)

        return None

    def create_tests_files_with_unit_test_lambda(self, lambda_name):
        unit_test_lambda_name = f'test_{lambda_name}'

        # create lambda code .py file
        self.lambda_tests_file_create(lambda_name)

        # create unit test lambda code .py file
        lambda_code = self.lambda_code_unit_test
        self.lambda_tests_file_create(unit_test_lambda_name, lambda_code)

        # create combined bundle
        bundle_json_content = {
            'lambdas': {}
        }
        bundle_json_content['lambdas'][lambda_name] = {
            'tests': [
                f'test_{lambda_name}'
            ]
        }
        bundle_json_content['lambdas'][unit_test_lambda_name] = {
            'tests': []
        }
        self.lambda_bundle_json_tests_file_create(None, bundle_json_content)

        return None

    def remove_xml_output_folder(self):
        dirpath = os.path.join('test-reports')
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)

    def remove_tests_folder(self):
        dirpath = os.path.join('lambda', 'tests')
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
        # remove `lambda` folder only if empty
        dir_name = 'lambda'
        if os.path.isdir(dir_name):
            if not os.listdir(dir_name):
                shutil.rmtree(dir_name)

    def update_tests_lambda_file(self, lambda_name):
        # update lambda .py file
        file_content = '''
def lambda_handler(event_data, lambda_config):
    print("hello again Arcimoto!")
        '''
        with self.safe_open_w(f'lambda/tests/{lambda_name}.py') as f:
            f.write(file_content)

        return None
