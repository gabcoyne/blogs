

module "batch_queue" {
  source = "../modules/batch-job-queue"

  vpc_id             = "VPC_ID"
  queue_name         = "whalesay-queue"
  environment        = "dev"
  instance_type      = ["m5"]
  min_cpus           = 0
  max_cpus           = 2
  private_subnet_ids = ["SUBNET_ID"] #module.network.private_subnets_ids
  tags = {
    "Name"     = "whalesay"
    "Platform" = "awsbatch",
    "Pipeline" = "whalesay-head"
  }
}

module "whalesay_batch_job" {
  source = "../modules/batch-job-definition"

  job_definition_name = "whalesay"
  environment         = var.environment

  container_properties = file("../${path.module}/batch-job-files/whalesay.json")

  tags = {
    "Platform" = "awsbatch",
    "Pipeline" = "whalesay"
  }
}
