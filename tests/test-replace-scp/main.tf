locals {

  project = "test-replace-scp-${random_string.id.result}"

  tags = {
    "project" = local.project
  }
}

module "replace_scp" {
  source        = "../../"
  project_name  = local.project
  detach_scp_id = "p-detach"
  attach_scp_id = "p-attach"
  dry_run       = true
  log_level     = "DEBUG"
  tags          = local.tags
}


data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}

resource "random_string" "id" {
  length  = 6
  upper   = false
  special = false
  numeric = false
}
