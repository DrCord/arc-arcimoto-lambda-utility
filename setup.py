
import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

# maintained automatically in pipeline release to master branch by python-semantic-version
__version__ = '1.2.3'

setuptools.setup(
    name='arcimoto-lambda-utility',
    version=__version__,
    author='Cord Slatton',
    author_email='cords@arcimoto.com',
    description='Utility for interacting with Arcimoto AWS Lambdas and Lambda Layers. Used at the CLI and in AWS Lambda related pipelines.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://bitbucket.org/arcimotocode1/arcimoto-lambda-utility',
    license='private',
    packages=[
        'arcimoto_lambda_utility',
        'arcimoto_lambda_utility.command',
        'arcimoto_aws_services',
        'arcimoto_aws_services.arcimoto_aws_services',
        'arcimoto_aws_services.tests'
    ],
    install_requires=[
        'argparse',
        'boto3',
        'botocore',
        'cognito',
        'command',
        'datetime',
        'jsonschema',
        'path',
        'uuid'
    ]
)
