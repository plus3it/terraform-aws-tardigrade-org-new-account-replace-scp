# terraform-aws-tardigrade-org-new-account-replace-scp

A Terraform module to replace one scp with with another SCP for an account

The Lambda function is triggered for the account by an Event Rule that matches
the CreateAccountResult or InviteAccountToOrganization events. The function then
replaces the default policy for that account.

<!-- BEGIN TFDOCS -->
<!-- END TFDOCS -->

## CLI Option

Steps to run via the CLI

1. Install and configure aws cli.
2. Set AWS_PROFILE and AWS_DEFAULT_REGION (account and region that can assume the role and run commands from)
3. Review the options for the script and run

### Script Options

```bash
Supported Environment Variables:
    'LOG_LEVEL': defaults to 'info'
        - set the desired log level ('error', 'warning', 'info' or 'debug')

    'DRY_RUN': defaults to 'true'
        - set whether actions should be simulated or live
        - value of 'true' (case insensitive) will be simulated.

    'DETACH_SCP_ID':
        -sets id of the policy to detach

    'ATTACH_SCP_ID':
        -sets id of the new policy to attach

options:
  -h, --help            show this help message and exit

required arguments:
  --target-account-id TARGET_ACCOUNT_ID
                        Account number to delete default VPC resources in

  --assume-role-arn ASSUME_ROLE_ARN
                        ARN of IAM role to assume in the target account (case sensitive)
  OR
  --assume-role-name ASSUME_ROLE_NAME
                        Name of IAM role to assume in the target account (case sensitive)

usage: replace_scp.py [-h] --target-account-id TARGET_ACCOUNT_ID (--assume-role-arn ASSUME_ROLE_ARN | --assume-role-name ASSUME_ROLE_NAME)
```

### Sample steps to execute in venv

```bash
mkdir vpc_env
python3 -m venv vpc_env
source vpc_env/bin/activate
python3 -m pip install -U pip
pip3 install -r src/requirements.txt
python3 src/replace_scp.py --target-account-id=<TARGET ACCT ID> (--assume-role-arn=<ROLE ARN TO ASSUME> | --assume-role-name=<ROLE NAME TO ASSUME>)
deactivate
rm -rf vpc_env
```
