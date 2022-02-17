resource "aws_s3_bucket" "bucket" {
  bucket = "proteona-${var.environment}-terraform-state-ap-southeast-1"

  versioning {
    enabled = true
  }
}

resource "aws_dynamodb_table" "terraform_state_lock" {
  name           = "terraform-${var.environment}-lock"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
}