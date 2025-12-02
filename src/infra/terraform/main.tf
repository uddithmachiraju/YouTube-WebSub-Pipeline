
provider "aws" {
    region = var.aws_region
}

module "EC2" {
    source = "./modules/ec2"

    instance_type = var.instance_type
    ami           = var.ami
    key_name      = var.key_name
    # subnet_id     = var.subnet_id
}