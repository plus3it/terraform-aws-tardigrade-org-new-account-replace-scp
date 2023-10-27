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
  log_level     = "DEBUG"
  tags          = local.tags
}

resource "random_string" "id" {
  length  = 6
  upper   = false
  special = false
  numeric = false
}
