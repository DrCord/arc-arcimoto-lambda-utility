import argparse
import logging
import os
import sys

# add arcimoto-aws-services git submodule to path to allow imports to work
(parent_folder_path, current_dir) = os.path.split(os.path.dirname(__file__))
sys.path.append(os.path.join(parent_folder_path, 'arcimoto_aws_services'))

# sub-commands are implemented as modules
from arcimoto_lambda_utility.command import (  # noqa: E402
    create,
    dependencies,
    grant_api,
    invoke,
    layer,
    list,
    release,
    runtime,
    test,
    update
)


logging.basicConfig(format='%(message)s', level=logging.WARNING)

DEFAULT_AWS_REGION = "us-west-2"
DEFAULT_AWS_ACCOUNT_ID = "511596272857"


class LambdaManager:

    def __init__(self):
        self.arg_parser = argparse.ArgumentParser(
            description='Manage AWS integration for a lambda function',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        self.arg_parser.add_argument(
            '-v',
            '--verbose',
            action='store_true',
            help='enable verbose output mode'
        )
        self.arg_parser.add_argument(
            '-d',
            '--debug',
            action='store_true',
            help='enable debug mode, including imported modules'
        )
        self.arg_parser.add_argument(
            '--dry-run',
            action='store_true',
            help="don't actually execute any AWS calls"
        )
        self.arg_parser.add_argument(
            '-r',
            '--region',
            help='AWS region',
            default=DEFAULT_AWS_REGION
        )
        self.arg_parser.add_argument(
            '-a',
            '--account-id',
            help='AWS account ID',
            default=DEFAULT_AWS_ACCOUNT_ID
        )
        subparsers = self.arg_parser.add_subparsers(
            help='AWS management command to execute',
            dest='command'
        )
        subparsers.required = True

        self.sub_commands = {
            'create': create.Command(
                subparsers.add_parser(
                    'create',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                    help='create a new lambda function'
                )
            ),
            'dependencies': dependencies.Command(
                subparsers.add_parser(
                    'dependencies',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                    help='list all dependencies for a lambda'
                )
            ),
            'grant_api': grant_api.Command(
                subparsers.add_parser(
                    'grant_api',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                    help='create a resource policy allowing API Gateway to execute a lambda'
                )
            ),
            'invoke': invoke.Command(
                subparsers.add_parser(
                    'invoke',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                    help='invoke the named lambda function'
                )
            ),
            'layer': layer.Command(
                subparsers.add_parser(
                    'layer',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                    help='create a new lambda layer version'
                )
            ),
            'list': list.Command(
                subparsers.add_parser(
                    'list',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                    help='list all lambdas'
                )
            ),
            'release': release.Command(
                subparsers.add_parser(
                    'release',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                    help='create version and/or alias tags for a lambda release'
                )
            ),
            'runtime': runtime.Command(
                subparsers.add_parser(
                    'runtime',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                    help='set python3 runtime for a lambda'
                )
            ),
            'test': test.Command(
                subparsers.add_parser(
                    'test',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                    help='run the unit test lambdas for a non-unit test lambda'
                )
            ),
            'update': update.Command(
                subparsers.add_parser(
                    'update',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                    help='update a lambda function'
                )
            )
        }

    def run(self):
        # parse all global options out before passing along to subcommand
        args = self.arg_parser.parse_args()

        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)

        # run the requested sub-command
        try:
            self.sub_commands[args.command].run(args)
        except KeyboardInterrupt:
            print("\n.. Aborted ..")
            pass


def run():
    app = LambdaManager()
    app.run()
