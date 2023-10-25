locals {
  detach_scp_id = "p-"

  project = "test-replace-scp-${random_string.id.result}"

  tags = {
    "project" = local.project
  }
}

module "test_scp" {
  source   = "./scp"
  scp_name = "${local.project}-policy"
  tags     = local.tags
}

module "replace_scp" {
  source           = "../../"
  project_name     = local.project
  assume_role_name = aws_iam_role.assume_role.name
  detach_scp_id    = local.detach_scp_id
  attach_scp_id    = module.test_scp.scp_id
  dry_run          = true
  log_level        = "DEBUG"
  tags             = local.tags
}


data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}

data "aws_iam_policy_document" "iam_cloudtrail" {
  statement {
    actions = [
      "cloudtrail:DescribeTrails",
      "cloudtrail:GetTrail",
    ]

    resources = [
      "*"
    ]
  }

  statement {
    actions = [
      "cloudtrail:DeleteTrail",
      "cloudtrail:StopLogging"
    ]

    resources = [
      module.test_cloudtrail.cloudtrail_arn
    ]
  }

}

resource "aws_iam_role" "assume_role" {
  name = "${local.project}-replace-scp-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Sid" : "AssumeRoleCrossAccount",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : "arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:root"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })

  inline_policy {
    name   = local.project
    policy = data.aws_iam_policy_document.iam_cloudtrail.json
  }
}

resource "random_string" "id" {
  length  = 6
  upper   = false
  special = false
  numeric = false
}
