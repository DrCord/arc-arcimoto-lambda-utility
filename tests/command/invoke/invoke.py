from arcimoto_aws_services.cognito import DEFAULT_CLIENT_ID

from tests.unit_tests_user_credentials import UnitTestsUserCredentials


class TestInvoke:

    UnitTestsUserCredentialsObject = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UnitTestsUserCredentialsObject = UnitTestsUserCredentials()

    @property
    def cognito_client_id(self):
        return DEFAULT_CLIENT_ID

    @property
    def password(self):
        return self.UnitTestsUserCredentialsObject.password

    @property
    def username(self):
        return self.UnitTestsUserCredentialsObject.username
