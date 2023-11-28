from arcimoto_aws_services.secretsmanager import SecretsManagerService


class UnitTestsUserCredentials(SecretsManagerService):

    unit_test_admin_user_credentials_secret_name = 'aws.cognito.unittest_admin'
    unit_test_non_admin_user_credentials_secret_name = 'aws.cognito.unittest'
    unit_test_user_credentials = None

    get_admin_user = None

    def __init__(self, get_admin_user=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_admin_user = get_admin_user
        self.unit_test_user_credentials = self.unit_test_user_credentials_get()

    @property
    def password(self):
        return self.unit_test_user_credentials.get('password')

    @property
    def username(self):
        return self.unit_test_user_credentials.get('username')

    def unit_test_user_credentials_get(self):
        if self.get_admin_user:
            return self.unit_test_admin_user_credentials_get()
        else:
            return self.unit_test_non_admin_user_credentials_get()

    def unit_test_non_admin_user_credentials_get(self):
        return self.get_secret(self.unit_test_non_admin_user_credentials_secret_name)

    def unit_test_admin_user_credentials_get(self):
        return self.get_secret(self.unit_test_admin_user_credentials_secret_name)
