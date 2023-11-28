import json
import os
import os.path
import shutil

from arcimoto_aws_services import path

from tests.TestHelper import TestHelper


class TestBundles(TestHelper):

    bundle_schema_content = {
        'test': 'property'
    }
    bundle_schema_file_created = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def bundle_json_invalid_file_create(self):
        bundle_json_invalid_content = '{{not-valid-json}'
        with self.safe_open_w('lambda/tests/bundle.json') as f:
            f.write(bundle_json_invalid_content)

    def bundle_json_invalid_file_remove(self):
        dirpath = os.path.join('lambda', 'tests')
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)

    def bundle_schema_file_create(self):
        # do not proceed if file already exists
        file_exists = os.path.exists(path.BUNDLE_CONFIG_SCHEMA)
        if file_exists:
            return

        with open(path.BUNDLE_CONFIG_SCHEMA, 'w') as f:
            self.bundle_schema_file_created = True
            f.write(json.dumps(self.bundle_schema_content))

    def bundle_schema_file_remove(self):
        # do not proceed if file was not created by this tests helper class
        if self.bundle_schema_file_created:
            try:
                os.remove(path.BUNDLE_CONFIG_SCHEMA)
            except Exception:
                pass

    def bundle_schema_invalid_file_create(self):
        return super().invalid_json_file_create(path.BUNDLE_CONFIG_SCHEMA)

    def bundle_schema_invalid_file_remove(self):
        return super().invalid_json_file_remove()
