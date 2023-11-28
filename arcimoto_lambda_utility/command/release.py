import logging
from time import sleep

from .command import AbstractCommand

from arcimoto_aws_services.lambda_service import (
    LambdaService,
    STAGING_ALIAS,
    PROD_ALIAS
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(AbstractCommand):

    arg_parser = None
    args = None
    env = None
    function_name = None
    lambda_service_object = None
    mute = False
    region = None

    def __init__(self, arg_parser):
        super().__init__(arg_parser)
        self.arg_parser = arg_parser
        self._parser_add_arguments()

    def run(self, args, mute=False):
        super().run(args)
        if mute:
            self.logger.setLevel(logging.ERROR)

        self._parse_arguments(args, mute)

        if not self.mute:
            self.logger.warning('Preparing release...')

        return self._release()

    @property
    def _LambdaServiceObject(self):
        if self.lambda_service_object is None:
            self.lambda_service_object = LambdaService(region=self.region)
        return self.lambda_service_object

    def _lambda_alias_latest_version_get(self, alias_name):
        return self._LambdaServiceObject.lambda_alias_latest_version_get(
            function_name=self.function_name,
            alias=alias_name,
            mute=self.mute,
            verbose=self.args.verbose
        )

    def _lambda_alias_upsert(self, alias_name, version):
        return self._LambdaServiceObject.lambda_alias_upsert(
            function_name=self.function_name,
            alias=alias_name,
            version=version,
            description=self.args.description,
            mute=self.mute,
            verbose=self.args.verbose
        )

    def _lambda_publish_version(self):
        return self._LambdaServiceObject.lambda_publish_version(
            function_name=self.function_name,
            region=self.region,
            mute=self.mute,
            verbose=self.args.verbose
        )

    def _parse_arguments(self, args, mute):
        if args.env not in [STAGING_ALIAS, PROD_ALIAS]:
            raise KeyError(f'Invalid input env: {args.env}')

        self.args = args
        self.env = args.env
        self.function_name = args.function_name
        self.region = args.region
        self.mute = mute

    def _parser_add_arguments(self):
        self.arg_parser.add_argument(
            'function_name',
            help='the name of the function to release'
        )
        self.arg_parser.add_argument(
            'env',
            choices={STAGING_ALIAS, PROD_ALIAS},
            help='target release environment'
        )
        self.arg_parser.add_argument(
            '--description',
            help='reason for release',
            default='Managed release'
        )

    def _release(self):
        release_success = None

        if self.env == PROD_ALIAS:
            release_success = self._release_prod()
        else:
            release_success = self._release_staging()

        if not self.mute:
            if release_success:
                self.logger.warning(f'Released function {self.function_name} to {self.env}')
            else:
                self.logger.warning(f'Failed to release function {self.function_name} to {self.env}')

        return release_success

    def _release_prod(self):
        # get the version of the current staging alias
        try:
            version = self._lambda_alias_latest_version_get(STAGING_ALIAS)
        except self._LambdaServiceObject.exceptions.TooManyRequestsException as e:
            self.logger.warning(f'Too Many Requests Exception from _lambda_alias_latest_version_get: {e}')
            # wait and try again if too many requests
            sleep(5)
            self._release_prod()

        if not version:
            if not self.mute:
                self.logger.error(f'Unable to get latest {STAGING_ALIAS} version')
            return False

        return self._lambda_alias_upsert(PROD_ALIAS, version)

    def _release_staging(self):
        # always create a new version when cutting a staging release
        version = self._lambda_publish_version()
        if not version:
            if not self.mute:
                self.logger.error(f'Unable to publish {self.function_name} version')
            return False

        return self._lambda_alias_upsert(STAGING_ALIAS, version)
