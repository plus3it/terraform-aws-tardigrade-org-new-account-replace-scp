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
import os
import sys

from aws_lambda_powertools import Logger
import boto3

# Standard logging config
LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")
LOG = Logger(
    service="new_account_replace_scp",
    level=LOG_LEVEL,
    stream=sys.stderr,
    location="%(name)s.%(funcName)s:%(lineno)d",
    timestamp="%(asctime)s.%(msecs)03dZ",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

ATTACH_SCP_ID = os.environ["ATTACH_SCP_ID"]
DETACH_SCP_ID = os.environ["DETACH_SCP_ID"]

# Get client
org_client = boto3.client("organizations")

@LOG.inject_lambda_context(log_event=True)
def lambda_handler(event, context):  # pylint: disable=unused-argument
    """Replace scp policy lambda handler."""
    account_id = event["detail"]["recipientAccountId"]
    replace_scp(account_id)


def replace_scp(account_id):
    """Replace scp policy from either a lambda or main method."""

    # Determine how many policies are attached, we can have only 5 and must have 1
    response = org_client.list_policies_for_target(
        TargetId=account_id,
        Filter='SERVICE_CONTROL_POLICY',
    )
    num_policies = len(response['Policies'])
    LOG.debug("Account ID %s has %s SCPs", account_id, num_policies)
    if 1 <= num_policies <= 4:
        org_client.attach_policy(PolicyId=ATTACH_SCP_ID, TargetId=account_id)
        org_client.detach_policy(PolicyId=DETACH_SCP_ID, TargetId=account_id)
    else:
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
