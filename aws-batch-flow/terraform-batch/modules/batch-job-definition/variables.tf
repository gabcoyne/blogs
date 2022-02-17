variable "job_definition_name" {
  type = string
}
variable "platform_capabilities" {
  type    = list(string)
  default = ["EC2"]
}
variable "container_properties" {
  type = string
}
variable "environment" {
  type = string
}
variable "tags" {
  type    = map(any)
  default = {}
}