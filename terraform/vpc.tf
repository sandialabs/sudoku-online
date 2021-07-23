locals {
  vpc_cidr = "10.0.0.0/16"
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "3.2.0"

  name = "sudoku_vpc"
  cidr = local.vpc_cidr
  azs  = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = [
    cidrsubnet(local.vpc_cidr, 8, 1),
    cidrsubnet(local.vpc_cidr, 8, 2),
    cidrsubnet(local.vpc_cidr, 8, 5),
  ]
  public_subnets = [
    cidrsubnet(local.vpc_cidr, 8, 3),
    cidrsubnet(local.vpc_cidr, 8, 4),
    cidrsubnet(local.vpc_cidr, 8, 6),
  ]
  enable_dns_hostnames = true
  enable_nat_gateway   = false
  single_nat_gateway   = false

}
