# AWS Region variable
variable "aws_region" {
    description     = "AWS region to deploy resources in"
    type            = string
    default         = "us-east-1"
}


# Variables for EC2 module
variable "instance_type" {
    description     = "EC2 Instance Type"
    type            = string
    default         = "t2.micro"
}

variable "ami" {
    description     = "AMI ID for the EC2 instance"
    type            = string
}

variable "key_name" {
    description     = "Key pair name for the EC2 instance"
    type            = string
}

variable "subnet_id" {
    description     = "Subnet ID for the EC2 instance"
    type            = string
}

variable "iam_instance_profile_name" {
    description     = "IAM Instance Profile name to attach to the EC2 instance"
    type            = string
    default         = null
}
