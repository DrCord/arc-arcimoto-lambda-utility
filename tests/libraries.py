import os
import shutil

DEFAULT_TEST_ARCHIVE_NAME = 'test_archive'


class TestLibraries():

    asset_dest = 'arcimoto_lambda_utility/dest'
    asset_source = 'arcimoto_lambda_utility/command'
    build_dir = None
    dest = None
    root_dir = None
    source = None

    DependenciesFileObject = None

    def __init__(self):
        super().__init__()

    def archive_create(self):
        shutil.make_archive(DEFAULT_TEST_ARCHIVE_NAME, 'zip', self.asset_source)

    def archive_remove(self):
        # remove test_archive.zip file if it exists
        try:
            os.remove(f'{DEFAULT_TEST_ARCHIVE_NAME}.zip')
        except Exception:
            pass
