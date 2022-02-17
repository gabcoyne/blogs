variable "environment" {
  type = string
}
variable "vpc_id" {
  type = string
}
variable "instance_type" {
  type = list(string)
}
variable "private_subnet_ids" {
  type = list(string)
}
variable "queue_name" {
  type = string
}
variable "max_cpus" {
  type    = number
  default = 256
}
variable "min_cpus" {
  type    = number
  default = 0
}
variable "tags" {
  type    = map(any)
  default = {}
}
variable "allocation_strategy" {
  type    = string
  default = "BEST_FIT_PROGRESSIVE"
}
variable "image_type" {
  type    = string
  default = "ECS_AL2"
}