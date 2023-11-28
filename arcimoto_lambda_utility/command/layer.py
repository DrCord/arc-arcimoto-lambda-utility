import logging

from .command import AbstractCommand

from arcimoto_aws_services.lambda_service import (
    LAMBDA_LAYERS_COMPATIBLE_RUNTIMES,
    LambdaLayersService,
    LICENSE_DEFAULT
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(AbstractCommand):

    arg_parser = None
    args = None
    arn = None
    lambda_service_object = None
    layer_config = None
    layers_config = None
    layer_description = None
    layer_identifier = None
    layer_packages = None
    mute = False
    region = False
    zip_bytes = None

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
            self.logger.info(f'Preparing to publish layer `{self.layer_identifier}` version...')

        if self.args.dry_run:
            if not self.mute:
                self.logger.info('Dry Run: skipping AWS layer publishing')
            return False

        return self._layer_publish_version(self.args.description)

    @property
    def _LambdaServiceObject(self):
        if self.lambda_service_object is None:
            self.lambda_service_object = LambdaLayersService(self.layer_identifier, region=self.region)
        return self.lambda_service_object

    def _layer_publish_version(self, description, **kwargs):
        if isinstance(kwargs.get('layer_identifier', None), str):
            self.lambda_service_object = LambdaLayersService(kwargs.get('layer_identifier'))

        if not self.mute and self.args.verbose:
            self.logger.info(f'Publishing layer `{self.layer_identifier}` version to AWS')

        return self._LambdaServiceObject.publish_layer_version(
            description=description,
            mute=self.mute
        )

    def _parse_arguments(self, args, mute):
        if not mute and self.args.verbose:
            self.logger.info('Parsing arguments')
        self.args = args
        self.layer_identifier = self.args.layer
        self.region = self.args.region
        self.mute = mute

    def _parser_add_arguments(self):
        self.arg_parser.add_argument(
            'layer',
            help='the name of the layer to create/update'
        )

        self.arg_parser.add_argument(
            '--description',
            default='created using the arcimoto-lambda-utility layer command',
            help='description of the layer'
        )
        self.arg_parser.add_argument(
            '--compatible_runtimes',
            default=LAMBDA_LAYERS_COMPATIBLE_RUNTIMES,
            action='append',
            help='python3 compatible runtimes, e.g. python3.x'
        )
        self.arg_parser.add_argument(
            '--license_info',
            default=LICENSE_DEFAULT,
            type=str,
            help='license name or info'
        )
