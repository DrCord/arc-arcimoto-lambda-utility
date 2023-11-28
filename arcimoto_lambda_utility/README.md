# Arcimoto Lambda Utility

The `lambda` utility is a general purpose command line tool for interacting with AWS for lambda function management. The goal of this tool is to remove the need for direct console configuration and management of AWS functions.

The utility is built as an executable Python package and is expected to be run from within the AWSLambda repository directory structure.

To run the tool from the root of the repository:

```text
$ python3 ./utility/lambda --help

usage: lambda [-h] [-v] [-d] [--dry-run] [-r REGION] [-a ACCOUNT_ID]
              {create,update,release,grant_api} ...

Manage AWS integration for a lambda function

positional arguments:
  {create,update,release,grant_api}
                        AWS management command to execute
    create              create a new lambda function
    update              update a lambda function
    layer               creates a new lambda layer version
    release             create version and/or alias tags for a lambda release
    grant_api           create a resource policy allowing API Gateway to
                        execute a lambda
    invoke              invokes a lambda with a payload
    test                runs the tests defined in the bundle.json file fo rhte lambda

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         enable verbose output mode (default: False)
  -d, --debug           enable debug mode, including imported modules
                        (default: False)
  --dry-run             don't actually execute any AWS calls (default: False)
  -r REGION, --region REGION
                        AWS region (default: us-west-2)
  -a ACCOUNT_ID, --account-id ACCOUNT_ID
                        AWS account ID (default: 511596272857)
```

## Create

Creates a new lambda function in AWS and assigns the initial `dev` alias. The function must already exist and be configured in the repository dependencies.json file. The execution role must already exist in AWS. The lambda will be created in AWS and the code will be bundled, including all specified dependencies, and uploaded to AWS. Lambdas will have a layer added to their configuration for global dependencies and common dependencies with a declared layer after creation.

**NOTE:** This will not create the source code for the function in the repository or automatically configure dependencies.json for the function.

```text
$ python3 ./utility/lambda create --help

usage: lambda create [-h] [--role ROLE] [--description DESCRIPTION]
                     [--vpc {authority,main,users}] [--timeout TIMEOUT]
                     [--tag TAG]
                     function

positional arguments:
  function              the name of the function to create

optional arguments:
  -h, --help            show this help message and exit
  --role ROLE           lambda execution role
  --description DESCRIPTION
                        description of the lambda
  --vpc {authority,main,users}
                        which VPC to attach to (default: main)
  --timeout TIMEOUT     execution timeout in seconds (default: 30)
  --tag TAG             tag to apply to the lambda (default: [])
```

NOTE: The --tag argument can be repeated in order to assign multiple tags:

```text
$ python3 ./utility/lambda create function_name --role function.role --description "Function description" --tag Telematics --tag users

Preparing to create...
Created function function_name: arn:aws:lambda:us-west-2:511596272857:function:function_name
```

## Dependencies

List all dependencies for a lambda function. This list both local and common dependencies.

**NOTE:** This will output nothing if there are no dependencies.

```text
$ python3 ./utility/lambda create --help

usage: lambda dependencies [-h] lambda_name

positional arguments:
  lambda_name              the name of the function to return the dependencies list for.

optional arguments:
  -h, --help            show this help message and exit
```

## Grant API Access

In order for a lambda to be callable from API Gateway when using stage variables, a resource policy must be directly attached to the lambda for each environment. The grant_api sub-command facilitates creating this resource policy.

```text
$ python3 ./utility/lambda grant_api --help

usage: lambda grant_api [-h] -a API_ID -p REQUEST_PATH [-e {dev,staging,prod}]
                        function

positional arguments:
  function              the name of the lambda function to allow

optional arguments:
  -h, --help            show this help message and exit
  -a API_ID, --api-id API_ID
                        the ID of the API to allow (default: None)
  -p REQUEST_PATH, --request-path REQUEST_PATH
                        the request method and path to allow (default: None), example: POST/v1/users/create
  -e {dev,staging,prod}, --env {dev,staging,prod}
                        environment to use (default: dev)
```

## Invoke

Invokes the specified lambda function. Payload json can be passed in directly as a command line argument or by specifying a json file. Allows authentication against a user pool.

```text
$ python3 ./utility/lambda invoke --help

usage: lambda invoke [-h] [--user USER] [--env {dev,staging,prod}]
                     [--client-id POOL] (--payload PAYLOAD | --file-name FILE_NAME)
                     function

positional arguments:
  function              the name of the lambda to invoke

optional arguments:
  -h, --help            show this help message and exit
  --user USER           authenticate as a specific user before invoking
                        (default: None)
  --env {dev,staging,prod}
                        specify which environment to use (default: dev)
  --client-id POOL      specify which user pool to use for authentication
                        (default: us-west-2_3x5jXoVFD)
  --payload PAYLOAD     the payload to pass as data to the lambda (default:
                        None)
  --file-name FILE_NAME
                        name of a json file to use as payload data (default:
                        None)
  --python3-minor-version PYTHON3-MINOR-VERSION
                        python3 minor version to set runtime to (default: 8)
```

## Layer

Creates a new lambda layer version. Outputs the ARN of the lambda layer version. Uses config in dependencies.json to build the layer.

```text
$ python3 ./utility/lambda layer --help

usage: lambda layer [-h] [--description DESCRIPTION] layer

positional arguments:
  layer              the name of the layer to create a new version of

optional arguments:
  -h, --help            show this help message and exit
  --description DESCRIPTION
                        layer description (default: empty string)
```

## List

List all or or a subset of Arcimoto AWS lambda function names. A set of flags is available to output excluding or exclusively tests. There is a flag to include the relative file path with the lambda name. A set of flags is available to output all lambdas from a given bundle, or the global or common dependencies, including their filepaths.

```text
$ python3 ./utility/lambda list --help

usage: lambda list [-h] [--include_filepath] [--global_dependencies|--common_config|--bundle BUNDLE] [--exclude_tests|--tests_only]

positional arguments:
  None

optional arguments:
  -h, --help                show this help message and exit
  --include_filepath        include relative filepath with lambda name

  mutally exclusive group 1:
    --global_dependencies   list files including relative path for global dependencies
    --common_config         list files including relative path for common config
    --bundle BUNDLE         list lambdas for bundle named input BUNDLE (str)

  mutally exclusive group 2:
    --exclude_tests         exclude tests from output
    --tests_only            only include tests in output
```

## Release

Tags a release for the specified lambda. If the destination environment is `staging`, creates a new version if there are any changes and sets the staging alias to that potentially new version. If the destination environment is `prod`, sets the production alias to the current staging version.

```text
$ python3 ./utility/lambda release --help

usage: lambda release [-h] [--description DESCRIPTION] function {prod,staging}

positional arguments:
  function              the name of the function to release
  {prod,staging}        target release environment

optional arguments:
  -h, --help            show this help message and exit
  --description DESCRIPTION
                        reason for release (default: Managed release)
```

## Runtime

Sets the python3 runtime for the specified lambda LATEST version.

```text
$ python3 ./utility/lambda runtime --help

usage: lambda runtime [-h] [--python3-minor-version PYTHON3-MINOR-VERSION] function

positional arguments:
  function              the name of the function to update runtime for

optional arguments:
  -h, --help            show this help message and exit
  --python3-minor-version PYTHON3-MINOR-VERSION
                        python3 minor version to set runtime to (default: 8)
```

## Test

Runs the lambda's unit tests denoted in the bundle's bundle.json file or other test suites.

```text
$ python3 ./utility/lambda test --help

usage: lambda test [-h] [--user USER] [--client-id POOL] (--payload PAYLOAD | --file-name FILE_NAME) function

positional arguments:
  function              the name of the lambda to invoke, use `None` and a test suite flag to run a non-function test suite

optional arguments:
  -h, --help            show this help message and exit
  --user USER           authenticate as a specific user before invoking
                        (default: None)
  --client-id POOL      specify which user client-id to use for authentication
                        (default: us-west-2_3x5jXoVFD)
  --payload PAYLOAD     the payload to pass as data to the lambda (default:
                        None)
  --file-name FILE_NAME
                        name of a json file to use as payload data (default:
                        None)
  --test-lambda-definitions TEST_LAMBDA_DEFINITIONS
                        run the lambda definitions test suite if the `function` input is set to `None`. Validates the lambda definitions in dependencies.json and each bundle bundle.json file.
  --test-dependencies-file-exists TEST_DEPENDENCIES_FILE_EXISTS
                        run the dependencies file exists test suite if the `function` input is set to `None`. Validate the dependencies.json file exists.
  --test-dependencies-schema-exists TEST_DEPENDENCIES_SCHEMA_EXISTS
                        run the dependencies schema exists test suite if the `function` input is set to `None`. Validate the dependencies.schema.json file exists.
  --test-dependencies-file-valid-json TEST_DEPENDENCIES_FILE_VALID_JSON
                        run the dependencies schema exists test suite if the `function` input is set to `None`. Validate the dependencies.json file as valid JSON.
  --test-dependencies-schema-valid-json TEST_DEPENDENCIES_SCHEMA_VALID_JSON
                        run the dependencies schema exists test suite if the `function` input is set to `None`. Validate the dependencies.schema.json file as valid JSON.
  --test-dependencies-file-valid-for-schema TEST_DEPENDENCIES_FILE_VALID_FOR_SCHEMA
                        run the dependencies schema exists test suite if the `function` input is set to `None`. Validate dependencies.json against the dependencies.schema.json file.

## Update

Creates a lambda bundle and pushes the update to the $LATEST version for the specified function. Does not change any verion or alias configuration. The function must already exist and be configured in the repository dependencies.json file. Lambdas will have a layer added to their configuration for global dependencies and common dependencies with a declared layer after update.

```text
$ python3 ./utility/lambda update --help

usage: lambda update [-h] function

positional arguments:
  function    the name of the function to update

optional arguments:
  -h, --help  show this help message and exit
```
```

## Development Notes

### `__init__.py`

The main `LambdaManager` class is implemented in `__init__.py` in order to allow easy package importing. The shared argument parser is created here, and each supported command is added as a subparser. Sub-commands are implemented as subclasses of the abstract base class `command.AbstractCommand`, which proveds convenience configuration for logging and argument parsing.

### `__main__.py`

Allows the package folder to be executed as if it were a file. Simply runs the `LambdaManager` defined in `__init__.py`.

### `path.py`

Common path and directory structure definitions and utilities. Convenience functions for finding specific directories and files specific to the AWSLambda repository.

### `bundle.py`

Common lambda bundle related functions are defined here. These tools allow you to create .zip archives for lambda bundles easily using the repository dependencies.json file.

### `cognito.py`

Common authentication and user pool configuration. Supports direct authentication, token generation and password challenges (including password reset and MFA).
