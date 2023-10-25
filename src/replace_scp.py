"""Replace SCP.

Purpose:
    Replace DETACH_SCP_ID SCP with ATTACH_SCP_ID SCP defined in the associated env vars
Environment Variables:
    LOG_LEVEL: (optional): sets the level for function logging
            valid input: critical, error, warning, info (default), debug
    DETACH_SCP_ID: id of the policy to detach
    ATTACH_SCP_ID: id of the new policy to attach
    DRY_RUN: (optional): true or false, defaults to true
    ASSUME_ROLE_NAME: Name of role to assume
"""
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import collections
import logging
import os
import sys

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
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"

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

# Get the Lambda session and clients
SESSION = boto3.Session()


def lambda_handler(event, context):  # pylint: disable=unused-argument
    """Replace scp policy lambda handler."""
    log.debug("AWS Event:%s", event)

    account_id = get_account_id(event)

    replace_scp(account_id)


def replace_scp(account_id):
    """Replace scp policy from either a lambda or main method."""
    org_client = SESSION.client("organizations")

    org_client.detach_policy(PolicyId=DETACH_SCP_ID, TargetId=account_id)

    org_client.attach_policy(PolicyId=ATTACH_SCP_ID, TargetId=account_id)


def get_account_id(event):
    """Return account id."""
    return event["detail"]["recipientAccountId"]


def get_partition():
    """Return AWS partition."""
    sts = boto3.client("sts")
    return sts.get_caller_identity()["Arn"].split(":")[1]


def cli_main(target_account_id):
    """Process cli assume_role_name arg and pass to main."""
    log.debug("CLI - target_account_id=%s", target_account_id)

    main(target_account_id)


def main(target_account_id):
    """Assume role and replace default scp."""
    log.debug(
        "Main identity is %s",
        SESSION.client("sts").get_caller_identity()["Arn"],
    )

    replace_scp(
        target_account_id,
    )

    if DRY_RUN:
        log.debug("Dry Run listed scp replacement")
    else:
        log.debug("SCP Replaced")


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

    'DRY_RUN': defaults to 'true'
        - set whether actions should be simulated or live
        - value of 'true' (case insensitive) will be simulated.

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

    sys.exit(cli_main(**vars(create_args())))
