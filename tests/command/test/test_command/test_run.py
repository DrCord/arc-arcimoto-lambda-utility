import argparse
import os
from time import sleep
import unittest
import warnings

from arcimoto_lambda_utility.command import test
from arcimoto_aws_services.lambda_service import LambdaService

from tests.command_args import (
    TestCommandArgs,
    TestIndividualLambdaCommandArgs,
    TestNonIndividualLambdaCommandArgs
)
from tests.LambdaHelper import LambdaHelper

from tests.bundles import TestBundles


class TestRun(unittest.TestCase):

    default_description = 'Unit test created'
    LambdaServiceObject = None
    _lambdas_created = []

    @classmethod
    def setUpClass(cls):
        warnings.filterwarnings(
            'ignore',
            category=ResourceWarning
        )
        cls.LambdaServiceObject = LambdaService(verbose=False)
        cls.TestHelperObject = LambdaHelper()
        cls.TestBundlesObject = TestBundles()
        cls.TestBundlesObject.bundle_schema_file_create()

    @classmethod
    def tearDownClass(cls):
        cls.TestHelperObject.dependencies_remove_file()
        cls.TestHelperObject.remove_tests_folder()
        cls.TestBundlesObject.bundle_schema_file_remove()
        for lambda_name in cls._lambdas_created:
            cls.TestHelperObject.lambda_remove(lambda_name)

    # No tests against input:
    # - payload/file-name
    # - user
    # - client-id
    # - dependencies-json-file-path
    # - bundle-json-file-path

    # test successes
    def test_run_success_test_individual_lambda_tests_found(self):
        self._individual_lambda_tests_found_test(False)

    def test_run_success_test_individual_lambda_tests_found_output_xml(self):
        self._individual_lambda_tests_found_test(True)

    def test_run_success_test_individual_lambda_no_tests_found(self):
        self._individual_lambda_no_tests_found_test(False)

    def test_run_success_test_individual_lambda_no_tests_found_output_xml(self):
        self._individual_lambda_no_tests_found_test(True)

    def test_run_success_test_lambda_definitions(self):
        self._lambda_definitions_test(False)

    def test_run_success_test_lambda_definitions_output_xml(self):
        self._lambda_definitions_test(True)

    def test_run_success_test_dependencies_file_exists(self):
        self._dependencies_file_exists_test(False)

    def test_run_success_test_dependencies_file_exists_output_xml(self):
        self._dependencies_file_exists_test(True)

    def test_run_success_test_dependencies_schema_exists(self):
        self._dependencies_schema_exists_test(False)

    def test_run_success_test_dependencies_schema_exists_output_xml(self):
        self._dependencies_schema_exists_test(True)

    def test_run_success_test_dependencies_file_valid_json(self):
        self._dependencies_file_valid_json_test(False)

    def test_run_success_test_dependencies_file_valid_json_output_xml(self):
        self._dependencies_file_valid_json_test(True)

    def test_run_success_test_dependencies_schema_valid_json(self):
        self._dependencies_schema_valid_json_output_xml(False)

    def test_run_success_test_dependencies_schema_valid_json_output_xml(self):
        self._dependencies_schema_valid_json_output_xml(True)

    def test_run_success_test_dependencies_file_valid_for_schema(self):
        self._dependencies_file_valid_for_schema_test(False)

    def test_run_success_test_dependencies_file_valid_for_schema_output_xml(self):
        self._dependencies_file_valid_for_schema_test(True)

    # test failures (and skips)
    def test_run_failure_test_individual_lambda_tests_found(self):
        args = TestCommandArgs()
        function_name = args.function_name
        unit_test_function_name = f'test_{function_name}'

        self.TestHelperObject.dependencies_create_file(function_name)
        self.TestHelperObject.create_tests_files_with_unit_test_lambda(function_name)
        # create unit test lambda code .py file
        lambda_code = self.TestHelperObject.lambda_code_unit_test_failure
        self.TestHelperObject.lambda_tests_file_create(unit_test_function_name, lambda_code)

        # create regular lambda, attach global_dependencies layer and create dev alias
        self.LambdaServiceObject.archive_create(
            function_name=function_name,
            mute=True
        )
        self.LambdaServiceObject.create(
            function_name=function_name,
            description=self.default_description,
            zip_bytes=self.LambdaServiceObject.zip_bytes,
            role=args.role,
            mute=True
        )
        self.LambdaServiceObject.add_layers(
            function_name=function_name,
            mute=True
        )
        self.LambdaServiceObject.lambda_dev_alias_create(
            function_name=function_name,
            mute=True
        )
        # create unit test lambda, attach global_dependencies layer and create dev alias
        self.LambdaServiceObject.archive_create(
            function_name=unit_test_function_name,
            mute=True
        )
        self.LambdaServiceObject.create(
            function_name=unit_test_function_name,
            description=self.default_description,
            zip_bytes=self.LambdaServiceObject.zip_bytes,
            role=args.role,
            mute=True
        )
        self.LambdaServiceObject.add_layers(
            function_name=unit_test_function_name,
            mute=True
        )
        self.LambdaServiceObject.lambda_dev_alias_create(
            function_name=unit_test_function_name,
            mute=True
        )
        result = self._lambda_unit_test_invoke(args)
        self.assertFalse(result)
        # tear down
        self._cleanup(function_name)
        self._cleanup(unit_test_function_name)

    def test_run_failure_test_lambda_definitions(self):
        args = TestNonIndividualLambdaCommandArgs()
        self.TestHelperObject.dependencies_create_file()
        parser = argparse.ArgumentParser(description=self.default_description)
        TestCommandObject = test.Command(parser)
        args.test_lambda_definitions = True
        try:
            result = TestCommandObject.run(args, True)
        except Exception as e:
            self.fail(f'test failed unexpectedly: {e}')
        finally:
            self._cleanup()
        self.assertFalse(result)

    def test_run_failure_test_dependencies_file_exists(self):
        args = TestNonIndividualLambdaCommandArgs()
        parser = argparse.ArgumentParser(description=self.default_description)
        TestCommandObject = test.Command(parser)
        args.test_dependencies_file_exists = True
        try:
            result = TestCommandObject.run(args, True)
        except Exception as e:
            self.fail(f'test failed unexpectedly: {e}')
        self.assertFalse(result)

    def test_run_failure_test_dependencies_schema_exists(self):
        args = TestNonIndividualLambdaCommandArgs()
        parser = argparse.ArgumentParser(description=self.default_description)
        TestCommandObject = test.Command(parser)
        args.test_dependencies_schema_exists = True
        try:
            result = TestCommandObject.run(args, True)
        except Exception as e:
            self.fail(f'test failed unexpectedly: {e}')
        self.assertFalse(result)

    def test_run_failure_test_dependencies_file_valid_json(self):
        args = TestNonIndividualLambdaCommandArgs()
        self.TestHelperObject.dependencies_invalid_file_create()
        parser = argparse.ArgumentParser(description=self.default_description)
        TestCommandObject = test.Command(parser)
        args.test_dependencies_file_valid_json = True
        try:
            result = TestCommandObject.run(args, True)
        except Exception as e:
            self.fail(f'test failed unexpectedly: {e}')
        finally:
            self._cleanup()
        self.assertFalse(result)

    def test_run_failure_test_dependencies_schema_valid_json(self):
        args = TestNonIndividualLambdaCommandArgs()
        self.TestHelperObject.schema_invalid_file_create()
        parser = argparse.ArgumentParser(description=self.default_description)
        TestCommandObject = test.Command(parser)
        args.test_dependencies_schema_valid_json = True
        try:
            result = TestCommandObject.run(args, True)
        except Exception as e:
            self.fail(f'test failed unexpectedly: {e}')
        finally:
            self._cleanup()
        self.assertFalse(result)

    def test_run_failure_test_dependencies_file_valid_for_schema(self):
        args = TestNonIndividualLambdaCommandArgs()
        file_content = {}
        self.TestHelperObject.dependencies_create_file(None, file_content)
        self.TestHelperObject.schema_file_create()
        parser = argparse.ArgumentParser(description=self.default_description)
        TestCommandObject = test.Command(parser)
        args.test_dependencies_file_valid_for_schema = True
        try:
            result = TestCommandObject.run(args, True)
        except Exception as e:
            self.fail(f'test failed unexpectedly: {e}')
        finally:
            self._cleanup()
        self.assertFalse(result)

    # test errors
    def test_run_error_dependencies_file_not_found(self):
        args = TestCommandArgs()
        parser = argparse.ArgumentParser(description=self.default_description)
        TestCommandObject = test.Command(parser)
        with self.assertRaises(FileNotFoundError):
            TestCommandObject.run(args, True)

    def test_run_error_input_invalid_no_test_selected(self):
        args = TestNonIndividualLambdaCommandArgs()
        parser = argparse.ArgumentParser(description=self.default_description)
        TestCommandObject = test.Command(parser)
        result = TestCommandObject.run(args, True)
        self.assertIsNone(result)

    def test_run_error_input_invalid_unit_test_lambda_selected(self):
        args = TestCommandArgs()
        function_name = args.function_name
        parser = argparse.ArgumentParser(description=self.default_description)
        TestCommandObject = test.Command(parser)
        args.function_name = f'test_{function_name}'
        result = TestCommandObject.run(args, True)
        self.assertIsNone(result)

    def test_run_error_test_individual_lambda_tests_found_botocore_ResourceNotFoundException(self):
        args = TestCommandArgs()
        function_name = args.function_name
        self.TestHelperObject.dependencies_create_file(function_name)
        self.TestHelperObject.create_tests_files_with_unit_test_lambda(function_name)
        parser = argparse.ArgumentParser(description=self.default_description)
        TestCommandObject = test.Command(parser)
        with self.assertRaises(self.LambdaServiceObject.client.exceptions.ResourceNotFoundException):
            TestCommandObject.run(args, True)

        self.TestHelperObject.remove_tests_folder()
        self.TestHelperObject.dependencies_remove_file()

    # helper (non-test) functions
    def _cleanup(self, function_name=None):
        self.TestHelperObject.resources_remove()
        if function_name is not None:
            self._lambda_delete(function_name)
            self.LambdaServiceObject.zip_bytes = None

    def _individual_lambda_tests_found_test(self, output_xml):
        # set up
        args = TestIndividualLambdaCommandArgs()
        if output_xml:
            args.output_xml = True
        function_name = args.function_name
        unit_test_function_name = f'test_{function_name}'
        self.TestHelperObject.lambda_with_dev_alias_create(function_name)
        self._lambdas_created.append(function_name)
        # create unit test lambda, attach global_dependencies layer and create dev alias
        self.TestHelperObject.lambda_with_dev_alias_create(unit_test_function_name)
        self._lambdas_created.append(unit_test_function_name)
        self.TestHelperObject.dependencies_create_file(function_name)
        # actions and assertions
        result = self._lambda_unit_test_invoke(args)
        self.assertTrue(result)
        if output_xml:
            self.assertTrue(os.path.isdir('test-reports'))
        # tear down
        self._cleanup(function_name)
        self._cleanup(unit_test_function_name)

    def _individual_lambda_no_tests_found_test(self, output_xml):
        # set up
        args = TestCommandArgs()
        function_name = args.function_name
        if output_xml:
            args.output_xml = True
        self.TestHelperObject.resources_create(function_name)
        # actions and assertions
        result = self._lambda_unit_test_invoke(args)
        self.assertTrue(result)
        if output_xml:
            self.assertTrue(os.path.isdir('test-reports'))
        # tear down
        self._cleanup()

    def _lambda_definitions_test(self, output_xml):
        # set up
        args = TestNonIndividualLambdaCommandArgs()
        self.TestHelperObject.dependencies_create_file()
        self.TestHelperObject.create_tests_files()
        args.test_lambda_definitions = True
        if output_xml:
            args.output_xml = True
        # actions and assertions
        result = self._lambda_unit_test_invoke(args)
        self.assertTrue(result)
        if output_xml:
            self.assertTrue(os.path.isdir('test-reports'))
        # tear down
        self._cleanup()

    def _dependencies_file_exists_test(self, output_xml):
        # set up
        args = TestNonIndividualLambdaCommandArgs()
        self.TestHelperObject.dependencies_create_file()
        args.test_dependencies_file_exists = True
        if output_xml:
            args.output_xml = True
        # actions and assertions
        result = self._lambda_unit_test_invoke(args)
        self.assertTrue(result)
        if output_xml:
            self.assertTrue(os.path.isdir('test-reports'))
        # tear down
        self._cleanup()

    def _dependencies_schema_exists_test(self, output_xml):
        # set up
        args = TestNonIndividualLambdaCommandArgs()
        self.TestHelperObject.schema_file_create()
        args.test_dependencies_schema_exists = True
        if output_xml:
            args.output_xml = True
        # actions and assertions
        result = self._lambda_unit_test_invoke(args)
        self.assertTrue(result)
        if output_xml:
            self.assertTrue(os.path.isdir('test-reports'))
        # tear down
        self._cleanup()

    def _dependencies_file_valid_json_test(self, output_xml):
        # set up
        args = TestNonIndividualLambdaCommandArgs()
        self.TestHelperObject.dependencies_create_file()
        args.test_dependencies_file_valid_json = True
        if output_xml:
            args.output_xml = True
        # actions and assertions
        result = self._lambda_unit_test_invoke(args)
        self.assertTrue(result)
        if output_xml:
            self.assertTrue(os.path.isdir('test-reports'))
        # tear down
        self._cleanup()

    def _dependencies_schema_valid_json_output_xml(self, output_xml):
        # set up
        args = TestNonIndividualLambdaCommandArgs()
        self.TestHelperObject.schema_file_create()
        args.test_dependencies_schema_valid_json = True
        if output_xml:
            args.output_xml = True
        # actions and assertions
        result = self._lambda_unit_test_invoke(args)
        self.assertTrue(result)
        if output_xml:
            self.assertTrue(os.path.isdir('test-reports'))
        # tear down
        self._cleanup()

    def _dependencies_file_valid_for_schema_test(self, output_xml):
        # set up
        args = TestNonIndividualLambdaCommandArgs()
        self.TestHelperObject.dependencies_create_file()
        self.TestHelperObject.schema_file_create()
        args.test_dependencies_file_valid_for_schema = True
        if output_xml:
            args.output_xml = True
        # actions and assertions
        result = self._lambda_unit_test_invoke(args)
        self.assertTrue(result)
        if output_xml:
            self.assertTrue(os.path.isdir('test-reports'))
        # tear down
        self._cleanup()

    def _lambda_delete(self, lambda_name):
        self.TestHelperObject.lambda_remove(lambda_name)

    def _lambda_unit_test_invoke(self, args):
        parser = argparse.ArgumentParser(description=self.default_description)
        TestCommandObject = test.Command(parser)
        invoked = False
        count = 0
        fail_count = 10
        while not invoked and count < fail_count:
            sleep(5)
            try:
                result = TestCommandObject.run(args, True)
                invoked = True
                return result
            except self.LambdaServiceObject.client.exceptions.ResourceConflictException as e:
                # lambda not ready to invoke yet
                count += 1
                if not invoked and count == fail_count:
                    self.fail(f'Unable to invoke lambda: {e}')
                continue
            except Exception as e:
                self.fail(f'test failed unexpectedly: {e}')


if __name__ == '__main__':
    unittest.main()
