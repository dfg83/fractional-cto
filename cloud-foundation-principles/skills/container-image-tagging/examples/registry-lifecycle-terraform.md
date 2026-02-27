# Container Registry with Lifecycle Policies

Terraform configuration for a container registry with lifecycle policies for image retention, image scanning, tag immutability, and cross-account pull permissions.

## AWS ECR Registry Configuration

```hcl
# registry.tf -- Container registry for a single service

# --- ECR Repository ---
resource "aws_ecr_repository" "this" {
  name                 = "${module.labels.prf}api"
  image_tag_mutability = "IMMUTABLE"  # Prevent tag overwrites

  image_scanning_configuration {
    scan_on_push = true  # Scan every image at push time
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = var.kms_key_arn  # Use dedicated KMS key
  }

  tags = module.labels.tags
}

# --- Lifecycle Policy ---
resource "aws_ecr_lifecycle_policy" "this" {
  repository = aws_ecr_repository.this.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 20 SHA-tagged images for rollback"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["sha-"]
          countType     = "imageCountMoreThan"
          countNumber   = 20
        }
        action = { type = "expire" }
      },
      {
        rulePriority = 2
        description  = "Keep last 10 semver-tagged images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = { type = "expire" }
      },
      {
        rulePriority = 10
        description  = "Remove untagged images after 7 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 7
        }
        action = { type = "expire" }
      }
    ]
  })
}

# --- Cross-Account Pull Policy ---
# Allow production account to pull images built in the CI/CD account
resource "aws_ecr_repository_policy" "cross_account_pull" {
  repository = aws_ecr_repository.this.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowProdAccountPull"
        Effect = "Allow"
        Principal = {
          AWS = [
            "arn:aws:iam::${var.prod_account_id}:root",
            "arn:aws:iam::${var.dev_account_id}:root"
          ]
        }
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability"
        ]
      }
    ]
  })
}

# --- Outputs ---
output "repository_url" {
  description = "The URL of the ECR repository"
  value       = aws_ecr_repository.this.repository_url
}

output "repository_arn" {
  description = "The ARN of the ECR repository"
  value       = aws_ecr_repository.this.arn
}
```

## GCP Artifact Registry Equivalent

```hcl
# registry.tf -- GCP Artifact Registry

resource "google_artifact_registry_repository" "this" {
  location      = var.region
  repository_id = "myapp-api"
  description   = "Container images for myapp-api"
  format        = "DOCKER"

  cleanup_policies {
    id     = "keep-last-20-tagged"
    action = "KEEP"
    most_recent_versions {
      keep_count = 20
    }
  }

  cleanup_policies {
    id     = "delete-untagged-after-7-days"
    action = "DELETE"
    condition {
      tag_state  = "UNTAGGED"
      older_than = "604800s"  # 7 days in seconds
    }
  }

  labels = module.labels.tags
}

# Allow cross-project pull
resource "google_artifact_registry_repository_iam_member" "prod_reader" {
  location   = google_artifact_registry_repository.this.location
  repository = google_artifact_registry_repository.this.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${var.prod_service_account_email}"
}
```

## Azure Container Registry Equivalent

```hcl
# registry.tf -- Azure Container Registry

resource "azurerm_container_registry" "this" {
  name                = "myorgmyappapi"  # ACR names must be globally unique, alphanumeric
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  sku                 = "Standard"
  admin_enabled       = false  # Use RBAC, not admin credentials

  retention_policy {
    enabled = true
    days    = 7  # Retain untagged manifests for 7 days
  }

  tags = module.labels.tags
}

# Role assignment for cross-subscription pull
resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.this.id
  role_definition_name = "AcrPull"
  principal_id         = var.prod_cluster_identity_principal_id
}
```

## Lifecycle Policy Rationale

| Rule | Retention | Rationale |
|------|-----------|-----------|
| SHA-tagged images | Keep last 20 | Covers ~2-4 weeks of deployments; always have rollback targets |
| Semver-tagged images | Keep last 10 | Release milestones for reference and long-term rollback |
| Untagged images | Delete after 7 days | Intermediate build layers; no production value |

### Why 20 Images?

If your team deploys once per day, 20 images covers nearly a month of rollback history. If you deploy 3 times per day, it covers about a week. Adjust the count to always maintain at least 1-2 weeks of rollback depth. The storage cost of 20 images is trivial compared to the cost of needing to roll back and discovering the image has been garbage collected.
