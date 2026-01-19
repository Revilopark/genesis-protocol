provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "genesis-protocol"
      Environment = "staging"
      ManagedBy   = "terraform"
    }
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "name" {
  description = "Project name"
  type        = string
  default     = "genesis"
}

# VPC (smaller for staging)
module "vpc" {
  source      = "../../modules/vpc"
  name        = "${var.name}-staging"
  environment = "staging"
  vpc_cidr    = "10.1.0.0/16"
  availability_zones = [
    "${var.aws_region}a",
    "${var.aws_region}b"
  ]
}

# EKS Cluster (smaller for staging)
module "eks" {
  source             = "../../modules/eks"
  name               = "${var.name}-staging"
  environment        = "staging"
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  kubernetes_version = "1.29"
}

# ECR Repositories (shared with production)
# In a real setup, you might share ECR repos or have separate ones

# S3 Buckets
module "s3" {
  source      = "../../modules/s3"
  name        = var.name
  environment = "staging"
}

# Outputs
output "vpc_id" {
  value = module.vpc.vpc_id
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "content_bucket_name" {
  value = module.s3.content_bucket_name
}
