import argparse
import unittest
import warnings

from arcimoto_lambda_utility.command import layer

from tests.dependencies import DependenciesConfigFile
from tests.TestHelper import TestHelper

from tests.libraries import TestLibraries

from tests.command_args import LayerCommandArgs


class TestRun(unittest.TestCase):

    args = None
    default_parser_description = 'Unit test created'
    LayerCommandObject = None

    @classmethod
    def setUpClass(cls):
        warnings.filterwarnings(
            'ignore',
            category=ResourceWarning
        )

        cls.args = LayerCommandArgs()
        cls.DependenciesFileObject = DependenciesConfigFile()
        cls.DependenciesFileObject.dependencies_create_file()

        cls.TestHelperObject = TestHelper()
        cls.TestHelperObject.create_tests_files()

        cls.TestLibrariesObject = TestLibraries()
        cls.TestLibrariesObject.archive_create()

    @classmethod
    def tearDownClass(cls):
        cls.DependenciesFileObject.dependencies_remove_file()
        cls.TestHelperObject.remove_tests_folder()
        cls.TestLibrariesObject.archive_remove()

    # test successes
    def test_run_success(self):
        parser = argparse.ArgumentParser(description=self.default_parser_description)
        LayerCommandObject = layer.Command(parser)
        try:
            LayerCommandObject.run(self.args, True)
        except Exception as e:
            self.fail(f'test failed unexpectedly: {e}')

    # test errors
    # None


if __name__ == '__main__':
    unittest.main()
