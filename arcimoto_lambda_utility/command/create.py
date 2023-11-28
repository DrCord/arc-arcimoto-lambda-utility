import argparse
import logging
from .command import AbstractCommand

from arcimoto_aws_services.lambda_service import (
    LAMBDA_ALLOWED_VPCS,
    LAMBDA_DEFAULT_TIMEOUT,
    LAMBDA_DEFAULT_VPC,
    LambdaService,
    PYTHON3_ALLOWED_MINOR_VERSIONS,
    PYTHON3_MINOR_VERSION_DEFAULT
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(AbstractCommand):

    # from input args
    account_id = None
    description = None
    dry_run = None
    function_name = None
    python3_minor_version = None
    region = None
    role = None
    tags = {}
    timeout = None
    verbose = None
    vpc = None

    arg_parser = None
    LambdaServiceObject = None
    mute = False
    zip_bytes = None

    def __init__(self, arg_parser):
        super().__init__(arg_parser)
        self.arg_parser = arg_parser
        self._parser_add_arguments()
        self.LambdaServiceObject = LambdaService()

    def run(self, args, mute=False):
        super().run(args)
        self._parse_arguments(args, mute)
        self.mute = mute
        if self.mute:
            self.logger.setLevel(logging.ERROR)
            self.LambdaServiceObject = LambdaService(
                verbose=not self.mute
            )

        self.logger.info(f"Preparing to Create lambda '{self.function_name}'...")

        self._archive_create(
            function_name=self.function_name,
            mute=self.mute
        )

        if self.dry_run:
            self.logger.info('Dry Run: Skipping AWS Lambda interactions (create, create alias, add layers)')
            return None

        arn = self._lambda_create(
            zip_bytes=self.LambdaServiceObject.zip_bytes
        )
        # if arn is None then create was unsuccessful, bail out
        if arn is None:
            self.logger.warning('Lambda create unsuccessful, quiting')
            return None

        self._lambda_dev_alias_create(
            verbose=self.verbose,
            mute=self.mute
        )
        self._lambda_add_layers(
            function_name=self.function_name,
            verbose=self.verbose,
            mute=self.mute
        )

        self.logger.info(f"Complete: lambda '{self.function_name}' creation and initial set up finished")

        return True

    def _archive_create(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)

        return self.LambdaServiceObject.archive_create(
            function_name=self.function_name,
            mute=self.mute
        )

    def _lambda_add_layers(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)

        return self.LambdaServiceObject.add_layers(
            function_name=self.function_name,
            verbose=self.verbose,
            mute=self.mute
        )

    def _lambda_create(self, **kwargs):

        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)

        return self.LambdaServiceObject.create(
            function_name=self.function_name,
            description=self.description,
            zip_bytes=self.zip_bytes,
            role=self.role,
            vpc=self.vpc,
            tags=self.tags,
            timeout=self.timeout,
            python3_minor_verion=self.python3_minor_version,
            verbose=self.verbose,
            mute=self.mute
        )

    def _lambda_dev_alias_create(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)

        # input validation
        if not isinstance(self.function_name, str):
            raise ValueError(f'Invalid input function_name `{self.function_name}`, must be a string.')

        if self.verbose is not None and not isinstance(self.verbose, bool):
            raise ValueError(f'Invalid input verbose `{self.verbose}`, must be a Boolean.')

        if not isinstance(self.mute, bool):
            raise ValueError(f'Invalid input mute `{self.mute}`, must be a Boolean.')

        return self.LambdaServiceObject.lambda_dev_alias_create(
            function_name=self.function_name,
            verbose=self.verbose,
            mute=self.mute
        )

    def _parser_add_arguments(self):
        self.arg_parser.add_argument(
            'function',
            help='the name of the function to create'
        )

        self.arg_parser.add_argument(
            '--description',
            default=argparse.SUPPRESS,
            required=True,
            help='description of the lambda'
        )
        self.arg_parser.add_argument(
            '--python3-minor-version',
            choices=PYTHON3_ALLOWED_MINOR_VERSIONS,
            default=PYTHON3_MINOR_VERSION_DEFAULT,
            help='specify which python3 runtime to use'
        )
        self.arg_parser.add_argument(
            '--role',
            default=argparse.SUPPRESS,
            required=True,
            help='lambda execution role'
        )
        self.arg_parser.add_argument(
            '--tag',
            default=[],
            action='append',
            help='tag to apply to the lambda'
        )
        self.arg_parser.add_argument(
            '--timeout',
            default=LAMBDA_DEFAULT_TIMEOUT,
            type=int,
            help='execution timeout in seconds'
        )
        self.arg_parser.add_argument(
            '--vpc',
            choices=LAMBDA_ALLOWED_VPCS,
            default=LAMBDA_DEFAULT_VPC,
            help='which VPC to attach to'
        )

    def _parse_arguments(self, args, mute=False):
        if not mute:
            self.logger.debug('Parsing arguments...')

        required_args = [
            'account_id',
            'description',
            'dry_run',
            'function',
            'python3_minor_version',
            'region',
            'role',
            'tag',
            'timeout',
            'verbose',
            'vpc'
        ]

        for required_arg in required_args:
            if getattr(args, required_arg) is None:
                raise ValueError(f'Input args `{required_arg}` must not be `None`.')

        self.account_id = args.account_id
        self.description = args.description
        self.dry_run = args.dry_run
        # input arg `function` becomes attribute `function_name`
        self.function_name = args.function
        self.python3_minor_version = args.python3_minor_version
        self.region = args.region
        self.role = args.role
        self.timeout = args.timeout
        self.verbose = args.verbose
        self.vpc = args.vpc

        self._tags_parse(args.tag)

    def _tags_parse(self, tags):
        for tag in tags:
            self.tags[tag] = ''
        return self.tags
