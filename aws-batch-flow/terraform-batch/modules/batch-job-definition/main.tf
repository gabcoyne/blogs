resource "aws_batch_job_definition" "job" {
  name = var.job_definition_name
  type = "container"

  platform_capabilities = var.platform_capabilities

  container_properties = var.container_properties

  tags = merge({
    "managed-by" = "terraform"
    environment  = var.environment
    },
  var.tags)
}

resource "aws_cloudwatch_log_group" "awslogs" {
  name = var.job_definition_name
}