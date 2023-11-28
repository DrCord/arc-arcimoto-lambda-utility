import json

from tests.TestHelper import TestHelper

TEST_PAYLOAD_FILE_PATH = 'lambda/tests/payload.json'


class TestInvokeHelper(TestHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_tests_files(self):
        return self.payload_file_create()

    def payload_file_create(self, file_content={}):
        with self.safe_open_w(TEST_PAYLOAD_FILE_PATH) as f:
            f.write(json.dumps(file_content))
        return TEST_PAYLOAD_FILE_PATH

    def payload_file_invalid_create(self):
        with self.safe_open_w(TEST_PAYLOAD_FILE_PATH) as f:
            f.write('{{"prop": "not-valid-json-missing-bracket"}')
        return TEST_PAYLOAD_FILE_PATH
