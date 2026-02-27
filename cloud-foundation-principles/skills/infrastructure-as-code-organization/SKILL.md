---
name: infrastructure-as-code-organization
description: "This skill should be used when the user is organizing Terraform repositories, designing numbered dependency layers, managing state files, structuring shared modules, or discussing blast radius containment. Covers multi-repo strategy, numbered layer architecture, state-per-layer isolation, module design patterns, cross-layer references, and quality gates."
version: 1.0.0
---

# Layer Your Infrastructure Like You Layer Your Software

A monolithic Terraform state file is a ticking time bomb. One bad `terraform apply` in a 2,000-resource state file can destroy your network, databases, and compute in a single operation. The blast radius is everything. Infrastructure must be organized into numbered dependency layers, each with independent state, so that a failed change to your monitoring stack cannot accidentally delete your VPC.

This principle covers three interlocking concerns: repository architecture (what goes where), numbered layer design (dependency ordering), and module patterns (how to build reusable components). Get these right on day one and your infrastructure scales from 10 to 10,000 resources without structural rewrites.

## Multi-Repository Strategy

Infrastructure code belongs in multiple repositories with clear ownership boundaries. Mixing organization-wide identity management with per-service compute configuration creates coupling that slows every team.

```
Repository 1: infra-root
  Purpose: Organization management, SSO, security delegation
  Scope:   Root/management account, per-account IAM roles

Repository 2: infra-global
  Purpose: Shared infrastructure per environment
  Scope:   Numbered layers (00-90) with env subdirectories

Repository 3+: modules-*
  Purpose: Reusable Terraform modules
  Scope:   Labels, alerts, service templates

Repository N: <service-repos>
  Purpose: Application code + service-specific Terraform
  Scope:   Service owns its own infrastructure
```

**Why separate repos?** Different change cadences. Your network changes quarterly; your compute configuration changes weekly. Coupling them means network reviewers block compute deploys, and compute deploys risk network changes.

## Numbered Layer Architecture

Each layer is a directory with its own Terraform state, its own CI pipeline, and its own blast radius. Lower numbers are prerequisites for higher numbers.

```
infra-global/
├── 00_network/          <- VPCs, subnets, DNS, private connectivity endpoints
│   ├── dev/
│   └── prod/
├── 10_security/         <- Security groups, encryption keys, certificates, WAF
│   ├── dev/
│   └── prod/
├── 20_storage/          <- Object storage, block storage, file systems
│   ├── dev/
│   └── prod/
├── 30_databases/        <- Managed databases, caches, warehouses
│   ├── dev/
│   └── prod/
├── 40_compute/          <- Container clusters, auto-scaling, GPU instances
│   ├── dev/
│   └── prod/
├── 50_edge/             <- CDN, load balancers, WAF rules
│   └── prod/
├── 70_monitoring/       <- Metrics, logging, dashboards, alerting
│   ├── dev/
│   └── prod/
├── 80_ci_cd/            <- Self-hosted runners, build infrastructure
└── 90_shared_services/  <- Bastion hosts, service discovery
    ├── dev/
    └── prod/
```

### Why This Works

| Benefit | Explanation |
|---------|-------------|
| Dependency clarity | Layer 40 (compute) clearly depends on layer 00 (network) and 10 (security) |
| Blast radius containment | Destroying layer 70 (monitoring) cannot affect layer 30 (databases) |
| Independent CI/CD | Each layer gets its own pipeline; network and compute deploy separately |
| Parallelizable | Layers at the same level with no cross-dependencies deploy in parallel |
| Gap numbering | Gaps (20, 60) leave room for future layers without renumbering |

### Cross-Layer State References

Higher layers read outputs from lower layers via remote state. This is the **only** coupling between layers.

```hcl
# In 40_compute/prod/main.tf — reading network outputs
data "terraform_remote_state" "network" {
  backend = "s3"   # or "gcs" or "azurerm"
  config = {
    bucket = "myorg-prod-tfstate"
    key    = "network"
    region = "us-east-1"
  }
}

# Use the outputs
resource "aws_ecs_service" "app" {
  network_configuration {
    subnets = data.terraform_remote_state.network.outputs.private_subnet_ids
  }
}
```

**Dependency chain** (arrows mean "reads from"):
- `40_compute` -> `00_network` + `10_security`
- `30_databases` -> `00_network` + `10_security`
- `70_monitoring` -> `40_compute` + `00_network`
- `90_shared_services` -> `00_network`

## State Management

### One State File Per Layer Per Environment

```
State bucket per account/project:
  myorg-root-tfstate       <- Root/management account
  myorg-dev-tfstate        <- Development account
  myorg-prod-tfstate       <- Production account
  myorg-security-tfstate   <- Security account

State keys within each bucket:
  network          <- 00_network layer
  security         <- 10_security layer
  databases        <- 30_databases layer
  compute          <- 40_compute layer
  monitoring       <- 70_monitoring layer
```

### Mandatory State Properties

| Property | Requirement | Why |
|----------|-------------|-----|
| Encryption | AES-256 at rest | State files contain sensitive outputs (passwords, ARNs, IPs) |
| Versioning | Enabled | Roll back corrupted state without losing history |
| Locking | Enabled | Prevent concurrent applies from corrupting state |
| Public access | Blocked | State files are the keys to your kingdom |

### Bad vs Good: State Organization

```
BAD: One state file for everything
terraform/
├── main.tf        <- 2,000+ resources in one state
└── backend.tf     <- blast radius = everything

GOOD: State per layer per environment
infra-global/
├── 00_network/dev/backend.tf    <- key = "network"    (30 resources)
├── 10_security/dev/backend.tf   <- key = "security"   (15 resources)
├── 30_databases/dev/backend.tf  <- key = "databases"   (8 resources)
└── 40_compute/dev/backend.tf    <- key = "compute"    (25 resources)
```

## Module Design Patterns

### Pattern 1: Wrap Community Modules

Never rebuild what the community maintains. Wrap upstream modules and add your domain logic.

```hcl
# GOOD: Wrap the community VPC module with your defaults
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.19.0"

  name = "${local.prefix}-vpc"
  cidr = var.vpc_cidr

  # Your organization's smart defaults
  enable_dns_hostnames = true
  enable_dns_support   = true
  single_nat_gateway   = true   # Cost optimization for startup scale

  tags = local.tags
}
```

### Pattern 2: Validate at the Boundary

Catch errors at `terraform plan`, not at runtime.

```hcl
variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "cost_center" {
  type = string
  validation {
    condition = contains([
      "platform", "data_pipeline", "observability",
      "api_gateway", "ml_training", "ml_inference", "cicd"
    ], var.cost_center)
    error_message = "Invalid cost_center. Must be from the approved list."
  }
}
```

### Pattern 3: Pin Everything

```hcl
# Custom modules: exact git refs
module "labels" {
  source = "github.com/myorg/tf-module-labels.git?ref=v1.3.0"
}

# Community modules: exact versions
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.19.0"
}

# Providers: pessimistic constraints
terraform {
  required_version = ">= 1.8.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

### Pattern 4: Smart Defaults with Overrides

```hcl
variable "containers" {
  type = list(object({
    name   = string
    image  = string
    cpu    = number
    memory = number
    # Optional with sensible defaults
    health_check_path    = optional(string, "/health")
    health_check_matcher = optional(string, "200")
    port                 = optional(number, 8080)
  }))
}
```

## Quality Gates

Every Terraform repository must enforce these before code enters the main branch:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    hooks:
      - id: terraform_fmt       # Consistent formatting
      - id: terraform_tflint    # Static analysis
      - id: terraform_checkov   # Security policy scanning
```

## Cloud Provider Translation

| Concept | AWS | GCP | Azure |
|---------|-----|-----|-------|
| State backend | S3 + DynamoDB | GCS | Azure Blob Storage |
| State encryption | S3 SSE-AES256 | GCS default encryption | Blob encryption |
| State locking | DynamoDB table | GCS native locking | Blob lease locking |
| Remote state data source | `terraform_remote_state` (S3) | `terraform_remote_state` (GCS) | `terraform_remote_state` (azurerm) |
| Community module registry | `terraform-aws-modules/*` | `terraform-google-modules/*` | `Azure/terraform-azurerm-*` |
| Provider constraint | `hashicorp/aws ~> 5.0` | `hashicorp/google ~> 5.0` | `hashicorp/azurerm ~> 3.0` |

## Examples

Working implementations in `examples/`:
- **`examples/numbered-layers.md`** -- Complete directory structure with backend configuration for a numbered-layer repository
- **`examples/module-wrapper.md`** -- Wrapping a community module with organization defaults, validation, and smart defaults

## Review Checklist

When designing or reviewing infrastructure-as-code organization:

- [ ] Each layer has its own state file (no monolithic state)
- [ ] Layers are numbered by dependency order (lower numbers are prerequisites)
- [ ] Cross-layer references use `terraform_remote_state`, not hardcoded values
- [ ] State buckets have encryption, versioning, locking, and public access blocked
- [ ] Root/management account infrastructure is in a separate repository
- [ ] Modules wrap community modules rather than reimplementing them
- [ ] All module inputs have validation rules where applicable
- [ ] All module and provider versions are pinned (no "latest")
- [ ] Pre-commit hooks enforce formatting, linting, and security scanning
- [ ] Service teams can deploy their layer independently without blocking others
- [ ] Gap numbering leaves room for future layers (10, 20, 30... not 1, 2, 3)
- [ ] Each environment (dev, prod) has its own subdirectory within each layer
