variable "scp_name" {
  description = "Name of the scp to create"
  type        = string
}

variable "tags" {
  description = "Tags for resource"
  type        = map(string)
  default     = {}
}
