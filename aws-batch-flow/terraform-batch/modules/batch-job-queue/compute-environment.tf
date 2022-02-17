resource "aws_iam_role" "ecs" {
  name = "ecs-role"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
    {
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Principal": {
            "Service": "ec2.amazonaws.com"
        }
    }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "ecs" {
  role       = aws_iam_role.ecs.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_instance_profile" "ecs" {
  name = "ecs-instance-profile"
  role = aws_iam_role.ecs.name
}

resource "aws_iam_role" "batch" {
  name = "batch-role"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
    {
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Principal": {
        "Service": "batch.amazonaws.com"
        }
    }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "batch" {
  role       = aws_iam_role.batch.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

resource "aws_security_group" "sg" {
  name   = "batch-compute-environment"
  vpc_id = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name         = "batch-compute-environment"
    "managed-by" = "terraform"
  }
}


resource "aws_batch_compute_environment" "batch" {
  depends_on = [aws_iam_role_policy_attachment.batch]

  compute_environment_name = var.tags["Name"]
  compute_resources {
    instance_role = aws_iam_instance_profile.ecs.arn

    instance_type = var.instance_type

    max_vcpus = var.max_cpus
    min_vcpus = var.min_cpus

    subnets = var.private_subnet_ids
    security_group_ids = [
      aws_security_group.sg.id,
    ]

    allocation_strategy = var.allocation_strategy
    type                = "EC2"

    ec2_configuration {
      image_type = var.image_type
    }
  }

  service_role = aws_iam_role.batch.arn
  type         = "MANAGED"

  tags = merge({
    "managed-by" = "terraform"
    environment  = var.environment
    },
  var.tags)
}