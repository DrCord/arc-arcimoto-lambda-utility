from copy import deepcopy
import datetime
import json
import jsonschema
import logging
import os
import re
from xml.dom import minidom

from .command import AbstractCommand

from arcimoto_aws_services.path import DEPENDENCIES_CONFIG
from arcimoto_aws_services import (
    bundle,
    cognito
)

from arcimoto_aws_services.lambda_service import LambdaService


class Command(AbstractCommand):

    function_name = None
    # non specific lambda test suites
    input_test_lambda_definitions = None
    input_test_dependencies_file_exists = None
    input_test_dependencies_schema_exists = None
    input_test_dependencies_file_valid_json = None
    input_test_dependencies_schema_valid_json = None
    input_test_dependencies_file_valid_for_schema = None

    input_dependencies_json_file_path = None
    input_bundle_json_file_path = None

    test_results = {}
    test_suite_success = None

    def __init__(self, arg_parser):
        super().__init__(arg_parser)
        self.arg_parser = arg_parser
        self._parser_add_arguments()

    def run(self, args, mute=False):
        super().run(args)
        if mute:
            self.logger.setLevel(logging.ERROR)

        self._parse_arguments(args, mute)

        self.test_suite_success = True

        # non specific lambda unit-test test suites
        if self.function_name is None:
            if True in [
                self.input_test_lambda_definitions,
                self.input_test_dependencies_file_exists,
                self.input_test_dependencies_schema_exists,
                self.input_test_dependencies_file_valid_json,
                self.input_test_dependencies_schema_valid_json,
                self.input_test_dependencies_file_valid_for_schema
            ]:
                return self._run_non_specific_lamda_test_suite()
            if not self.mute:
                self.logger.warning('If the input function is None then you must select another test option')
            return None

        # individual lambda unit test suites
        # don't test unit test lambdas
        if self.function_name.startswith('test_'):
            if not self.mute:
                self.logger.warning('Test utility does not work with unit test functions provided as the input function, please provide a normal lambda to detect and run it\'s unit tests.')
            return None

        lambda_test_suite = TestSuiteLambda(
            self.function_name,
            self.args.region,
            self.input_dependencies_json_file_path,
            self.input_bundle_json_file_path,
            self.args.output_xml,
            mute=self.mute
        )
        (self.test_suite_success, self.test_results) = lambda_test_suite.run(
            self.args.payload,
            self.args.file_name,
            self.args.user,
            self.args.client_id
        )

        return self.test_suite_success

    def _parse_arguments(self, args, mute):
        self.args = args
        self.function_name = args.function_name if args.function_name != 'None' else None
        self.region = args.region
        self.mute = mute

        # non specific lambda test suites
        self.input_test_lambda_definitions = self.args.test_lambda_definitions
        self.input_test_dependencies_file_exists = self.args.test_dependencies_file_exists
        self.input_test_dependencies_schema_exists = self.args.test_dependencies_schema_exists
        self.input_test_dependencies_file_valid_json = self.args.test_dependencies_file_valid_json
        self.input_test_dependencies_schema_valid_json = self.args.test_dependencies_schema_valid_json
        self.input_test_dependencies_file_valid_for_schema = self.args.test_dependencies_file_valid_for_schema

        self.input_dependencies_json_file_path = self.args.dependencies_json_file_path
        self.input_bundle_json_file_path = None if self.args.bundle_json_file_path == 'None' else self.args.bundle_json_file_path

    def _parser_add_arguments(self):
        self.arg_parser.add_argument(
            "function_name",
            help="the name of the lambda to invoke"
        )
        self.arg_parser.add_argument(
            "--user",
            default=None,
            help='authenticate as a specific user before invoking'
        )
        self.arg_parser.add_argument(
            "--client-id",
            default=cognito.DEFAULT_CLIENT_ID,
            help='specify which user pool to use for authentication'
        )
        self.arg_parser.add_argument(
            "--output-xml",
            action='store_true',
            help='output in xml format for pipeline, default false'
        )
        self.arg_parser.add_argument(
            "--dependencies-json-file-path",
            default=DEPENDENCIES_CONFIG,
            help='location of dependencies.json file, including file name'
        )
        self.arg_parser.add_argument(
            "--bundle-json-file-path",
            default='None',
            help='location of bundle.json file, including file name'
        )

        # payload mutually exclusive args group - inline in command vs file
        args_group_payload = self.arg_parser.add_mutually_exclusive_group()
        args_group_payload.add_argument(
            "--payload",
            type=json.loads,
            help='the payload to pass as data to the lambda',
            default={}
        )
        args_group_payload.add_argument(
            "--file-name",
            help='name of a json file to use as payload data'
        )

        # non specific function tests mutually exclusive args group
        args_group_non_function_tests = self.arg_parser.add_mutually_exclusive_group()
        args_group_non_function_tests.add_argument(
            '--test-lambda-definitions',
            action='store_true',
            help='validate the lambda definitions in dependencies.json and each bundle bundle.json file')
        args_group_non_function_tests.add_argument(
            '--test-dependencies-file-exists',
            action='store_true',
            help='validate the dependencies.json file exists')
        args_group_non_function_tests.add_argument(
            '--test-dependencies-schema-exists',
            action='store_true',
            help='validate the dependencies.schema.json file exists')
        args_group_non_function_tests.add_argument(
            '--test-dependencies-file-valid-json',
            action='store_true',
            help='validate the dependencies.json file as valid JSON')
        args_group_non_function_tests.add_argument(
            '--test-dependencies-schema-valid-json',
            action='store_true',
            help='validate the dependencies.schema.json file as valid JSON')
        args_group_non_function_tests.add_argument(
            '--test-dependencies-file-valid-for-schema',
            action='store_true',
            help='validate dependencies.json against the dependencies.schema.json file')

    def _run_non_specific_lamda_test_suite(self):
        if self.input_test_lambda_definitions:
            test_suite = TestSuiteLambdaDefinitions(
                dependencies_json_file_path=self.input_dependencies_json_file_path,
                bundle_json_file_path=self.input_bundle_json_file_path,
                output_xml=self.args.output_xml,
                mute=self.mute
            )
        elif self.input_test_dependencies_file_exists:
            test_suite = TestSuiteDependenciesFileExists(
                dependencies_json_file_path=self.input_dependencies_json_file_path,
                output_xml=self.args.output_xml,
                mute=self.mute
            )
        elif self.input_test_dependencies_schema_exists:
            test_suite = TestSuiteDependenciesSchemaExists(
                dependencies_json_file_path=self.input_dependencies_json_file_path,
                output_xml=self.args.output_xml,
                mute=self.mute
            )
        elif self.input_test_dependencies_file_valid_json:
            test_suite = TestSuiteDependenciesFileValidJson(
                dependencies_json_file_path=self.input_dependencies_json_file_path,
                output_xml=self.args.output_xml,
                mute=self.mute
            )
        elif self.input_test_dependencies_schema_valid_json:
            test_suite = TestSuiteDependenciesSchemaValidJson(
                dependencies_json_file_path=self.input_dependencies_json_file_path,
                output_xml=self.args.output_xml,
                mute=self.mute
            )
        elif self.input_test_dependencies_file_valid_for_schema:
            test_suite = TestSuiteDependenciesFileValidForSchema(
                dependencies_json_file_path=self.input_dependencies_json_file_path,
                output_xml=self.args.output_xml,
                mute=self.mute
            )
        else:
            raise ValueError('No non specific lamda test suite set to run')
        (self.test_suite_success, self.test_results) = test_suite.run()
        return self.test_suite_success


class TestSuite():
    ''' this is intended as a base class and not for direct instantiation '''

    test_suite_name = None
    test_suite_data = None
    test_results = {}

    function_definitions = None
    common_config = None
    global_dependencies = None
    test_suite_output_template = {
        'issues': {},
        'message': None,
        'status': None,
        'tests_run': 0,
        'tests_failed': 0,
        'tests_skipped': 0,
        'tests_successful': 0
    }

    dependencies_json_file_path = None
    bundle_json_file_path = None

    output_xml = False
    XML_OUTPUT_FOLDER_NAME = 'test-reports'

    mute = False

    def __init__(self, dependencies_json_file_path=DEPENDENCIES_CONFIG, bundle_json_file_path=None, output_xml=False, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.dependencies_json_file_path = dependencies_json_file_path if dependencies_json_file_path is not None else DEPENDENCIES_CONFIG
        self.bundle_json_file_path = bundle_json_file_path
        self.output_xml = output_xml
        self.mute_set(kwargs.get('mute', False))
        if self.mute:
            self.logger.setLevel(logging.ERROR)

        if self.output_xml:
            self.output_xml_folder_guarantee()

    def file_exists(self):
        # empty method that is overwritten in child classes
        pass

    def file_valid_json(self):
        # empty method that is overwritten in child classes
        pass

    def generate_tests_xml_output(self, test_suite_success, test_results, entity_name):
        ''' output xml that is detected as a test suite by bitbucket '''
        ct = datetime.datetime.now()
        # initial xml setup
        root = minidom.Document()
        xml = root.createElement('testsuites')
        root.appendChild(xml)

        if not len(test_results):
            if not self.mute:
                self.logger.info(f'No test results provided in input for {entity_name}')

        xml_str = ''

        for key, value in test_results.items():
            tests_count = int(value.get('message', '0')[0])
            if tests_count > 0:
                if not test_suite_success:
                    issues = value.get('issues', {})

                testSuite = root.createElement('testsuite')
                testSuite.setAttribute('errors', '0')
                failures = 0 if test_suite_success else len(issues)
                testSuite.setAttribute('failures', f'{failures}')
                testSuite.setAttribute('hostname', 'none')
                testSuite.setAttribute('name', f'{key}')
                testSuite.setAttribute('skipped', '0')
                testSuite.setAttribute('tests', f"{value.get('message', '0')[0]}")
                testSuite.setAttribute('time', '0')
                testSuite.setAttribute('timestamp', f'{ct}')

                xml.appendChild(testSuite)

                # failures - currently more actual data to output
                if not test_suite_success:
                    issues_count = 1
                    for test_name, test_data in issues.items():
                        testCase = root.createElement('testcase')
                        testCase.setAttribute('classname', entity_name)
                        testCase.setAttribute('file', f'{key}.py')
                        testCase.setAttribute('line', f'{issues_count}')
                        testCase.setAttribute('name', f'{test_name}')
                        testCase.setAttribute('time', '0')

                        failureEl = root.createElement('failure')
                        failureEl.setAttribute('message', f'{test_name} failed')
                        test_message = test_data.get('message', '')
                        if test_message == '':
                            test_message = 'No message returned by test failure'
                        failureElContent = root.createTextNode(f'{test_message}')
                        failureEl.appendChild(failureElContent)
                        testCase.appendChild(failureEl)

                        testSuite.appendChild(testCase)
                        issues_count += 1

                # successes
                for x in range(tests_count - failures):
                    testCase = root.createElement('testcase')
                    testCase.setAttribute('classname', entity_name)
                    testCase.setAttribute('file', f'{key}.py')
                    testCase.setAttribute('line', f'{failures+x+1}')
                    # currently generic due to data not available in return payload
                    testCase.setAttribute('name', 'successful-test-item')
                    testCase.setAttribute('time', '0')

                    testSuite.appendChild(testCase)

            xml_str = root.toprettyxml(indent='\t', encoding='utf-8')

            with open(f'{self.XML_OUTPUT_FOLDER_NAME}/{key}.xml', 'wb') as f:
                f.write(xml_str)

        return xml_str

    def mute_set(self, value):
        self.mute = value

    def output_xml_folder_guarantee(self):
        ''' If xml output folder doesn't exist create it '''

        if not os.path.isdir(self.XML_OUTPUT_FOLDER_NAME):
            os.makedirs(self.XML_OUTPUT_FOLDER_NAME)

    def parse_results(self, tests_to_parse):
        for item in tests_to_parse:
            if item is not None:
                (item['message'], item['status']) = self.test_results_prepare_output(item)

        failed_tests = [x for x in tests_to_parse if x['status'] == 'FAILURE']
        if len(failed_tests) == 0:
            test_successful = True
        else:
            test_successful = False

        return test_successful

    def run_tests(self):
        test_successful = None
        self.test_suite_data = self._test_suite_data_template_copy()

        self.test_perform()

        self.test_results[self.test_suite_name] = self.test_suite_data

        # parse results of all tests to assess success/failure
        tests_to_parse = [
            self.test_suite_data
        ]
        test_successful = self.parse_results(tests_to_parse)
        for item in tests_to_parse:
            if item is not None:
                (item['message'], item['status']) = self.test_results_prepare_output(item)

        if not self.mute:
            if test_successful:
                self.logger.warning('Test suite SUCCESS')
            else:
                self.logger.warning('Test suite FAILURE')

        return test_successful

    def test_file_exists(self):
        if self.test_suite_data is None:
            self.test_suite_data = self._test_suite_data_template_copy()
        self.test_suite_data['tests_run'] += 1
        file_exists = self.file_exists()
        if file_exists:
            self.test_suite_data['tests_successful'] += 1
            self.test_suite_success = True
        else:
            self.test_suite_data['tests_failed'] += 1
            self.test_suite_data['issues']['file_exists'] = {'message': 'FAILURE'}
            self.test_suite_success = False

        return self.test_suite_success

    def test_file_valid_json(self):
        if self.test_suite_data is None:
            self.test_suite_data = self._test_suite_data_template_copy()
        self.test_suite_data['tests_run'] += 1
        file_valid_json = self.file_valid_json()
        if file_valid_json:
            self.test_suite_data['tests_successful'] += 1
            self.test_suite_success = True
        else:
            self.test_suite_data['tests_failed'] += 1
            self.test_suite_data['issues']['file_exists'] = {'message': 'FAILURE'}
            self.test_suite_success = False

        return self.test_suite_success

    def test_perform(self):
        # empty method that is overwritten in child classes
        pass

    def test_results_message(self, test_results):
        message = ''
        if test_results['tests_run'] == 1:
            message = f'{test_results["tests_run"]} test run'
        else:
            message = f'{test_results["tests_run"]} tests run'
        if test_results['tests_skipped'] > 0:
            if test_results['tests_skipped'] == 1:
                message += f', {test_results["tests_skipped"]} test skipped'
            else:
                message += f', {test_results["tests_skipped"]} tests skipped'

        return message

    def test_results_prepare_output(self, test_results):
        message = self.test_results_message(test_results)
        status = self.test_results_status(test_results)
        return (message, status)

    def test_results_status(self, test_results):
        status = ''
        if test_results['tests_run'] == 0:
            status = 'NO TESTS'
        elif test_results['tests_failed'] > 0:
            status = 'FAILURE'
        else:
            status = 'SUCCESS'

        return status

    def test_suite_name_set(self, class_name):
        # parse test suite name and convert to kebab case for output usage
        self.test_suite_name = re.sub(r'(?<!^)(?=[A-Z])', '-', class_name).lower().replace('test-suite-', '')

    def _test_suite_data_template_copy(self):
        return deepcopy(self.test_suite_output_template)

    def _output_results(self):
        if len(self.test_results.keys()):
            self.logger.info('Results: {}'.format(json.dumps(self.test_results, indent=2)))
        else:
            self.logger.info('No results from tests')

    def _output_tests_xml(self, entity_name):
        try:
            self.generate_tests_xml_output(self.test_suite_success, self.test_results, entity_name)
        except Exception as e:
            if not self.mute:
                self.logger.error(f'Execution error when preparing XML output: {e}')
            raise e


class TestSuiteLambda(TestSuite):

    _lambda_bundle_name = None
    lambda_name = None
    payload = None
    region = None

    test_suite_success = True

    lambda_service_object = None

    def __init__(self, lambda_name, region='us-west-2', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_suite_name_set(__class__.__name__)

        self.lambda_name = lambda_name
        self.region = region

        self._bundle_json_file_path_set()

    def run(self, payload=None, file_name=None, user=None, client_id=None):
        if not self.mute:
            self.logger.info(f'Running {self.test_suite_name} test suite')
        return self._lambda_test(payload, file_name, user, client_id)

    def _authenticate_as_user(self, user, client_id):
        # authenticate as user if provided in input
        if not self.mute:
            self.logger.info(f'Authenticating as {user} with client ID {client_id}')

        try:
            CognitoAuthenticateObject = cognito.CognitoAuthenticate()
            token = cognito.authenticate(user, client_id)
            self._payload_add_token(token)
            if not self.mute:
                self.logger.error(f'Successfully authenticated as {user}')
        except CognitoAuthenticateObject.client.exceptions.NotAuthorizedException as e:
            if not self.mute:
                self.logger.error(f'User {user} not authorized: {e}')
                return False
            else:
                raise e
        except Exception as e:
            if not self.mute:
                self.logger.error(f'Unable to authenticate as {user}: {e}')
            raise e
        return True

    def _bundle_json_file_path_set(self):
        if self.bundle_json_file_path is None:
            self.bundle_json_file_path = f'lambda/{self._lambda_bundle}/bundle.json'

    @property
    def _lambda_bundle(self):
        if self._lambda_bundle_name is None:
            self._lambda_bundle_name = bundle.lambda_bundle_get(self.lambda_name, self.dependencies_json_file_path)
        return self._lambda_bundle_name

    @property
    def _LambdaServiceObject(self):
        if self.lambda_service_object is None:
            self.lambda_service_object = LambdaService(region=self.region)
        return self.lambda_service_object

    def _lambda_test(self, payload=None, file_name=None, user=None, client_id=None):
        if not self.mute:
            self.logger.info(f'Preparing to test lambda: {self.lambda_name}')

        self._lambda_tests_get()
        self._payload_load(payload, file_name)

        if None not in [user, client_id] and not self.mute:
            authenticated_successfullly = self._authenticate_as_user(user, client_id)
            if not authenticated_successfullly:
                return (None, self.test_results)

        self._tests_run()

        if self.output_xml:
            self._output_tests_xml()

        if not self.mute:
            self._output_results()

        return (self.test_suite_success, self.test_results)

    def _lambda_tests_get(self):
        # get test names
        try:
            self.lambda_tests = self._lambda_tests_names_get_from_bundle(self.lambda_name, self.bundle_json_file_path)
            if len(self.lambda_tests) == 0:
                if not self.mute:
                    self.logger.warning('No tests found, exiting')
                return (None, self.test_results)

            if not self.mute:
                self.logger.info(f'test names: {", ".join(self.lambda_tests)}')

        except Exception as e:
            if not self.mute:
                self.logger.error(f'Unable to get test names for {self.lambda_name}: {e}')
            raise e

    def _lambda_tests_names_get_from_bundle(self, lambda_name=None, bundle_json_file_path=None):
        if lambda_name is None:
            lambda_name = self.lambda_name
        if bundle_json_file_path is None:
            bundle_json_file_path = self.bundle_json_file_path
        lambda_bundle_name = self._lambda_bundle
        bundle_info = bundle.bundle_info_get(lambda_name, lambda_bundle_name, bundle_json_file_path, self.mute)

        return (
            bundle_info.get('lambdas', {}).get(lambda_name, {}).get('tests', [])
        )

    def _output_tests_xml(self):
        super()._output_tests_xml(self.lambda_name)

    def _payload_add_token(self, token):
        if self.payload.get('params', None) is None:
            self.payload['params'] = {}
        if self.payload['params'].get('header', None) is None:
            self.payload['params']['header'] = {}
        self.payload['params']['header']['Authorization'] = token

    def _payload_load(self, payload, file_name):
        # load payload from inline input or from file is no inline input
        try:
            if payload is not None:
                self.payload = payload
            else:
                with open(file_name) as f:
                    self.payload = json.load(f)
        except Exception as e:
            raise Exception('Unable to parse payload') from e

    def _tests_run(self):
        # loop and invoke tests
        try:
            count = 1
            for lambda_test_name in self.lambda_tests:
                if not self.mute:
                    self.logger.warning(f'Running Test Suite [{count}/{len(self.lambda_tests)}]: {lambda_test_name} ')

                result = self._LambdaServiceObject.client.invoke(
                    FunctionName=lambda_test_name,
                    InvocationType='RequestResponse',
                    Payload=json.dumps(self.payload)
                )
                response = json.loads(result['Payload'].read())
                if 'FunctionError' in result:
                    raise Exception(response['errorMessage'])

                if response.get('status', None).lower() != 'success':
                    self.test_suite_success = False
                self.test_results[lambda_test_name] = response
                count += 1
        except Exception as e:
            if not self.mute:
                self.logger.error(f'Execution error while running tests: {e}')
            raise e


class TestSuiteLambdaDefinitions(TestSuite):

    bundles = []
    bundles_bundle_json_failed = []

    test_results = {}
    test_suite_success = True

    bundle_json_file_exists = None
    bundle_json_file_valid_json = None
    bundle_json_contents_valid_for_schema = None
    test_bundle_json_contents_valid_failed = False

    dependencies_json_contents_valid_for_schema = None
    test_dependencies_json_contents_valid_failed = False

    dependencies_json_lambdas_common_dependencies_valid = None
    test_dependencies_json_lambdas_common_dependencies_valid_failed = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_suite_name_set(__class__.__name__)

    def run(self):
        '''
        test suite for use in awslambda repo pipeline
        usage: `--test-lambda-definitions` argument
        tests:
            - dependencies.json file for validity against schema
            - each bundle's bundle.json file for validity against schema
            - if each lambda's declared common_dependencies are valid common_dependencies
        '''

        if not self.mute:
            self.logger.info(f'Running {self.test_suite_name} test suite')

        (self.function_definitions, self.common_config, self.global_dependencies) = bundle.load_dependencies()
        self.bundles = bundle.bundles_list()

        # test each bundle's bundle.json existence and validity
        self._test_bundles_bundle_json()

        # check that all lambdas common dependencies are valid options listed in self.common_config
        self._test_dependencies_json_lambdas_common_dependencies_valid()

        if self.output_xml:
            self._output_tests_xml()

        if not self.mute:
            self._output_results()

        return (self.test_suite_success, self.test_results)

    def _output_tests_xml(self):
        super()._output_tests_xml('lambda-definitions')

    def _test_bundle_json_file_valid_json(self, bundle_name):
        try:
            # try to json-load each bundle's bundle.json, if fails not valid json
            self.bundle_json_file_exists['tests_run'] += 1
            bundle.json_load_bundle_json(bundle_name)
            # didn't raise exception - bundle's bundle.json file exists and is valid JSON
            self.bundle_json_file_valid_json['tests_run'] += 1
            self.bundle_json_file_exists['tests_successful'] += 1
            self.bundle_json_file_valid_json['tests_successful'] += 1

        except json.decoder.JSONDecodeError as e:
            # bundle's bundle.json file exists but is not valid JSON
            self.bundles_bundle_json_failed.append(bundle_name)
            self.logger.warning(f'Bundle {bundle_name} bundle.json file invalid JSON: {e}')
            self.test_suite_success = False
            self.bundle_json_file_valid_json['tests_run'] += 1
            self.bundle_json_file_exists['tests_successful'] += 1
            self.bundle_json_file_valid_json['tests_failed'] += 1
            self.bundle_json_file_valid_json['issues'][bundle_name] = {'message': 'FAILURE'}
            self.logger.warning(f'Test failed: bundle {bundle_name} bundle.json file exists but is not valid JSON')

        except Exception as e:
            # bundle's bundle.json file does not exist (valid JSON test skipped)
            self.bundles_bundle_json_failed.append(bundle_name)
            self.logger.warning(f'Bundle {bundle_name} bundle.json file not found: {e}')
            self.test_suite_success = False
            self.bundle_json_file_exists['tests_failed'] += 1
            self.bundle_json_file_exists['issues'][bundle_name] = {'message': 'FAILURE'}
            self.bundle_json_file_valid_json['tests_skipped'] += 1
            self.bundle_json_file_valid_json['issues'][bundle_name] = {'message': 'SKIPPED'}
            self.logger.warning(f'Test failed: bundle {bundle_name} bundle.json file does not exist')

    def _test_bundles_bundle_json(self):
        test_successful = None
        self.bundle_json_file_exists = self._test_suite_data_template_copy()
        self.bundle_json_file_valid_json = self._test_suite_data_template_copy()
        self.bundle_json_contents_valid_for_schema = self._test_suite_data_template_copy()

        self._test_bundles_bundle_json_files_valid_json()
        self._test_bundles_bundle_json_contents_valid_for_schema()

        # parse results of all bundle's bundle.json tests to assess success/failure
        tests_to_parse = [
            self.bundle_json_file_exists,
            self.bundle_json_file_valid_json,
            self.bundle_json_contents_valid_for_schema
        ]
        for item in tests_to_parse:
            if item is not None:
                (item['message'], item['status']) = self.test_results_prepare_output(item)

        if self.test_bundle_json_contents_valid_failed is False:
            test_successful = True
            if not self.mute:
                self.logger.info('Test suite SUCCESS: bundle.json file is valid')
        else:
            test_successful = False
            if not self.mute:
                self.logger.info('Test suite FAILURE: bundle.json file is invalid')

        return test_successful

    def _test_bundles_bundle_json_contents_valid_for_schema(self):
        bundle_json_schema = bundle.json_load_bundle_schema()
        for bundle_name in self.bundles:
            if bundle_name in self.bundles_bundle_json_failed:
                self.bundle_json_contents_valid_for_schema['tests_skipped'] += 1
                self.bundle_json_contents_valid_for_schema['issues'][bundle_name] = {'message': 'SKIPPED'}
            else:
                self._test_bundle_json_contents_valid_for_schema(bundle_json_schema, bundle_name)

        self.test_results['bundle_json_contents_valid_for_schema'] = self.bundle_json_contents_valid_for_schema

    def _test_bundles_bundle_json_files_valid_json(self):
        # test if each bundle's bundle.json exists and is valid
        for bundle_name in self.bundles:
            self._test_bundle_json_file_valid_json(bundle_name)

        self.test_results['bundle_json_file_exists'] = self.bundle_json_file_exists
        self.test_results['bundle_json_file_valid_json'] = self.bundle_json_file_valid_json

    def _test_bundle_json_contents_valid_for_schema(self, bundle_json_schema, bundle_name):
        self.bundle_json_contents_valid_for_schema['tests_run'] += 1
        bundle_json = bundle.json_load_bundle_json(bundle_name)
        try:
            jsonschema.validate(instance=bundle_json, schema=bundle_json_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.test_suite_success = False
            self.bundle_json_contents_valid_for_schema['tests_failed'] += 1
            self.bundle_json_contents_valid_for_schema['issues'][bundle_name] = {'message': 'FAILURE'}
            self.logger.warning(f'{bundle_name} bundle.json is invalid JSON: {e}')
            return False

        self.bundle_json_contents_valid_for_schema['tests_successful'] += 1
        return True

    def _test_dependencies_json_lambdas_common_dependencies_valid(self):
        ''' validate that all lambdas common dependencies are options listed in self.common_config '''

        test_successful = None
        self.dependencies_json_lambdas_common_dependencies_valid = False
        self.dependencies_json_lambdas_common_dependencies_valid = self._test_suite_data_template_copy()

        self.dependencies_json_lambdas_common_dependencies_valid['tests_run'] += 1

        for lambda_name, lambda_definition in self.function_definitions.items():
            lambda_definition_common_dependencies = lambda_definition.get('common_dependencies', None)
            if lambda_definition_common_dependencies is None:
                continue
            for lambda_definition_common_dependency in lambda_definition_common_dependencies:
                if lambda_definition_common_dependency in self.common_config:
                    continue
                # lambda_definition_common_dependency not valid
                self.logger.warning(f'FAIL: {lambda_name} dependencies.json definition is using an invalid common dependency')
                if test_successful is None:
                    self.test_suite_success = False
                    self.test_dependencies_json_lambdas_common_dependencies_valid_failed = True
                    self.dependencies_json_lambdas_common_dependencies_valid['tests_failed'] += 1
                    self.dependencies_json_lambdas_common_dependencies_valid['issues'][lambda_name] = {'message': f'FAILURE: {lambda_definition_common_dependency} is not a valid common_dependency'}
                    test_successful = False

        # parse results of tests to assess success/failure
        for item in [self.dependencies_json_lambdas_common_dependencies_valid]:
            if item is not None:
                (item['message'], item['status']) = self.test_results_prepare_output(item)

        self.test_results['dependencies_json_lambdas_common_dependencies_valid'] = self.dependencies_json_lambdas_common_dependencies_valid

        if test_successful is not False:
            self.dependencies_json_lambdas_common_dependencies_valid['tests_successful'] += 1
            test_successful = True
            if not self.mute:
                self.logger.info('Test suite SUCCESS: dependencies.json lambda definition common dependencies are valid')
        else:
            if not self.mute:
                self.logger.info('Test suite FAILURE: dependencies.json lambda definition common dependencies are not valid')

        return test_successful


class TestSuiteDependencies(TestSuite):

    test_results = {}
    test_suite_success = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self):
        if not self.mute:
            self.logger.warning(f'Running {self.test_suite_name} test suite')
        self.run_tests()
        if self.output_xml:
            self._output_tests_xml()

        if not self.mute:
            self._output_results()

        return (self.test_suite_success, self.test_results)

    def _file_exists(self, file_loader_func):
        # try to json-load file
        try:
            file_loader_func()
            return True
        except json.decoder.JSONDecodeError:
            # file exists but is not valid JSON
            return True
        except Exception:
            # file does not exist
            return False

    def _file_valid_json(self, file_loader_func):
        # try to json-load file
        try:
            file_loader_func()
            return True
        except json.decoder.JSONDecodeError:
            # file exists but is not valid JSON
            return False
        except Exception as e:
            # file does not exist
            raise e

    def _output_tests_xml(self):
        super()._output_tests_xml(self.test_suite_name)


class TestSuiteDependenciesFile(TestSuiteDependencies):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def file_exists(self):
        return super()._file_exists(bundle.json_load_dependencies)

    def file_valid_json(self):
        return super()._file_valid_json(bundle.json_load_dependencies)


class TestSuiteDependenciesSchema(TestSuiteDependencies):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def file_exists(self):
        return super()._file_exists(bundle.json_load_dependencies_schema)

    def file_valid_json(self):
        return super()._file_valid_json(bundle.json_load_dependencies_schema)


class TestSuiteDependenciesFileExists(TestSuiteDependenciesFile):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_suite_name_set(__class__.__name__)

    def test_perform(self):
        return self.test_file_exists()


class TestSuiteDependenciesSchemaExists(TestSuiteDependenciesSchema):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_suite_name_set(__class__.__name__)

    def test_perform(self):
        return self.test_file_exists()


class TestSuiteDependenciesFileValidJson(TestSuiteDependenciesFile):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_suite_name_set(__class__.__name__)

    def test_perform(self):
        return self.test_file_valid_json()


class TestSuiteDependenciesSchemaValidJson(TestSuiteDependenciesSchema):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_suite_name_set(__class__.__name__)

    def test_perform(self):
        return self.test_file_valid_json()


class TestSuiteDependenciesFileValidForSchema(TestSuiteDependenciesFile):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_suite_name_set(__class__.__name__)

    def _test_file_valid_for_schema(self):
        ''' test dependencies.json contents validity against schema '''

        if self.test_suite_data is None:
            self.test_suite_data = self._test_suite_data_template_copy()

        self.test_suite_data['tests_run'] += 1

        dependencies_json = bundle.json_load_dependencies()
        dependencies_json_schema = bundle.json_load_dependencies_schema()

        try:
            jsonschema.validate(instance=dependencies_json, schema=dependencies_json_schema)
            self.test_suite_data['tests_successful'] += 1
            self.test_suite_success = True
        except jsonschema.exceptions.ValidationError as e:
            self.test_suite_success = False
            self.test_suite_data['tests_failed'] += 1
            self.test_suite_data['issues']['file_valid_for_schema'] = {'message': f'FAILURE: {e}'}
            if not self.mute:
                self.logger.warning(f'File not valid for schema: {e}')

        return self.test_suite_success

    def test_perform(self):
        return self._test_file_valid_for_schema()
