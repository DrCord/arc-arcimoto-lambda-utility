import logging

from .command import AbstractCommand

from arcimoto_aws_services.lambda_service import LambdaService


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(AbstractCommand):

    arg_parser = None
    args = None
    function_name = None
    lambda_service_object = None
    mute = None
    python3_minor_version = None
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
        self._lambda_runtime_set()

    @property
    def _LambdaServiceObject(self):
        if self.lambda_service_object is None:
            self.lambda_service_object = LambdaService(region=self.region)
        return self.lambda_service_object

    def _lambda_runtime_set(self):
        return self._LambdaServiceObject.lambda_runtime_set(
            function_name=self.function_name,
            python3_minor_version=self.python3_minor_version,
            mute=self.mute,
            verbose=self.args.verbose
        )

    def _parse_arguments(self, args, mute):
        self.args = args
        self.function_name = args.function_name
        self.python3_minor_version = args.python3_minor_version
        self.region = args.region
        self.mute = mute

    def _parser_add_arguments(self):
        self.arg_parser.add_argument(
            'function_name',
            help='the name of the function to set the runtime for'
        )

        # currently our infrastructure only supports python3.8 (via global dependencies layer compatibility)
        self.arg_parser.add_argument(
            '--python3-minor-version',
            choices=['8'],
            default='8',
            help='specify which python3 runtime to use'
        )
