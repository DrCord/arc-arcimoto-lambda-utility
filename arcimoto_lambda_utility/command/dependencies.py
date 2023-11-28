import logging

from .command import AbstractCommand

from arcimoto_aws_services import bundle

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(AbstractCommand):

    arg_parser = None
    common_config = None
    function_name = None
    functions = None
    global_dependencies = None
    lambda_common_dependencies_files = []
    lambda_dependencies = []
    lambda_dependencies_data = None
    lambda_local_dependencies_files = []

    def __init__(self, arg_parser):
        super().__init__(arg_parser)
        self.arg_parser = arg_parser
        self._parser_add_arguments()

    def run(self, args, mute=False):
        super().run(args)
        self._parse_arguments(args)
        self._dependencies_get()
        self.lambda_dependencies = self._lambda_get_dependencies(self.function_name)

        if not mute:
            for item in self.lambda_dependencies:
                print(item)

        return self.lambda_dependencies

    def _dependencies_get(self):
        (self.functions, self.common_config, self.global_dependencies) = bundle.load_dependencies()

    def _lambda_get_dependencies(self, function_name):
        self._lambda_get_dependencies_data(function_name)
        self._lambda_get_common_dependencies()
        self._lambda_get_local_dependencies()
        self.lambda_dependencies = self.lambda_common_dependencies_files + self.lambda_local_dependencies_files

        return sorted(list(set(self.lambda_dependencies)))

    def _lambda_get_dependencies_data(self, function_name):
        self.lambda_dependencies_data = None
        for key, value in self.functions.items():
            if key == function_name:
                self.lambda_dependencies_data = value
        if self.lambda_dependencies_data is None:
            raise KeyError(f'Input function_name {function_name} not found in configuration')
        return self.lambda_dependencies_data

    def _lambda_get_common_dependencies(self):
        if not isinstance(self.lambda_dependencies_data, dict):
            raise ValueError('self.lambda_dependencies_data must be a dict')
        for item in self.lambda_dependencies_data.get('common_dependencies', []):
            common_dependency_data = self.common_config.get(item, None)
            if common_dependency_data is None:
                raise KeyError(f'Unable to get data for common dependency {item}')
            file_path = common_dependency_data.get('from', None)
            if file_path is None:
                raise KeyError(f'Unable to get `from` path for common dependency {item}')
            self.lambda_common_dependencies_files.append(file_path)

        return sorted(list(set(self.lambda_common_dependencies_files)))

    def _lambda_get_local_dependencies(self):
        if not isinstance(self.lambda_dependencies_data, dict):
            raise ValueError('self.lambda_dependencies_data must be a dict')
        for item in self.lambda_dependencies_data.get('dependencies', []):
            file_path = item.get('from', None)
            if file_path is None:
                raise KeyError(f'Unable to get `from` path for common dependency {item}')
            self.lambda_local_dependencies_files.append(file_path)

        return sorted(list(set(self.lambda_local_dependencies_files)))

    def _parse_arguments(self, args):
        if not isinstance(args.function_name, str):
            raise ValueError('Input function name must be a string.')

        self.function_name = args.function_name

    def _parser_add_arguments(self):
        self.arg_parser.add_argument(
            'function_name',
            help='the lambda name to output the list of dependencies for'
        )
