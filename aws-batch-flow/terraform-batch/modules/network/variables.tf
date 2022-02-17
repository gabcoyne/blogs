variable "environment" {
  type = string
}
variable "azs" {
  type = list(string)
}
variable "vpc_cidr" {
  type        = string
  description = "cidr range to assign to VPC"
}
variable "private_subnet_cidrs" {
  type = list(string)
}
variable "public_subnet_cidrs" {
  type = list(string)
}