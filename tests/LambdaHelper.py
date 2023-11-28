from arcimoto_aws_services.lambda_service import LambdaService

from tests.command_args import (
    DEFAULT_TEST_LAMBDA_DESCRIPTION,
    DEFAULT_TEST_LAMBDA_NAME,
    DEFAULT_TEST_LAMBDA_ROLE_NAME
)
from tests.dependencies import DependenciesConfigFile


class LambdaHelper(DependenciesConfigFile):

    _lambda_service_object = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lambda_tests_initial_prep()

    def lambda_create(self, function_name, description, zip_bytes, role):
        LambdaServiceObject = LambdaService(verbose=False)
        return LambdaServiceObject.create(
            function_name=function_name,
            description=description,
            zip_bytes=zip_bytes,
            role=role,
            mute=True
        )

    def lambda_delete(self, function_name):
        LambdaServiceObject = LambdaService(verbose=False)
        LambdaServiceObject.delete(
            function_name=function_name,
            mute=True
        )
        return None

    def lambda_dev_alias_create(self, function_name):
        LambdaServiceObject = LambdaService(verbose=False)
        LambdaServiceObject.lambda_dev_alias_create(
            function_name=function_name,
            mute=True
        )

    def lambda_tests_initial_prep(self):
        if self.lambda_exists():
            self.lambda_remove()

    def lambda_exists(self, function_name=DEFAULT_TEST_LAMBDA_NAME):
        return self._LambdaServiceObject.lambda_exists(
            function_name=function_name,
            mute=True
        )

    def lambda_remove(self, function_name=DEFAULT_TEST_LAMBDA_NAME):
        try:
            self._LambdaServiceObject.delete(
                function_name=function_name,
                mute=True
            )
        except self._LambdaServiceObject.client.exceptions.ResourceNotFoundException:
            # we don't care if this fails due to the function not existing
            return False

        return True

    @property
    def _LambdaServiceObject(self):
        if self._lambda_service_object is None:
            self._lambda_service_object = LambdaService(verbose=False)
        return self._lambda_service_object

    def lambda_with_dev_alias_create(self, function_name=DEFAULT_TEST_LAMBDA_NAME):
        try:
            # set up
            self.dependencies_create_file(function_name)
            self.create_tests_files(function_name)
            self._LambdaServiceObject.archive_create(
                function_name=function_name,
                mute=True
            )
            # actions
            try:
                self._LambdaServiceObject.create(
                    function_name=function_name,
                    description=DEFAULT_TEST_LAMBDA_DESCRIPTION,
                    zip_bytes=self._LambdaServiceObject.zip_bytes,
                    role=DEFAULT_TEST_LAMBDA_ROLE_NAME,
                    mute=True
                )
            except self._LambdaServiceObject.client.exceptions.ResourceConflictException:
                # if lambda already exists that is fine, move on
                pass
            try:
                self._LambdaServiceObject.lambda_dev_alias_create(
                    function_name=function_name,
                    mute=True
                )
            except self._LambdaServiceObject.client.exceptions.ResourceConflictException:
                # if dev alias already exists that is fine, move on
                pass
        except Exception as e:
            raise e
        finally:
            # clean up
            self._LambdaServiceObject.zip_bytes = None
            self.dependencies_remove_file()
            self.remove_tests_folder()

        return True

    def resources_create(self, function_name):
        self.dependencies_create_file(function_name)
        self.create_tests_files(function_name)

    def resources_remove(self):
        self.dependencies_remove_file()
        self.dependencies_invalid_file_remove()
        self.remove_tests_folder()
        self.schema_file_remove()
        self.schema_invalid_file_remove()
        self.remove_xml_output_folder()
