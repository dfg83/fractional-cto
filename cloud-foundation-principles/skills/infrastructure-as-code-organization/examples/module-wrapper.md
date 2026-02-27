# Example: Module Wrapper Patterns

## Pattern: Wrapping a Community Module

Instead of reimplementing VPC logic, wrap the community module with your organization's smart defaults, validation, and standard outputs.

### Module Structure

```
tf-module-ecs-service/
├── main.tf          <- Wraps community ECS module
├── variables.tf     <- Smart defaults with validation
├── outputs.tf       <- Lookup-style outputs with natural keys
├── versions.tf      <- Pinned provider and Terraform versions
└── locals.tf        <- Complex transformations
```

### variables.tf -- Smart Defaults and Validation

```hcl
variable "name" {
  type        = string
  description = "Name of the ECS service"
}

variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "containers" {
  type = list(object({
    name   = string
    image  = string
    cpu    = number
    memory = number
    port   = optional(number, 8080)

    # Sensible defaults reduce boilerplate for consumers
    health_check_path    = optional(string, "/health")
    health_check_matcher = optional(string, "200")
    environment_vars     = optional(map(string), {})
  }))

  validation {
    condition     = length(var.containers) > 0
    error_message = "At least one container must be defined."
  }
}

variable "desired_count" {
  type        = number
  default     = 2
  description = "Number of task instances. Set to 0 to stop the service."
}

variable "enable_autoscaling" {
  type    = bool
  default = true
}

variable "autoscaling_min" {
  type    = number
  default = 2
}

variable "autoscaling_max" {
  type    = number
  default = 10
}

variable "cpu_target" {
  type        = number
  default     = 70
  description = "CPU utilization target for autoscaling. Set to -1 to disable CPU-based scaling."
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "security_group_ids" {
  type = list(string)
}

variable "cluster_arn" {
  type = string
}
```

### locals.tf -- Complex Logic in Locals

```hcl
locals {
  # Calculate total CPU/memory from container definitions
  total_cpu    = sum([for c in var.containers : c.cpu])
  total_memory = sum([for c in var.containers : c.memory])

  # Flatten container port mappings for target group creation
  container_ports = {
    for c in var.containers :
    "${c.name}-${c.port}" => {
      container_name       = c.name
      container_port       = c.port
      health_check_path    = c.health_check_path
      health_check_matcher = c.health_check_matcher
    }
  }

  # Determine whether to create autoscaling resources
  create_cpu_scaling = var.enable_autoscaling && var.cpu_target >= 0
}
```

### main.tf -- Wrapping the Community Module

```hcl
# Wrap the community ECS service module
module "ecs_service" {
  source  = "terraform-aws-modules/ecs/aws//modules/service"
  version = "~> 5.0"

  name        = var.name
  cluster_arn = var.cluster_arn

  # Bridge: calculate from container definitions
  cpu    = local.total_cpu
  memory = local.total_memory

  # Network configuration from shared infrastructure
  network_mode = "awsvpc"
  subnet_ids   = var.subnet_ids

  security_group_ids = var.security_group_ids

  # Deployment: zero-downtime rolling updates
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  deployment_circuit_breaker = {
    enable   = true
    rollback = true
  }

  # Capacity strategy: mix on-demand and spot
  capacity_provider_strategy = {
    fargate = {
      capacity_provider = "FARGATE"
      weight            = 50
      base              = 1   # At least one on-demand task
    }
    fargate_spot = {
      capacity_provider = "FARGATE_SPOT"
      weight            = 50
    }
  }

  desired_count = var.desired_count

  tags = var.tags
}

# Target groups for each container port
resource "aws_lb_target_group" "this" {
  for_each = local.container_ports

  name_prefix = substr(replace(each.key, "/[^a-zA-Z0-9]/", ""), 0, 6)
  port        = each.value.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path    = each.value.health_check_path
    matcher = each.value.health_check_matcher
  }

  tags = var.tags
}

# Conditional autoscaling
resource "aws_appautoscaling_target" "this" {
  count = var.enable_autoscaling ? 1 : 0

  max_capacity       = var.autoscaling_max
  min_capacity       = var.autoscaling_min
  resource_id        = "service/${split("/", var.cluster_arn)[1]}/${var.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu" {
  count = local.create_cpu_scaling ? 1 : 0

  name               = "${var.name}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.this[0].resource_id
  scalable_dimension = aws_appautoscaling_target.this[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.this[0].service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = var.cpu_target

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}
```

### outputs.tf -- Lookup-Style Outputs

```hcl
# Export as lookups keyed by natural identifiers, not indices
output "target_groups" {
  description = "Map of container target groups keyed by name-port"
  value = {
    for key, tg in aws_lb_target_group.this :
    key => {
      arn  = tg.arn
      name = tg.name
      port = tg.port
    }
  }
}

output "service_name" {
  description = "Name of the ECS service"
  value       = module.ecs_service.name
}

output "service_id" {
  description = "ARN of the ECS service"
  value       = module.ecs_service.id
}
```

### Consumer Usage

```hcl
# In a service repo: infrastructure/dev/main.tf
module "api_service" {
  source = "github.com/myorg/tf-module-ecs-service.git?ref=v2.1.0"

  name        = "${local.prefix}api"
  environment = "dev"
  cluster_arn = data.terraform_remote_state.compute.outputs.cluster_arn
  vpc_id      = data.terraform_remote_state.network.outputs.vpc_id
  subnet_ids  = data.terraform_remote_state.network.outputs.private_subnet_ids
  security_group_ids = [
    data.terraform_remote_state.security.outputs.sg_private_8080_id
  ]

  containers = [
    {
      name   = "api"
      image  = "${var.ecr_repo}:${var.git_sha}"
      cpu    = 512
      memory = 1024
      port   = 8080
      environment_vars = {
        DATABASE_URL = data.aws_secretsmanager_secret_version.db.secret_string
        LOG_LEVEL    = "info"
      }
    }
  ]

  # Autoscaling with CPU target
  enable_autoscaling = true
  autoscaling_min    = 2
  autoscaling_max    = 8
  cpu_target         = 70

  tags = local.tags
}
```

## Version Pinning Strategy

```
v1.0.0  <- Initial release
v1.1.0  <- Add health check customization (backward compatible)
v1.2.0  <- Add autoscaling support (backward compatible)
v2.0.0  <- Change container variable structure (BREAKING)
v2.1.0  <- Add spot capacity provider option (backward compatible)
```

- Consumers pin to specific versions (`?ref=v2.1.0`)
- Major versions signal breaking changes
- Never reference "latest" or an untagged branch
