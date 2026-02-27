# Labels Module Usage -- Practical Patterns

How services consume the labels module for naming storage buckets, databases, compute clusters, IAM roles, and more.

## Basic Setup (Every Project Starts Here)

```hcl
# main.tf -- Import labels once, use everywhere

module "labels" {
  source      = "git::https://github.com/myorg/tf-module-labels.git?ref=v1.0.0"
  team        = "eng"
  env         = var.environment   # "dev" or "prod" from tfvars
  name        = "backend"
  cost_center = "business_logic"
  scope       = "g"
}

locals {
  tags = module.labels.tags
  prf  = module.labels.prefix   # "eng-dev-g-backend-" or "eng-prod-g-backend-"
}
```

## Storage Buckets

```hcl
resource "aws_s3_bucket" "data" {
  bucket = "${local.prf}data"       # eng-dev-g-backend-data
  tags   = local.tags
}

resource "aws_s3_bucket" "logs" {
  bucket = "${local.prf}logs"       # eng-dev-g-backend-logs
  tags   = local.tags
}

resource "aws_s3_bucket" "artifacts" {
  bucket = "${local.prf}artifacts"  # eng-dev-g-backend-artifacts
  tags   = local.tags
}
```

## Databases

```hcl
resource "aws_db_instance" "main" {
  identifier = "${local.prf}db"     # eng-dev-g-backend-db
  tags       = local.tags

  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.medium"
  allocated_storage    = 50
  db_name              = "app"
  username             = "app_rw"
  manage_master_user_password = true
}

resource "aws_elasticache_replication_group" "cache" {
  replication_group_id = "${local.prf}cache"  # eng-dev-g-backend-cache
  description          = "Redis cache for ${module.labels.name}"
  tags                 = local.tags

  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_clusters   = 2
}
```

## Compute (ECS)

```hcl
resource "aws_ecs_cluster" "main" {
  name = "${local.prf}cluster"      # eng-dev-g-backend-cluster
  tags = local.tags

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_service" "api" {
  name            = "${local.prf}api"  # eng-dev-g-backend-api
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 2
  tags            = local.tags
}
```

## IAM Roles

```hcl
resource "aws_iam_role" "task_execution" {
  name = "${local.prf}task-exec"    # eng-dev-g-backend-task-exec
  tags = local.tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role" "task" {
  name = "${local.prf}task"         # eng-dev-g-backend-task
  tags = local.tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}
```

## Security Groups

```hcl
resource "aws_security_group" "app" {
  name        = "${local.prf}app-sg"         # eng-dev-g-backend-app-sg
  description = "Application traffic for ${module.labels.name}"
  vpc_id      = var.vpc_id
  tags        = local.tags
}

resource "aws_security_group" "db" {
  name        = "${local.prf}db-sg"          # eng-dev-g-backend-db-sg
  description = "Database access for ${module.labels.name}"
  vpc_id      = var.vpc_id
  tags        = local.tags
}
```

## Log Groups (Slash-Separated)

```hcl
# Log groups use slashes for hierarchy -- deliberate deviation from dash naming
resource "aws_cloudwatch_log_group" "app" {
  name              = "/${module.labels.team}/${module.labels.env}/ecs/${module.labels.name}"
  retention_in_days = var.environment == "prod" ? 90 : 30
  tags              = local.tags
}

# Result: /eng/dev/ecs/backend  or  /eng/prod/ecs/backend
```

## Terraform State Bucket

```hcl
# State bucket naming follows the same convention
resource "aws_s3_bucket" "tfstate" {
  bucket = "${module.labels.team}-${module.labels.env}-g-tfstate"
  tags   = local.tags
  # Result: eng-dev-g-tfstate
}

resource "aws_dynamodb_table" "tfstate_lock" {
  name     = "${module.labels.team}-${module.labels.env}-g-tfstate-lock"
  tags     = local.tags
  # Result: eng-dev-g-tfstate-lock

  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

## GCP Equivalent

```hcl
# GCP uses labels instead of tags, but the pattern is identical

module "labels" {
  source      = "git::https://github.com/myorg/tf-module-labels.git?ref=v1.0.0"
  team        = "eng"
  env         = var.environment
  name        = "api"
  cost_center = "compute"
  scope       = "g"
}

resource "google_storage_bucket" "data" {
  name     = "${module.labels.prefix}data"   # eng-prod-g-api-data
  location = var.region
  labels   = module.labels.tags              # GCP calls them "labels"
}

resource "google_sql_database_instance" "main" {
  name             = "${module.labels.prefix}db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro"
    user_labels = module.labels.tags
  }
}
```

## Anti-Pattern: Hand-Crafted Names

```hcl
# DO NOT DO THIS -- inconsistent, no validation, no traceability

resource "aws_s3_bucket" "data" {
  bucket = "my-app-data-bucket"     # No team, no env, no cost center
  tags = {
    Name = "Data Bucket"            # Tells you nothing useful
  }
}

resource "aws_s3_bucket" "logs" {
  bucket = "prod-logs-2026"         # Different pattern than above
  tags = {
    Environment = "Production"      # Capital P -- inconsistent with "prod" elsewhere
    CostCenter  = "Infrastructure"  # Not from approved list
  }
}
```

These names tell you nothing about ownership, cannot be queried consistently, and will never appear correctly in cost reports.
