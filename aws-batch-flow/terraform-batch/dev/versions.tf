terraform {
  required_version = ">= 0.13"
  required_providers {
    aws = ">= 3.6.0"
  }
  #   backend "s3" {
  #     bucket         = "proteona-dev-terraform-state-ap-southeast-1"
  #     key            = "terraform-state.tfstate"
  #     region         = "ap-southeast-1"
  #     dynamodb_table = "terraform-dev-lock"
  #     profile        = "proteona"
  #   }
}
