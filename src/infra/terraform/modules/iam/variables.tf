
variable "role_name" {
    description     = "The name of the IAM role to be created"
    type            = string
}

variable "environment" {
    description     = "The environment for resource deployment (e.g., dev, staging, prod)"
    type            = string
}

variable "project_name" {
    description     = "The name of the project for resource tagging"
    type            = string
}

variable "instance_profile_name" {
    description     = "The name of the IAM instance profile to be created"
    type            = string
}