
# EC2 Module Outputs
output "instance_id" {
    description = "The ID of the EC2 instance"
    value       = module.EC2.instance_id
}

output "private_ip" {
    description = "The private IP address of the EC2 instance"
    value       = module.EC2.private_ip
}

output "public_ip" {
    description = "The public IP address of the EC2 instance"
    value       = module.EC2.public_ip
}

output "instance_arn" {
    description = "The ARN of the EC2 instance"
    value       = module.EC2.instance_arn
}


# IAM Module Outputs
output "role_arn" {
    description = "The ARN of the IAM role"
    value       = module.IAM.role_arn
}

output "role_name" {
    description = "The name of the IAM role"
    value       = module.IAM.role_name
}