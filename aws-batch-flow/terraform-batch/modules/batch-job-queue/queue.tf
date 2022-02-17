resource "aws_batch_job_queue" "queue" {
  name     = var.queue_name
  state    = "ENABLED"
  priority = 1
  compute_environments = [
    aws_batch_compute_environment.batch.arn
  ]

  tags = {
    Name         = var.queue_name
    "managed-by" = "terraform"
    environment  = var.environment
  }
}