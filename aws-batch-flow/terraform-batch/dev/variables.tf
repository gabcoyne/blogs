variable "environment" {
  type = string
}
# variable "ami_id" {
#   type = string
# }
variable "compute_env_tags" {
  type    = map(any)
  default = {}
}