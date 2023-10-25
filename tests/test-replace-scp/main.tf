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

resource "random_string" "id" {
  length  = 6
  upper   = false
  special = false
  numeric = false
}
