
output "role_arn" {
    description = "The ARN of the IAM role"
    value       = aws_iam_role.EC2_Role.arn
}

output "role_name" {
    description = "The name of the IAM role"
    value       = aws_iam_role.EC2_Role.name
}

output "instance_profile_name" {
    description = "The name of the IAM instance profile"
    value       = aws_iam_instance_profile.instance_profile.name
}