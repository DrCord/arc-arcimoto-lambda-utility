import json
import logging

from .command import AbstractCommand

from arcimoto_aws_services import cognito
from arcimoto_aws_services.cognito import CognitoAuthenticate
from arcimoto_aws_services.lambda_service import (
    ALIASES,
    DEV_ALIAS,
    LambdaService
)


class Command(AbstractCommand):

    arg_parser = None
    args = None
    env = None
    file_name = None
    lambda_service_object = None
    mute = False
    payload = None
    region = None
    token = None

    def __init__(self, arg_parser):
        super().__init__(arg_parser)
        self.arg_parser = arg_parser
        self._parser_add_arguments()

    def run(self, args, mute=False):
        super().run(args)
        if self.mute:
            self.logger.setLevel(logging.ERROR)
        self._parse_arguments(args, mute)
        if self.args.user is not None:
            self._cognito_authenticate()
            self._payload_set_authorization_header()
        self._lambda_invoke()
        return True

    @property
    def _LambdaServiceObject(self):
        if self.lambda_service_object is None:
            self.lambda_service_object = LambdaService(region=self.region)
        return self.lambda_service_object

    def _cognito_authenticate(self):
        if not self.mute:
            self.logger.info(f'Authenticating with client ID {self.args.client_id}')
        try:
            # authenticate using unit test credentials if requested and available
            if hasattr(self.args, 'username') and \
                    hasattr(self.args, 'password') and \
                    isinstance(self.args.user, str) and \
                    isinstance(self.args.password, str):
                CognitoAuthenticateObject = CognitoAuthenticate(self.args.client_id)
                self.token = CognitoAuthenticateObject.authenticate_non_interactive(self.args.user, self.args.password)
            else:  # authenticate normally with the user inputting a password at the CLI
                if self.args.user is None:
                    raise ValueError('Unable to authenticate with Cognito: input `user` null')
                if not self.mute:
                    self.logger.info(f'Authenticating with user {self.args.user}')
                self.token = cognito.authenticate(self.args.user, self.args.client_id)
        except Exception as e:
            if not self.mute:
                self.logger.error(f'Execution error: {e}')
            raise e

    def _lambda_invoke(self):
        if not self.mute:
            self.logger.info(f'Invoking lambda {self.function_name}:{self.env} with payload:\n{json.dumps(self.payload)}\n')
        return self._LambdaServiceObject.invoke(
            function_name=self.function_name,
            env=self.env,
            payload=self.payload,
            mute=self.mute
        )

    def _parse_arguments(self, args, mute):
        self.args = args
        self.env = args.env
        self.file_name = args.file_name if hasattr(args, 'file_name') else None
        self.function_name = args.function_name
        self.region = args.region
        self.mute = mute
        self._payload_get()

    def _parser_add_arguments(self):
        self.arg_parser.add_argument(
            'function_name',
            help='the name of the lambda to invoke'
        )
        self.arg_parser.add_argument(
            '--user',
            default=None,
            help='authenticate as a specific user before invoking'
        )
        self.arg_parser.add_argument(
            '--env',
            choices=ALIASES,
            default=DEV_ALIAS,
            help='specify which environment to use'
        )
        self.arg_parser.add_argument(
            '--client-id',
            default=cognito.DEFAULT_CLIENT_ID,
            help='specify which user pool to use for authentication'
        )

        argument_group_payload_source = self.arg_parser.add_mutually_exclusive_group(required=True)
        argument_group_payload_source.add_argument(
            '--payload',
            type=json.loads,
            help='the payload to pass as data to the lambda'
        )
        argument_group_payload_source.add_argument(
            '--file-name',
            help='name of a json file to use as payload data'
        )

    def _payload_get(self):
        self.payload = self.args.payload
        if self.payload is None:
            self._payload_load_from_source_file()
        if not isinstance(self.payload, dict):
            raise TypeError('Input payload must be a dictionary')

    def _payload_load_from_source_file(self):
        try:
            with open(self.file_name) as f:
                self.payload = json.load(f)
        except FileNotFoundError as e:
            if not self.mute:
                self.logger.error(f'File not Found - unable to load payload from input file-name `{self.args.file_name}`: {e}')
            raise e
        except json.decoder.JSONDecodeError as e:
            if not self.mute:
                self.logger.error(f'Invalid JSON - unable to load payload from input file-name `{self.args.file_name}`: {e}')
            raise e
        except Exception as e:
            if not self.mute:
                self.logger.error(f'Unable to load payload from file-name `{self.args.file_name}`: {e}')
            raise e

    def _payload_set_authorization_header(self):
        if not isinstance(self.token, str):
            raise ValueError(f'Unable to set payload Authorization header without valid token: {self.token}')

        if self.payload is None:
            self.payload = {}
        # don't overwrite any existing payload params/headers
        # build what strcuture is needed and only set the header Authorization token explicitly
        if self.payload.get('params', None) is None:
            self.payload['params'] = {}
        if self.payload['params'].get('header', None) is None:
            self.payload['params']['header'] = {}
        self.payload['params']['header']['Authorization'] = self.token
