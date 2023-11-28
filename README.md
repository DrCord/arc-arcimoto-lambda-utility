# Arcimoto Lambda Utility

Utility for interacting with Arcimoto AWS Lambdas and Lambda Layers. Used at the CLI and in AWS Lambda related pipelines.

See `./arcimoto_lambda_utillity/README.md` or use the help command for usage information.

## Contributors

- Cord Slatton - Repo Man (Authorizes changes to master branch)

## Contributing

### Git commit formatting

We use the `Angular git commit` style

Full (long) version:

```git commit template
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

Short version

```git commit template
<type>(<scope>): <subject>
```

See https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-format more details

VS Code extension that helps you to make the commit msg, no need to remember your scope, etc.:
https://marketplace.visualstudio.com/items?itemName=Jhecht.git-angular

We use the allowed `types` from https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-format

We use custom `scopes` per repository, see `scopes` below. If you need to add a scope that is allowed.

#### Scopes

- bundle
- cognito
- command
- command:create
- command:dependencies
- command:grant_api
- command:invoke
- command:layer
- command:list
- command:release
- command:runtime
- command:test
- command:update
- layers
- path
- pipeline

### Prerequisites

The majority of the repo code is written in Python and meant to be executed by [AWS Lambda](https://aws.amazon.com/lambda/) in a Python runtime environment.  Many of the functions rely on the AWS SDK for Python, [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html).

Install `boto3` using pip:

```sh
pip install boto3
```

Additionally, in order to run Lambda functions which interact with AWS services, use the AWS [Command Line Interface (CLI)](https://aws.amazon.com/cli/).  
Install `CLI` using pip:

```sh
pip install awscli
```

In order to use the CLI, you will also need the proper AWS credentials, managed by the AWS [Identity and Access Management (IAM)](https://console.aws.amazon.com/iam/home?#/home) service.  Have the Arcimoto AWS administrator create CLI credentials for you, or give you IAM permission to create them yourself.  Then on the command line run:

```sh
aws configure
```

and enter the Access Key ID and Secret Access Key that you just created.

### Installing

#### For Development

To get the AWSLmbda Lambda functions running locally, first obtain a local copy by cloning the repository.  From the directory that you want to install your local copy, use git on the command line:

```sh
git clone https://<username>@bitbucket.org/arcimotocode1/awsshared.git
```

Where `<username>` is your bitbucket user name.

#### For usage (installation via pip)

Setup a bitbucket app password with read access to your account's repositories and substitute the username into the command:

```sh
pip install git+https://{{BITBUCKET_USERNAME}}@bitbucket.org/arcimotocode1/arcimoto-lambda-utility.git
```

##### Usage in a bitbucket pipeline

In order to be able to install in a pipeline programatically you will need to set up ssh access between the repos. On the repo that is using this utility in the pipeline you will need to retrieve the repository public ssh key from settings->pipeline->ssh keys->copy public key (you may need to generate the keypair before you can copy the public key portion). On this repository set that public key as an access key at settings->access keys->add key.

Pipeline usage example:

```cli
# install arcimoto-lambda-utility
- pip install git+ssh://git@bitbucket.org/arcimotocode1/arcimoto-lambda-utility.git
- python -m arcimoto_lambda_utility {{command}} {{args}}
```

## Automatic Versioning

This package automatically updates it's version in `setup.py` using [semantic versioning](https://semver.org/) via the [python-semantic-release](https://github.com/relekang/python-semantic-release) package. It runs on a merge to the `master` branch via bitbucket Continous Integration (CI) (see `bitbucket-pipelines.yml`). It generates a new section in the `CHANGELOG.md` file then updates the `__version__` in `setup.py` and commits to the master branch `master` with a message that prevents a re-run of the CI (`[skip-ci]`).

### Semantic Version Schema

`MAJOR.MINOR.PATCH`

### Initial Setup

- Require `Commitizen` for all contributors (see above)

### Configuration

Uses angular commit style to evaluate commits for automatic semantic versioning. We use the [default rules](https://github.com/semantic-release/commit-analyzer/blob/master/lib/default-release-rules.js) from [semantic-release: commit-analyzer](https://github.com/semantic-release/commit-analyzer).

Scope => Release Type

- feat => minor
- fix => patch
- perf => patch

The body or footer can begin with `BREAKING CHANGE:` followed by a short description to create a major release.

## Directory Layout

The `aricmoto_lambda_utility` folder contains the package.

## BitBucket Pipelines

The BitBucket pipelines file [bitbucket-pipelines.yml] implements the Continuous Integration (CI)/Continuous Deployment (CD) for the AWSLambda repository.

### Pipelines

#### Run Tests

Tests are run automatically on Pull Request (PR) creation/update from a feature branch beginning with the prefix `TEL-` to the `dev` branch.

These tests include:

- linting
- unit tests

Any failed tests will result in a failure of the pipeline, which will prevent merging the PR to `dev` until the PR is updated to fix the issue(s) and the pipeline is re-run successfully for the PR.

#### Merge to Dev

- Notification to email group: `arcimoto-lambda-utility-release-dev@arcimoto.com`

#### Merge to Staging

- Notification to email group: `arcimoto-lambda-utility-release-staging@arcimoto.com`

#### Merge to Prod

- Publish new semantic version based on the commits included (see Automatic Versioning section above)
- Notification to email group: `arcimoto-lambda-utility-release@arcimoto.com`
