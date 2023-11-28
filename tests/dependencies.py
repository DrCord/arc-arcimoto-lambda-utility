import json
import os


from arcimoto_aws_services import path
from arcimoto_aws_services.lambda_service import LambdaService

from tests.TestHelper import TestHelper

from tests.command_args import DEFAULT_TEST_LAMBDA_NAME


class DependenciesConfigFile(TestHelper):

    dependencies_file_created = False
    schema_file_created = False

    dependencies_schema_content = {
        '$schema': 'http://json-schema.org/draft-06/schema#',
        'title': 'Arcimoto AWS Lambda Dependencies Definitions',
        'description': 'Dependency definitions to build deployment packages for AWS Lambdas and Layers',
        'type': 'object',
        'properties': {
            'global_dependencies': {
                'type': 'object'
            }
        },
        'required': [
            'global_dependencies'
        ]
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def dependencies_create_file(self, lambda_name=DEFAULT_TEST_LAMBDA_NAME, file_content=None, verbose=False):
        '''
        create mock path.DEPENDENCIES_CONFIG file
        do not overwrite if file already exists
        file only contains enough of the real dependencies.json file structure/data to pass tests
        '''

        # do not proceed if file already exists
        file_exists = os.path.exists(path.DEPENDENCIES_CONFIG)
        if file_exists:
            return

        if file_content is not None:
            dependencies_file_content = file_content
        else:
            (
                global_dependencies_latest_layer_version_dev,
                global_dependencies_latest_layer_version_staging,
                global_dependencies_latest_layer_version_prod
            ) = self.global_dependencies_latest_layer_versions_get()
            dependencies_file_content = self.dependencies_file_content_get(
                global_dependencies_latest_layer_version_dev,
                global_dependencies_latest_layer_version_staging,
                global_dependencies_latest_layer_version_prod,
                lambda_name
            )
        json_object = json.dumps(dependencies_file_content, indent=4)
        with open(path.DEPENDENCIES_CONFIG, 'w') as outfile:
            outfile.write(json_object)

        self.dependencies_file_created = True

    def dependencies_file_content_get(self, global_dependencies_latest_layer_version_dev, global_dependencies_latest_layer_version_staging, global_dependencies_latest_layer_version_prod, lambda_name=DEFAULT_TEST_LAMBDA_NAME):
        dependencies_file_content = {
            'global_dependencies': {
                'arcimoto': {
                    'name': 'arcimoto',
                    'from': 'dependencies/arcimoto/',
                    'to': 'arcimoto/'
                },
                'psycopg2': {
                    'name': 'psycopg2',
                    'from': 'dependencies/psycopg2.zip',
                    'action': 'unzip'
                },
                'cerberus': {
                    'name': 'cerberus',
                    'from': 'dependencies/cerberus',
                    'to': 'cerberus'
                }
            },
            'layers': {
                'global_dependencies': {
                    "name": "arcimoto-globals",
                    "version": global_dependencies_latest_layer_version_prod,
                    "meta": {
                        "contains": [
                            "arcimoto",
                            "cerberus",
                            "psycopg2"
                        ],
                        "compatible_runtimes": [
                            "python3.8"
                        ]
                    }
                },
                'global_dependencies_dev': {
                    "name": "arcimoto-globals-dev",
                    "version": global_dependencies_latest_layer_version_dev,
                    "meta": {
                        "contains": [
                            "arcimoto",
                            "cerberus",
                            "psycopg2"
                        ],
                        "compatible_runtimes": [
                            "python3.8"
                        ]
                    }
                },
                'global_dependencies_staging': {
                    "name": "arcimoto-globals-staging",
                    "version": global_dependencies_latest_layer_version_staging,
                    "meta": {
                        "contains": [
                            "arcimoto",
                            "cerberus",
                            "psycopg2"
                        ],
                        "compatible_runtimes": [
                            "python3.8"
                        ]
                    }
                },
                'package1': {
                    'name': 'package_1',
                    'version': 1,
                    'meta': {
                        "contains": [
                            "common_dependency1",
                            "common_dependency2"
                        ],
                        "compatible_runtimes": [
                            "python3.8"
                        ]
                    }
                },
                'package2-missing-name-property': {
                    'version': 1,
                    'meta': {
                        "contains": [
                            "common_dependency1",
                            "common_dependency2"
                        ],
                        "compatible_runtimes": [
                            "python3.8"
                        ]
                    }
                }
            },
            'common_dependencies': {
                "common_dependency1": {
                    "from": "test_archive.zip",
                    "action": "unzip"
                },
                "common_dependency2": {
                    "from": "arcimoto_lambda_utility/command",
                    "to": "command"
                }
            },
            'functions': {
                f'{lambda_name}': {
                    'bundle': 'tests'
                },
                f'{lambda_name}_with_dependencies': {
                    'bundle': 'tests',
                    'common_dependencies': [
                        'common_dependency1'
                    ],
                    'dependencies': [
                        {
                            "from": "arcimoto_lambda_utility/command",
                            "to": "command"
                        }
                    ]
                },
                f'test_{lambda_name}': {
                    'bundle': 'tests'
                },
            }
        }

        return dependencies_file_content

    def dependencies_invalid_file_create(self):
        return super().invalid_json_file_create(path.DEPENDENCIES_CONFIG)

    def dependencies_remove_file(self):
        ''' remove path.DEPENDENCIES_CONFIG file if created by unit tests and available '''

        # do not proceed if file was not created by this tests helper class
        if self.dependencies_file_created:
            try:
                os.remove(path.DEPENDENCIES_CONFIG)
            except Exception:
                pass

    def dependencies_invalid_file_remove(self):
        return super().invalid_json_file_remove()

    def global_dependencies_latest_layer_versions_get(self):
        # get global dependencies latest layer versions
        LambdaServiceObject = LambdaService(verbose=False)
        global_dependencies_latest_layer_version_dev = LambdaServiceObject.get_latest_global_dependencies_layer_version('dev', False, True)
        global_dependencies_latest_layer_version_staging = LambdaServiceObject.get_latest_global_dependencies_layer_version('staging', False, True)
        global_dependencies_latest_layer_version_prod = LambdaServiceObject.get_latest_global_dependencies_layer_version('prod', False, True)

        return (global_dependencies_latest_layer_version_dev, global_dependencies_latest_layer_version_staging, global_dependencies_latest_layer_version_prod)

    def schema_file_create(self):
        # do not proceed if file already exists
        file_exists = os.path.exists(path.DEPENDENCIES_CONFIG_SCHEMA)
        if file_exists:
            return

        json_object = json.dumps(self.dependencies_schema_content, indent=4)
        try:
            with open(path.DEPENDENCIES_CONFIG_SCHEMA, 'w') as outfile:
                self.schema_file_created = True
                try:
                    outfile.write(json_object)
                except Exception as e:
                    raise Exception(f'Unable to write file content from source data:\n{self.dependencies_schema_content}') from e
        except Exception as e:
            raise Exception(f'Unable to open {path.DEPENDENCIES_CONFIG_SCHEMA} for writing file: {e}')

    def schema_invalid_file_create(self):
        return super().invalid_json_file_create(path.DEPENDENCIES_CONFIG_SCHEMA)

    def schema_file_remove(self):
        # do not proceed if file was not created by this tests helper class
        if self.schema_file_created:
            try:
                os.remove(path.DEPENDENCIES_CONFIG_SCHEMA)
            except Exception:
                pass

    def schema_invalid_file_remove(self):
        return super().invalid_json_file_remove()
