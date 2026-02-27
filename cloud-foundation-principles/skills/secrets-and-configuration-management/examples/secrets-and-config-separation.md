# Secrets and Configuration Separation
#
# Demonstrates the strict separation between:
#   - Secrets (credentials) --> Secrets Manager with KMS + auto-rotation
#   - Configuration (plain values) --> SSM Parameter Store with hierarchy
#
# Both follow the /{environment}/{service}/{key} naming convention.
# IAM policies scope access by environment and service path.

# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "service_name" {
  description = "Service identifier for naming hierarchy"
  type        = string
  default     = "myapp"
}

variable "team" {
  description = "Team identifier for resource naming"
  type        = string
  default     = "acme"
}

variable "vpc_id" {
  description = "VPC ID (passed from network layer via remote state)"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs (passed from network layer)"
  type        = list(string)
}

variable "db_instance_address" {
  description = "Database endpoint address (passed from database layer)"
  type        = string
}

variable "db_instance_port" {
  description = "Database port (passed from database layer)"
  type        = number
  default     = 5432
}

variable "redis_endpoint" {
  description = "Redis endpoint (passed from cache layer)"
  type        = string
}

# ---------------------------------------------------------------------------
# Locals
# ---------------------------------------------------------------------------

locals {
  name_prefix = "${var.team}-${var.environment}"
  secret_path = "/${var.environment}/${var.service_name}"
  config_path = "/${var.environment}/${var.service_name}"
  shared_path = "/${var.environment}/shared"
}

# ---------------------------------------------------------------------------
# KMS Key for Secrets Encryption
# ---------------------------------------------------------------------------

# Customer-managed key -- not the provider default.
# Enables key rotation, cross-account policies, and decryption audit trails.

resource "aws_kms_key" "secrets" {
  description         = "Encryption key for ${var.service_name} secrets in ${var.environment}"
  enable_key_rotation = true

  tags = {
    Environment = var.environment
    Service     = var.service_name
    Purpose     = "secrets-encryption"
  }
}

resource "aws_kms_alias" "secrets" {
  name          = "alias/${local.name_prefix}-${var.service_name}-secrets"
  target_key_id = aws_kms_key.secrets.key_id
}

# ---------------------------------------------------------------------------
# Secrets Manager -- Credentials Only
# ---------------------------------------------------------------------------

# Database password: auto-rotated, KMS-encrypted, never exposed in plaintext

resource "aws_secretsmanager_secret" "db_password" {
  name       = "${local.secret_path}/db-password"
  kms_key_id = aws_kms_key.secrets.arn

  description = "Database password for ${var.service_name} in ${var.environment}"

  tags = {
    Environment = var.environment
    Service     = var.service_name
    Type        = "credential"
    Rotation    = "automatic"
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = "${var.service_name}_readwrite"
    password = random_password.db.result
    host     = var.db_instance_address
    port     = var.db_instance_port
    dbname   = var.service_name
  })

  lifecycle {
    ignore_changes = [secret_string] # After initial creation, rotation manages the value
  }
}

# Auto-rotation: rotates the password every 30 days
resource "aws_secretsmanager_secret_rotation" "db_password" {
  secret_id           = aws_secretsmanager_secret.db_password.id
  rotation_lambda_arn = var.rotation_lambda_arn # Provided by the security/rotation layer

  rotation_rules {
    automatically_after_days = 30
  }
}

# Third-party API key: cannot auto-rotate, documented with manual process
resource "aws_secretsmanager_secret" "stripe_api_key" {
  name       = "${local.secret_path}/stripe-api-key"
  kms_key_id = aws_kms_key.secrets.arn

  description = "Stripe API key for ${var.service_name}. MANUAL ROTATION: quarterly, see runbook."

  tags = {
    Environment = var.environment
    Service     = var.service_name
    Type        = "credential"
    Rotation    = "manual-quarterly"
  }
}

# ---------------------------------------------------------------------------
# SSM Parameter Store -- Configuration Only
# ---------------------------------------------------------------------------

# Database host: plain configuration value, not a credential

resource "aws_ssm_parameter" "db_host" {
  name  = "${local.config_path}/db-host"
  type  = "String"
  value = var.db_instance_address

  description = "Database endpoint for ${var.service_name}"

  tags = {
    Environment = var.environment
    Service     = var.service_name
    Type        = "configuration"
  }
}

resource "aws_ssm_parameter" "db_port" {
  name  = "${local.config_path}/db-port"
  type  = "String"
  value = tostring(var.db_instance_port)

  description = "Database port for ${var.service_name}"

  tags = {
    Environment = var.environment
    Service     = var.service_name
    Type        = "configuration"
  }
}

resource "aws_ssm_parameter" "redis_url" {
  name  = "${local.config_path}/redis-url"
  type  = "String"
  value = "redis://${var.redis_endpoint}:6379"

  description = "Redis connection URL for ${var.service_name}"

  tags = {
    Environment = var.environment
    Service     = var.service_name
    Type        = "configuration"
  }
}

resource "aws_ssm_parameter" "feature_new_checkout" {
  name  = "${local.config_path}/feature-new-checkout"
  type  = "String"
  value = var.environment == "prod" ? "false" : "true"

  description = "Feature flag: new checkout flow"

  tags = {
    Environment = var.environment
    Service     = var.service_name
    Type        = "feature-flag"
  }
}

# Shared configuration: cross-service values readable by all services
resource "aws_ssm_parameter" "vpc_id" {
  name  = "${local.shared_path}/vpc-id"
  type  = "String"
  value = var.vpc_id

  description = "VPC ID for ${var.environment} environment"

  tags = {
    Environment = var.environment
    Service     = "shared"
    Type        = "configuration"
  }
}

resource "aws_ssm_parameter" "private_subnet_ids" {
  name  = "${local.shared_path}/private-subnet-ids"
  type  = "StringList"
  value = join(",", var.private_subnet_ids)

  description = "Private subnet IDs for ${var.environment} environment"

  tags = {
    Environment = var.environment
    Service     = "shared"
    Type        = "configuration"
  }
}

# ---------------------------------------------------------------------------
# ECS Task Definition -- Consuming Secrets and Configuration
# ---------------------------------------------------------------------------

# Secrets: passed as secret references, resolved at runtime by ECS
# Configuration: passed as environment variables (plain values are safe here)

resource "aws_ecs_task_definition" "myapp" {
  family                   = "${local.name_prefix}-${var.service_name}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.task_execution.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([{
    name  = var.service_name
    image = "123456789012.dkr.ecr.eu-west-1.amazonaws.com/${var.service_name}:latest"

    # Secrets: ECS resolves these from Secrets Manager at container start
    secrets = [
      {
        name      = "DB_PASSWORD"
        valueFrom = aws_secretsmanager_secret.db_password.arn
      },
      {
        name      = "STRIPE_API_KEY"
        valueFrom = aws_secretsmanager_secret.stripe_api_key.arn
      }
    ]

    # Configuration: plain values, safe as environment variables
    environment = [
      {
        name  = "DB_HOST"
        value = var.db_instance_address
      },
      {
        name  = "DB_PORT"
        value = tostring(var.db_instance_port)
      },
      {
        name  = "REDIS_URL"
        value = "redis://${var.redis_endpoint}:6379"
      },
      {
        name  = "ENVIRONMENT"
        value = var.environment
      }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/${local.name_prefix}/${var.service_name}"
        "awslogs-region"        = data.aws_region.current.name
        "awslogs-stream-prefix" = var.service_name
      }
    }
  }])
}

# ---------------------------------------------------------------------------
# IAM -- Scoped Access by Environment and Service
# ---------------------------------------------------------------------------

# Task execution role: can read secrets and pull images
resource "aws_iam_role" "task_execution" {
  name = "${local.name_prefix}-${var.service_name}-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

# Scoped to THIS service's secrets only -- not all secrets in the account
resource "aws_iam_role_policy" "task_execution_secrets" {
  name = "secrets-access"
  role = aws_iam_role.task_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:*:*:secret:${local.secret_path}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = [aws_kms_key.secrets.arn]
      }
    ]
  })
}

# Task role: can read configuration parameters
resource "aws_iam_role" "task" {
  name = "${local.name_prefix}-${var.service_name}-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

# Scoped to THIS service's config AND shared config -- not all parameters
resource "aws_iam_role_policy" "task_config" {
  name = "config-access"
  role = aws_iam_role.task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "ssm:GetParameter",
        "ssm:GetParametersByPath"
      ]
      Resource = [
        "arn:aws:ssm:*:*:parameter${local.config_path}/*",
        "arn:aws:ssm:*:*:parameter${local.shared_path}/*"
      ]
    }]
  })
}

# ---------------------------------------------------------------------------
# Supporting Resources
# ---------------------------------------------------------------------------

resource "random_password" "db" {
  length  = 32
  special = false # Avoids connection string escaping issues
}

variable "rotation_lambda_arn" {
  description = "ARN of the secret rotation Lambda (from security layer)"
  type        = string
  default     = "" # Optional: rotation requires a Lambda function
}

data "aws_region" "current" {}

# ---------------------------------------------------------------------------
# Key Points
# ---------------------------------------------------------------------------

# 1. Secrets (db-password, stripe-api-key) are in Secrets Manager with KMS
# 2. Configuration (db-host, redis-url, feature flags) are in SSM Parameter Store
# 3. Both follow /{environment}/{service}/{key} naming hierarchy
# 4. IAM policies scope access to specific environment + service paths
# 5. ECS resolves secrets at runtime via valueFrom (never plaintext in config)
# 6. Database password auto-rotates every 30 days
# 7. Third-party keys that can't auto-rotate are tagged with rotation schedule
# 8. Shared config (/prod/shared/*) is readable by all services in that env
