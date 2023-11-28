import logging

from .command import AbstractCommand

from arcimoto_aws_services import bundle

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(AbstractCommand):

    arg_parser = None
    args = None
    common_config_data = None
    functions_data = None
    global_dependencies_data = None
    mute = False

    def __init__(self, arg_parser):
        super().__init__(arg_parser)
        self.arg_parser = arg_parser
        self._parser_add_arguments()

    def run(self, args, mute=False):
        super().run(args)
        if mute:
            self.logger.setLevel(logging.ERROR)

        self._parse_arguments(args, mute)
        self._dependencies_load()

        if self.args.global_dependencies:
            output_data = self.global_dependencies
        elif self.args.common_config:
            output_data = self.common_config
        else:
            output_data = self.functions

        return self._output(output_data)

    @property
    def common_config(self):
        if self.common_config_data is None:
            self._dependencies_load()
        return sorted(self._file_paths_get(self.common_config_data))

    @property
    def functions(self):
        if self.functions_data is None:
            self._dependencies_load()
        lambdas = []
        for key, value in self.functions_data.items():
            if self.args.exclude_tests and key.startswith('test_'):
                continue
            elif self.args.tests_only and not key.startswith('test_'):
                continue
            if self.args.bundle != '' and value.get('bundle', '').split('/')[0] != self.args.bundle:
                continue
            if self.args.include_filepath:
                lambdas.append(f"lambda/{value.get('bundle', '')}/{key}.py")
                continue
            lambdas.append(key)
        return sorted(lambdas)

    @property
    def global_dependencies(self):
        if self.global_dependencies_data is None:
            self._dependencies_load()
        return sorted(self._file_paths_get(self.global_dependencies_data))

    def _dependencies_load(self):
        (self.functions_data, self.common_config_data, self.global_dependencies_data) = bundle.load_dependencies()

    def _file_paths_get(self, config):
        file_paths = []
        for value in config.values():
            file_path = value.get('from', None)
            if file_path is not None:
                file_paths.append(file_path)
        return file_paths

    def _output(self, data):
        for item in data:
            if not self.mute:
                print(item)
        return data

    def _parse_arguments(self, args, mute):
        self.args = args
        self.mute = mute

    def _parser_add_arguments(self):
        self.arg_parser.add_argument(
            '--include_filepath',
            action='store_true',
            help='include filepath with lambda name'
        )

        group1 = self.arg_parser.add_mutually_exclusive_group(required=False)
        group1.add_argument(
            '--global_dependencies',
            action='store_true',
            help='list files for global dependencies'
        )
        group1.add_argument(
            '--common_config',
            action='store_true',
            help='list files for common config'
        )
        group1.add_argument(
            '--bundle',
            default='',
            help='list lambdas for bundle named {input}'
        )

        group2 = self.arg_parser.add_mutually_exclusive_group(required=False)
        group2.add_argument(
            '--exclude_tests',
            action='store_true',
            help='exclude tests'
        )
        group2.add_argument(
            '--tests_only',
            action='store_true',
            help='only list tests'
        )
