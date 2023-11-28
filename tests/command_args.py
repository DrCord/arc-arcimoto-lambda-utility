import uuid

from arcimoto_aws_services.path import DEPENDENCIES_CONFIG

from arcimoto_aws_services.lambda_service import (
    PYTHON3_MINOR_VERSION_DEFAULT,
    STAGING_ALIAS,
    LambdaApiGatewayArgs,
    LambdaArgs,
    LambdaCreateArgs,
    LambdaInvokeArgs,
    LambdaLayersArgs,
    LambdaTestArgs
)

from tests.command.invoke.invoke import TestInvoke


DEFAULT_TEST_API_ID = 'bewsuj10p2'
DEFAULT_TEST_API_PATH = 'GET/v1/vehicles'

DEFAULT_TEST_LAMBDA_ENV = 'dev'
DEFAULT_TEST_LAMBDA_DESCRIPTION = 'arcimoto-lambda-utility: unit tests created'
DEFAULT_TEST_LAMBDA_LAYER_NAME = 'package1'
DEFAULT_TEST_LAMBDA_NAME = 'alu_unit_test'
DEFAULT_TEST_LAMBDA_ROLE_NAME = 'lambda.unit_test.arcimoto_lambda_utility'


class CommandArgs(LambdaArgs):
    ''' Used to pass into run command as mock CLI arguments '''

    description = None
    env = None
    function = None
    mute = True
    role = None

    def __init__(self, lambda_name=DEFAULT_TEST_LAMBDA_NAME, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # automatically set attributes to defaults for tests
        self.function_name_set(lambda_name)
        self.env_set()
        self.mute_set()

    def description_set(self, description='created by unit test'):
        self.description = description

    def env_set(self, env=DEFAULT_TEST_LAMBDA_ENV):
        self.env = env

    def function_name_set(self, function_name=DEFAULT_TEST_LAMBDA_NAME):
        self.function = function_name
        if function_name == DEFAULT_TEST_LAMBDA_NAME:
            self.function += f'_{str(uuid.uuid4())}'

    def mute_set(self, mute=True):
        self.mute = mute

    def role_set(self, role=DEFAULT_TEST_LAMBDA_ROLE_NAME):
        self.role = role


class CreateCommandArgs(CommandArgs, LambdaCreateArgs):
    ''' Used to pass into run command as mock CLI arguments '''

    role = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # automatically set attributes to defaults for tests
        self.description_set()
        self.role_set()


class GrantApiCommandArgs(CommandArgs, LambdaApiGatewayArgs):
    ''' Used to pass into run command as mock CLI arguments '''

    api_id = None
    request_path = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # automatically set attributes to defaults for tests
        self.api_id_set()
        self.request_path_set()
        self.role_set()

    def api_id_set(self, api_id=DEFAULT_TEST_API_ID):
        self.api_id = api_id

    def request_path_set(self, request_path=DEFAULT_TEST_API_PATH):
        self.request_path = request_path


class InvokeCommandArgs(CommandArgs, LambdaInvokeArgs, TestInvoke):
    ''' Used to pass into run command as mock CLI arguments '''

    client_id = None
    args = None
    file_name = None
    payload = None
    user = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # automatically set attributes to defaults for tests
        self.client_id_set()
        self.payload_set()
        self.role_set()

    def client_id_set(self):
        self.client_id = self.cognito_client_id

    def file_name_set(self, file_name='lambda/tests/payload.json'):
        self.file_name = file_name

    def payload_set(self, payload={}):
        self.payload = payload

    def role_set(self, value=DEFAULT_TEST_LAMBDA_ROLE_NAME):
        self.role = value


class LayerCommandArgs(CommandArgs, LambdaLayersArgs):
    ''' Used to pass into run command as mock CLI arguments '''

    layer = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._layer_set()

    def _layer_set(self, value=DEFAULT_TEST_LAMBDA_LAYER_NAME):
        self.layer = value


class ListCommandArgs(CommandArgs):
    ''' Used to pass into run command as mock CLI arguments '''

    bundle = None
    common_config = None
    exclude_tests = None
    global_dependencies = None
    include_filepath = None
    tests_only = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ReleaseCommandArgs(CommandArgs):
    ''' Used to pass into run command as mock CLI arguments '''

    env = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.env_set()
        self.function_name_set()
        self.role_set()
        self.description_set()

    def env_set(self, value=STAGING_ALIAS):
        return super().env_set(value)

    def function_name_set(self, value=DEFAULT_TEST_LAMBDA_NAME):
        return super().function_name_set(value)


class RuntimeCommandArgs(CommandArgs):
    ''' Used to pass into run command as mock CLI arguments '''

    python3_minor_version = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.python3_minor_version_set()
        self.function_name_set()
        self.role_set()
        self.description_set()

    def python3_minor_version_set(self, value=PYTHON3_MINOR_VERSION_DEFAULT):
        self.python3_minor_version = value

    def function_name_set(self, value=DEFAULT_TEST_LAMBDA_NAME):
        return super().function_name_set(value)


class TestCommandArgs(CommandArgs, LambdaTestArgs):
    ''' Used to pass into run command as mock CLI arguments '''

    test_lambda_definitions = None
    test_dependencies_file_exists = None
    test_dependencies_schema_exists = None
    test_dependencies_file_valid_json = None
    test_dependencies_schema_valid_json = None
    test_dependencies_file_valid_for_schema = None

    dependencies_json_file_path = None
    bundle_json_file_path = None

    output_xml = False

    payload = None
    file_name = None
    user = None
    client_id = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.function_name_set()
        self.role_set()
        self.description_set()
        self.payload_set()
        self.client_id_set()

    def client_id_set(self):
        self.client_id = self.cognito_client_id

    def dependencies_json_file_path_set(self, value=DEPENDENCIES_CONFIG):
        self.dependencies_json_file_path = value

    def function_name_set(self, value=DEFAULT_TEST_LAMBDA_NAME):
        return super().function_name_set(value)

    def output_xml_set(self, value):
        self.output_xml = value

    def payload_set(self, value={}):
        self.payload = value


class TestIndividualLambdaCommandArgs(TestCommandArgs):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TestNonIndividualLambdaCommandArgs(TestCommandArgs):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.function_name = 'None'


class UpdateCommandArgs(CommandArgs):
    ''' Used to pass into run command as mock CLI arguments '''

    python3_minor_version = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.function_name_set()
        self.role_set()
        self.description_set()

    def function_name_set(self, value=DEFAULT_TEST_LAMBDA_NAME):
        return super().function_name_set(value)
