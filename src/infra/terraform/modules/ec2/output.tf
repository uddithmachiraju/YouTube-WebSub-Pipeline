output "instance_id" {
    description = "The public IP address of the EC2 instance"
    value       = aws_instance.WebSub.id
}

output "private_ip" {
    description = "The private IP address of the EC2 instance"
    value       = aws_instance.WebSub.private_ip
}

output "public_ip" {
    description = "The public IP address of the EC2 instance"
    value       = aws_instance.WebSub.public_ip
}

output "instance_arn" {
    description = "The ARN of the EC2 instance"
    value       = aws_instance.WebSub.arn
}

