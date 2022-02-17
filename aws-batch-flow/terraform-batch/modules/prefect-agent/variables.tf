variable "ami_id" {
  type = string
}
variable "environment" {
  type = string
}
variable "vpc_id" {
  type = string
}
variable "private_subnets_ids" {
  type = list(string)
}
variable "min_size" {
  type    = number
  default = 1
}
variable "max_size" {
  type    = number
  default = 1
}
variable "desired_capacity" {
  type    = number
  default = 1
}