"""Replace SCP.

Purpose:
    Replace DETACH_SCP_ID SCP with ATTACH_SCP_ID SCP defined in the associated environment variables
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
from aws_assume_role_lib import (  # pylint: disable=import-error
    assume_role,
    generate_lambda_session_name,
)
from botocore.exceptions import ClientError

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

ASSUME_ROLE_NAME = os.environ.get("ASSUME_ROLE_NAME", "OrganizationAccountAccessRole")
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

    assume_role_arn = f"arn:{get_partition()}:iam::{account_id}:role/{ASSUME_ROLE_NAME}"

    replace_scp(assume_role_arn, account_id)


def replace_scp(assume_role_arn, account_id):
    """Replace scp policy from either a lambda or main method."""
    org_client = get_boto3_clients(assume_role_arn, account_id)

    org_client.detach_policy(
        PolicyId=DETACH_SCP_ID,
        TargetId=account_id
    )

    org_client.attach_policy(
        PolicyId=ATTACH_SCP_ID,
        TargetId=account_id
    )



def get_boto3_clients(assume_role_arn, account_id):
    """Get the organization client."""
    # Assume the session
    assumed_role_session = get_assumed_role_session(account_id, assume_role_arn)
    # Create the organization client
    org_client = assumed_role_session.client("organizations")
    return org_client


def get_new_account_id(event):
    """Return account id for new account events."""
    return event["detail"]["serviceEventDetails"]["createAccountStatus"]["accountId"]


def get_invite_account_id(event):
    """Return account id for invite account events."""
    return event["detail"]["requestParameters"]["target"]["id"]


def get_account_id(event):
    """Return account id for supported events."""
    event_name = event["detail"]["eventName"]
    get_account_id_strategy = {
        "CreateAccountResult": get_new_account_id,
        "InviteAccountToOrganization": get_invite_account_id,
    }
    return get_account_id_strategy[event_name](event)


def get_assumed_role_session(account_id, role_arn):
    """Get boto3 session."""
    function_name = os.environ.get(
        "AWS_LAMBDA_FUNCTION_NAME", os.path.basename(__file__)
    )

    role_session_name = generate_lambda_session_name(function_name)

    # Assume the session
    assumed_role_session = assume_role(
        SESSION, role_arn, RoleSessionName=role_session_name, validate=False
    )
    # do stuff with the assumed role using assumed_role_session
    log.debug(
        "Assumed identity for account %s is %s",
        account_id,
        assumed_role_session.client("sts").get_caller_identity()["Arn"],
    )
    return assumed_role_session


def get_partition():
    """Return AWS partition."""
    sts = boto3.client("sts")
    return sts.get_caller_identity()["Arn"].split(":")[1]


def cli_main(target_account_id, assume_role_arn=None, assume_role_name=None):
    """Process cli assume_role_name arg and pass to main."""
    log.debug(
        "CLI - target_account_id=%s assume_role_arn=%s assume_role_name=%s",
        target_account_id,
        assume_role_arn,
        assume_role_name,
    )

    if assume_role_name:
        assume_role_arn = (
            f"arn:{get_partition()}:iam::{target_account_id}:role/{assume_role_name}"
        )
        log.info("assume_role_arn for provided role name is '%s'", assume_role_arn)

    main(target_account_id, assume_role_arn)


def main(target_account_id, assume_role_arn):
    """Assume role and replace default scp."""
    log.debug(
        "Main identity is %s",
        SESSION.client("sts").get_caller_identity()["Arn"],
    )

    replace_scp(
        assume_role_arn,
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
        mut_x_group = parser.add_mutually_exclusive_group(required=True)
        mut_x_group.add_argument(
            "--assume-role-arn",
            type=str,
            help="ARN of IAM role to assume in the target account (case sensitive)",
        )
        mut_x_group.add_argument(
            "--assume-role-name",
            type=str,
            help="Name of IAM role to assume in the target account (case sensitive)",
        )

        return parser.parse_args()

    sys.exit(cli_main(**vars(create_args())))
