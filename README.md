# terraform-aws-tardigrade-org-new-account-replace-scp

A Terraform module to replace one scp with with another SCP for an account

The Lambda function is triggered for the account by an Event Rule that matches
the CreateAccountResult or InviteAccountToOrganization events. The function then
replaces the default policy for that account.

<!-- BEGIN TFDOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.3 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.9 |
| <a name="requirement_external"></a> [external](#requirement\_external) | >= 1.0 |
| <a name="requirement_local"></a> [local](#requirement\_local) | >= 1.0 |
| <a name="requirement_null"></a> [null](#requirement\_null) | >= 2.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 4.9 |

## Resources

| Name | Type |
|------|------|
| [aws_iam_policy_document.lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_partition.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/partition) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_attach_scp_id"></a> [attach\_scp\_id](#input\_attach\_scp\_id) | ID of the SCP to attach | `string` | n/a | yes |
| <a name="input_detach_scp_id"></a> [detach\_scp\_id](#input\_detach\_scp\_id) | ID of the SCP to detach | `string` | n/a | yes |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | Project name to prefix resources with | `string` | n/a | yes |
| <a name="input_event_bus_name"></a> [event\_bus\_name](#input\_event\_bus\_name) | Event bus name to create event rules in | `string` | `"default"` | no |
| <a name="input_event_types"></a> [event\_types](#input\_event\_types) | Event types that will trigger this lambda | `set(string)` | <pre>[<br>  "CreateAccountResult",<br>  "InviteAccountToOrganization",<br>  "CreateOrganizationalUnit"<br>]</pre> | no |
| <a name="input_lambda"></a> [lambda](#input\_lambda) | Object of optional attributes passed on to the lambda module | <pre>object({<br>    artifacts_dir            = optional(string, "builds")<br>    build_in_docker          = optional(bool, false)<br>    create_package           = optional(bool, true)<br>    ephemeral_storage_size   = optional(number)<br>    ignore_source_code_hash  = optional(bool, true)<br>    local_existing_package   = optional(string)<br>    memory_size              = optional(number, 128)<br>    recreate_missing_package = optional(bool, false)<br>    runtime                  = optional(string, "python3.8")<br>    s3_bucket                = optional(string)<br>    s3_existing_package      = optional(map(string))<br>    s3_prefix                = optional(string)<br>    store_on_s3              = optional(bool, false)<br>    timeout                  = optional(number, 300)<br>  })</pre> | `{}` | no |
| <a name="input_log_level"></a> [log\_level](#input\_log\_level) | Log level for lambda | `string` | `"INFO"` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags for resource | `map(string)` | `{}` | no |

## Outputs

No outputs.

<!-- END TFDOCS -->

## CLI Option

Steps to run via the CLI

1. Install and configure aws cli.
2. Set AWS_PROFILE and AWS_DEFAULT_REGION (account and region that can run commands to attach and detach organizational policies)
3. Review the options for the script and run

### Script Options

```bash
Supported Environment Variables:
    'LOG_LEVEL': defaults to 'info'
        - set the desired log level ('error', 'warning', 'info' or 'debug')

    'DETACH_SCP_ID':
        -sets id of the policy to detach

    'ATTACH_SCP_ID':
        -sets id of the new policy to attach

options:
  -h, --help            show this help message and exit

required arguments:
  --target-id TARGET_ID
                        Target ID to replace policy in

usage: replace_scp.py [-h] --target-account-id TARGET_ACCOUNT_ID
```

### Sample steps to execute in venv

```bash
mkdir vpc_env
python3 -m venv vpc_env
source vpc_env/bin/activate
python3 -m pip install -U pip
pip3 install -r src/requirements.txt
python3 src/replace_scp.py --target-id=<TARGET ID>
deactivate
rm -rf vpc_env
```
