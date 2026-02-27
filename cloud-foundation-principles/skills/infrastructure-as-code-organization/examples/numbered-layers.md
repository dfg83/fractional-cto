# Example: Numbered Layer Repository Structure

## Directory Layout

```
infra-global/
├── 00_network/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── backend.tf
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── backend.tf
├── 10_security/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── backend.tf
│   └── prod/
│       └── ...
├── 30_databases/
│   ├── dev/
│   └── prod/
├── 40_compute/
│   ├── dev/
│   └── prod/
├── 70_monitoring/
│   ├── dev/
│   └── prod/
└── 90_shared_services/
    ├── dev/
    └── prod/
```

## Backend Configuration (00_network/dev/backend.tf)

```hcl
terraform {
  backend "s3" {
    bucket         = "myorg-dev-tfstate"
    key            = "network"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "myorg-dev-tflock"
  }
}
```

## Network Layer (00_network/dev/main.tf)

```hcl
terraform {
  required_version = ">= 1.8.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = local.tags
  }
}

# Labels module -- single source of truth for naming and tagging
module "labels" {
  source      = "github.com/myorg/tf-module-labels.git?ref=v1.3.0"
  team        = "platform"
  env         = "dev"
  name        = "network"
  cost_center = "platform"
}

locals {
  tags   = module.labels.tags
  prefix = module.labels.prf
}

# VPC -- wrapping the community module
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.19.0"

  name = "${local.prefix}vpc"
  cidr = "10.0.0.0/16"

  azs                = ["${var.region}a", "${var.region}b", "${var.region}c"]
  public_subnets     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnets    = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
  database_subnets   = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]
  elasticache_subnets = ["10.0.31.0/24", "10.0.32.0/24", "10.0.33.0/24"]

  enable_dns_hostnames = true
  enable_dns_support   = true

  # Cost optimization: single NAT at startup scale
  enable_nat_gateway = true
  single_nat_gateway = true

  tags = local.tags
}
```

## Network Outputs (00_network/dev/outputs.tf)

```hcl
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = module.vpc.private_subnets
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = module.vpc.public_subnets
}

output "database_subnet_ids" {
  description = "List of database subnet IDs"
  value       = module.vpc.database_subnets
}

output "database_subnet_group_name" {
  description = "Name of the database subnet group"
  value       = module.vpc.database_subnet_group_name
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}
```

## Compute Layer Reading Network State (40_compute/dev/main.tf)

```hcl
terraform {
  required_version = ">= 1.8.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = local.tags
  }
}

# Cross-layer state reference: compute reads from network
data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "myorg-dev-tfstate"
    key    = "network"
    region = var.region
  }
}

# Cross-layer state reference: compute reads from security
data "terraform_remote_state" "security" {
  backend = "s3"
  config = {
    bucket = "myorg-dev-tfstate"
    key    = "security"
    region = var.region
  }
}

module "labels" {
  source      = "github.com/myorg/tf-module-labels.git?ref=v1.3.0"
  team        = "platform"
  env         = "dev"
  name        = "compute"
  cost_center = "platform"
}

locals {
  tags   = module.labels.tags
  prefix = module.labels.prf
}

# ECS cluster using outputs from lower layers
module "ecs_cluster" {
  source  = "terraform-aws-modules/ecs/aws//modules/cluster"
  version = "~> 5.0"

  cluster_name = "${local.prefix}cluster"

  fargate_capacity_providers = {
    FARGATE = {
      default_capacity_provider_strategy = {
        weight = 50
      }
    }
    FARGATE_SPOT = {
      default_capacity_provider_strategy = {
        weight = 50
      }
    }
  }

  tags = local.tags
}
```

## State Bucket Bootstrap (run once per account)

```hcl
# bootstrap/main.tf -- run manually before any other Terraform
resource "aws_s3_bucket" "tfstate" {
  bucket = "myorg-${var.environment}-tfstate"

  tags = {
    purpose     = "terraform-state"
    environment = var.environment
    managed_by  = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "tflock" {
  name         = "myorg-${var.environment}-tflock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    purpose     = "terraform-lock"
    environment = var.environment
    managed_by  = "terraform"
  }
}
```
