import logging

from .command import AbstractCommand

from arcimoto_aws_services.lambda_service import LambdaService


class Command(AbstractCommand):

    args = None
    function_name = None
    lambda_service_object = None
    mute = None
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
        self._update_lambda()

    @property
    def _LambdaServiceObject(self):
        if self.lambda_service_object is None:
            self.lambda_service_object = LambdaService(region=self.region)
        return self.lambda_service_object

    def _parse_arguments(self, args, mute):
        self.args = args
        self.function_name = args.function_name
        self.region = args.region
        self.mute = mute

    def _parser_add_arguments(self):
        self.arg_parser.add_argument(
            'function_name',
            help='the name of the function to update'
        )

    def _update_lambda(self):
        if not self.mute:
            self.logger.info(f'Preparing to update {self.args.function_name}...')

        self._LambdaServiceObject.lambda_update_code(
            function_name=self.function_name,
            verbose=self.args.verbose,
            mute=self.mute
        )

        self._LambdaServiceObject.add_layers(
            function_name=self.function_name,
            verbose=self.args.verbose,
            mute=self.mute
        )
        if not self.mute:
            self.logger.info(f'Function {self.function_name}: update complete')
