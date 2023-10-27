"""Replace SCP.

Purpose:
    Replace DETACH_SCP_ID SCP with ATTACH_SCP_ID SCP defined in the associated env vars
Environment Variables:
    LOG_LEVEL: (optional): sets the level for function logging
            valid input: critical, error, warning, info (default), debug
    DETACH_SCP_ID: id of the policy to detach
    ATTACH_SCP_ID: id of the new policy to attach
    ASSUME_ROLE_NAME: Name of role to assume
"""
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import collections
import logging
import os
import sys

from aws_lambda_powertools import Logger
import boto3

# Standard logging config
DEFAULT_LOG_LEVEL = logging.INFO
LOG_LEVELS = collections.defaultdict(
    lambda: DEFAULT_LOG_LEVEL,
    {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    },
)

ATTACH_SCP_ID = os.environ["ATTACH_SCP_ID"]
DETACH_SCP_ID = os.environ["DETACH_SCP_ID"]

# Lambda initializes a root logger that needs to be removed in order to set a
# different logging config
root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)

logging.basicConfig(
    format="%(asctime)s.%(msecs)03dZ [%(name)s][%(levelname)-5s]: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=LOG_LEVELS[os.environ.get("LOG_LEVEL", "").lower()],
)

log = logging.getLogger(__name__)

# Get client
org_client = boto3.client("organizations")

@LOG.inject_lambda_context(log_event=True)
def lambda_handler(event, context):  # pylint: disable=unused-argument
    """Replace scp policy lambda handler."""
    account_id = event["detail"]["recipientAccountId"]
    replace_scp(account_id)


def replace_scp(account_id):
    """Replace scp policy from either a lambda or main method."""
    org_client.detach_policy(PolicyId=DETACH_SCP_ID, TargetId=account_id)
    org_client.attach_policy(PolicyId=ATTACH_SCP_ID, TargetId=account_id)


if __name__ == "__main__":

    def create_args():
        """Return parsed arguments."""
        parser = ArgumentParser(
            formatter_class=RawDescriptionHelpFormatter,
            description="""
Replace SCP for provided target account.

Supported Environment Variables:
    'LOG_LEVEL': defaults to 'info'
        - set the desired log level ('error', 'warning', 'info' or 'debug')

    DETACH_SCP_ID: id of the policy to detach
    ATTACH_SCP_ID: id of the new policy to attach
""",
        )
        required_args = parser.add_argument_group("required named arguments")
        required_args.add_argument(
            "--target-account-id",
            required=True,
            type=str,
            help="Account number to delete default cloudtrail resources in",
        )

        return parser.parse_args()

    sys.exit(replace_scp(**vars(create_args())))
