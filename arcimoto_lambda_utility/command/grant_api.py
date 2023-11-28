import logging

from .command import AbstractCommand

from arcimoto_aws_services.lambda_service import (
    DEFAULT_AWS_REGION,
    LambdaApiGatewayService
)

'''
{
    "Sid": "94b5ccc4-d76a-4de3-8eec-1acb049d3bcc",
    "Effect": "Allow",
    "Principal": {
        "Service": "apigateway.amazonaws.com"
    },
    "Action": "lambda:InvokeFunction",
    "Resource": "arn:aws:lambda:us-west-2:511596272857:function:users_group_get:dev",
    "Condition": {
        "ArnLike": {
            "AWS:SourceArn": "arn:aws:execute-api:us-west-2:511596272857:fq1v0dj83b/*/GET/v1/groups/*"
        }
    }
}

arn:aws:execute-api:region:account-id:api-id/stage-name/HTTP-VERB/resource-path-specifier
'''

ACTION = 'lambda:InvokeFunction'
PRINCIPAL = 'apigateway.amazonaws.com'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(AbstractCommand):

    _LambdaApiGatewayServiceObject = None
    account_id = None
    arg_parser = None
    dry_run = False
    env = None
    function_name = None
    lambda_service_object = None
    mute = False
    _region = None
    verbose = False

    def __init__(self, arg_parser, **kwargs):
        super().__init__(arg_parser)
        self.arg_parser = arg_parser
        self.mute = kwargs.get('mute', False)

        self._parser_add_arguments()

    @property
    def region(self):
        if self._region is None:
            self._region = DEFAULT_AWS_REGION
        return self._region

    @region.setter
    def region(self, value):
        self._region = value

    def run(self, args, mute=False):
        super().__init__(args)
        self._parse_arguments(args, mute)

        if self.mute:
            self.logger.setLevel(logging.ERROR)
        else:
            self.logger.warning(f'Running grant_api for {args.function_name}:{args.env}')

        lambda_arn = self._LambdaApiGatewayServiceObject.lambda_arn_build(
            args.region,
            args.account_id,
            args.function_name,
            args.env
        )
        api_arn = self._LambdaApiGatewayServiceObject.api_arn_build(
            args.region,
            args.account_id,
            args.api_id,
            args.request_path
        )

        if not self.mute and args.verbose:
            self.logger.info(f'Constructed Lambda ARN: {lambda_arn}')
            self.logger.info(f'Constructed API Gateway ARN: {api_arn}')

        try:
            if not self._policy_exists(lambda_arn, api_arn):
                if not self.mute:
                    self.logger.warning('Policy does not exist')
                self._policy_deploy(lambda_arn, api_arn)
                return True
            else:
                if not self.mute:
                    self.logger.warning('Policy already exists, skipping deployment')
                return False
        except Exception as e:
            if not self.mute:
                self.logger.error(f'ERROR: {e}')
            raise e

    @property
    def _LambdaApiGatewayServiceObject(self):
        if self.lambda_service_object is None:
            self.lambda_service_object = LambdaApiGatewayService(region=self.region)
        return self.lambda_service_object

    def _parse_arguments(self, args, mute=False):
        if not mute:
            self.logger.debug('Parsing arguments...')

        required_args = [
            'account_id',
            'dry_run',
            'env',
            'function_name',
            'region',
            'verbose'
        ]

        for required_arg in required_args:
            if getattr(args, required_arg) is None:
                raise ValueError(f'Input args `{required_arg}` must not be `None`.')

        self.account_id = args.account_id
        self.dry_run = args.dry_run
        self.env = args.env
        self.function_name = args.function_name
        self.mute = mute
        self.region = args.region
        self.verbose = args.verbose

    def _parser_add_arguments(self):
        self.arg_parser.add_argument(
            'function_name',
            help='the name of the lambda function to allow'
        )

        self.arg_parser.add_argument(
            '-a',
            '--api-id',
            required=True,
            help='the ID of the API to allow'
        )
        self.arg_parser.add_argument(
            '-p',
            '--request-path',
            required=True,
            help='the request method and path to allow'
        )
        self.arg_parser.add_argument(
            '-e', '--env',
            help='environment to use',
            choices=['dev', 'staging', 'prod'],
            default='dev'
        )

    def _policy_deploy(self, lambda_arn, api_arn):
        if self.dry_run:
            if not self.mute:
                self.logger.warning('Dry Run: skipping AWS policy deployment')
            return False

        return self._LambdaApiGatewayServiceObject.policy_deploy(
            lambda_arn=lambda_arn,
            api_arn=api_arn,
            verbose=self.verbose,
            mute=self.mute
        )

    def _policy_exists(self, lambda_arn, api_arn):
        return self._LambdaApiGatewayServiceObject.policy_exists(
            lambda_arn=lambda_arn,
            api_arn=api_arn,
            verbose=self.verbose,
            mute=self.mute
        )
