##############################
# Lambda
##############################
module "lambda" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git?ref=v6.0.1"

  function_name = "${var.project_name}-replace-scp"

  description = "Lambda function replacing detach_scp_id with attach_scp_id"
  handler     = "replace_scp.lambda_handler"
  tags        = var.tags

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda.json

  artifacts_dir            = var.lambda.artifacts_dir
  build_in_docker          = var.lambda.build_in_docker
  create_package           = var.lambda.create_package
  ephemeral_storage_size   = var.lambda.ephemeral_storage_size
  ignore_source_code_hash  = var.lambda.ignore_source_code_hash
  local_existing_package   = var.lambda.local_existing_package
  recreate_missing_package = var.lambda.recreate_missing_package
  runtime                  = var.lambda.runtime
  s3_bucket                = var.lambda.s3_bucket
  s3_existing_package      = var.lambda.s3_existing_package
  s3_prefix                = var.lambda.s3_prefix
  store_on_s3              = var.lambda.store_on_s3
  timeout                  = var.lambda.timeout

  environment_variables = {
    ATTACH_SCP_ID = var.attach_scp_id
    DETACH_SCP_ID = var.detach_scp_id
    DRY_RUN       = var.dry_run
    LOG_LEVEL     = var.log_level
  }

  source_path = [
    {
      path             = "${path.module}/src"
      pip_requirements = true
      patterns         = ["!\\.terragrunt-source-manifest"]
    }
  ]

}

data "aws_iam_policy_document" "lambda" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }

  statement {
    effect = "Allow"
    actions = [
      "organizations:DetachPolicy",
      "organizations:AttachPolicy"
    ]

    resources = ["*"]
  }

}


##############################
# Events
##############################
locals {
  lambda_name = module.lambda.lambda_function_name

  event_types = {
    CreateAccount = jsonencode(
      {
        "detail" : {
          "eventSource" : ["organizations.amazonaws.com"],
          "eventName" : ["CreateAccount"]
        }
      }
    )
    CreateGovCloudAccount = jsonencode(
      {
        "detail" : {
          "eventSource" : ["organizations.amazonaws.com"],
          "eventName" : ["CreateGovCloudAccount"]
        }
      }
    )
    CreateOrganizationalUnit = jsonencode(
      {
        "detail" : {
          "eventSource" : ["organizations.amazonaws.com"],
          "eventName" : ["CreateOrganizationalUnit"]
        }
      }
    )
    InviteAccountToOrganization = jsonencode(
      {
        "detail" : {
          "eventSource" : ["organizations.amazonaws.com"],
          "eventName" : ["InviteAccountToOrganization"]
        }
      }
    )
  }
}

resource "aws_cloudwatch_event_rule" "this" {
  for_each = var.event_types

  name           = "${var.project_name}-${each.value}"
  description    = "Managed by Terraform"
  event_pattern  = local.event_types[each.value]
  event_bus_name = var.event_bus_name
  tags           = var.tags
}

resource "aws_cloudwatch_event_target" "this" {
  for_each = aws_cloudwatch_event_rule.this

  rule = each.value.name
  arn  = module.lambda.lambda_function_arn
}

resource "aws_lambda_permission" "events" {
  for_each = aws_cloudwatch_event_rule.this

  action        = "lambda:InvokeFunction"
  function_name = module.lambda.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = each.value.arn
}

##############################
# Common
##############################
data "aws_partition" "current" {}
