


data "aws_iam_policy_document" "EC2_Assume_Role_Policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "CloudWatch_Logs_Policy" {
    statement {
        effect = "Allow"

        actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ]

        resources = ["arn:aws:logs:*:*:*"]
    }
}

resource "aws_iam_role" "EC2_Role" {
  name               = var.role_name
  assume_role_policy = data.aws_iam_policy_document.EC2_Assume_Role_Policy.json
  description        = "IAM Role for EC2 instances to access AWS services"

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_iam_role_policy" "cloudwatch_logs" {
    name_prefix = "${var.project_name}-cloudwatch"
    role        = aws_iam_role.EC2_Role.id
    policy      = data.aws_iam_policy_document.CloudWatch_Logs_Policy.json
}

resource "aws_iam_instance_profile" "instance_profile" {
    name = var.instance_profile_name
    role = aws_iam_role.EC2_Role.name
}