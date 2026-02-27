# Image Tagging and Lifecycle

Demonstrates container image tagging with git SHAs, registry lifecycle policies for cleanup, and the deployment traceability chain from running container back to source code.

## Container Registry with Lifecycle Policy

```hcl
# Container image repository (one per service)
resource "aws_ecr_repository" "service" {
  name                 = "${module.labels.prf}myapp-api"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}

# Lifecycle policy: retain last 20 tagged images, clean up untagged after 7 days
resource "aws_ecr_lifecycle_policy" "service" {
  repository = aws_ecr_repository.service.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Delete untagged images after 7 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 7
        }
        action = { type = "expire" }
      },
      {
        rulePriority = 2
        description  = "Keep last 20 tagged images"
        selection = {
          tagStatus   = "tagged"
          tagPrefixList = [""]
          countType   = "imageCountMoreThan"
          countNumber = 20
        }
        action = { type = "expire" }
      }
    ]
  })
}
```

## Image Build and Tag Pattern

```bash
#!/usr/bin/env bash
# build-and-push.sh -- Used in CI/CD pipeline
# Tags the image with the full git SHA for traceability

set -euo pipefail

REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE="myapp-api"
GIT_SHA=$(git rev-parse HEAD)

echo "Building image: ${REGISTRY}/${IMAGE}:${GIT_SHA}"

docker build \
  --tag "${REGISTRY}/${IMAGE}:${GIT_SHA}" \
  --label "org.opencontainers.image.revision=${GIT_SHA}" \
  --label "org.opencontainers.image.source=https://github.com/myorg/myapp-api" \
  --label "org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  .

docker push "${REGISTRY}/${IMAGE}:${GIT_SHA}"

echo "Pushed: ${REGISTRY}/${IMAGE}:${GIT_SHA}"
echo "Traceability: container -> ${GIT_SHA} -> https://github.com/myorg/myapp-api/commit/${GIT_SHA}"
```

## Task Definition with Git SHA Reference

```hcl
# The image tag is always a git SHA, passed as a variable
variable "image_tag" {
  type        = string
  description = "Git SHA of the container image to deploy"

  validation {
    condition     = can(regex("^[a-f0-9]{7,40}$", var.image_tag))
    error_message = "image_tag must be a valid git SHA (7-40 hex characters)"
  }
}

resource "aws_ecs_task_definition" "service" {
  family = "${module.labels.prf}myapp-api"
  # ... other configuration ...

  container_definitions = jsonencode([{
    name  = "myapp-api"
    # Image reference uses git SHA -- never "latest"
    image = "${aws_ecr_repository.service.repository_url}:${var.image_tag}"
    # ... ports, health checks, logging ...
  }])
}
```

## Traceability Chain

```
Production incident at 3am
  |
  v
"What image is running?"
  → Describe the running task: image = registry/myapp-api:a1b2c3d4e5f6
  |
  v
"What code is that?"
  → git show a1b2c3d4e5f6
  → git log a1b2c3d4e5f6 --oneline -5
  |
  v
"What changed in that deploy?"
  → git diff <previous-tag>..a1b2c3d4e5f6
  |
  v
"Who approved the release?"
  → git tag --contains a1b2c3d4e5f6
  → Check the tag's associated PR and approval
```

## Bad Patterns to Avoid

```bash
# BAD: Using "latest" -- which build is this? Nobody knows.
docker build -t registry/myapp-api:latest .
docker push registry/myapp-api:latest

# BAD: Using date tags -- multiple commits per day, which one?
docker build -t registry/myapp-api:20260215 .

# BAD: Using branch names -- mutable, overwritten on every push
docker build -t registry/myapp-api:main .

# BAD: Using incrementing build numbers -- no connection to source code
docker build -t registry/myapp-api:build-142 .
```

```bash
# GOOD: Git SHA tag -- immutable, traceable to exact commit
GIT_SHA=$(git rev-parse HEAD)
docker build -t registry/myapp-api:${GIT_SHA} .

# GOOD: Semantic version + SHA for human-readable releases
GIT_SHA=$(git rev-parse --short HEAD)
VERSION=$(git describe --tags --always)
docker build -t registry/myapp-api:${VERSION}-${GIT_SHA} .
# Result: registry/myapp-api:v1.4.2-a1b2c3d
```

## GCP and Azure Equivalents

### GCP Artifact Registry

```hcl
resource "google_artifact_registry_repository" "service" {
  repository_id = "myapp-api"
  location      = "europe-west1"
  format        = "DOCKER"

  cleanup_policies {
    id     = "keep-last-20"
    action = "KEEP"
    most_recent_versions {
      keep_count = 20
    }
  }

  cleanup_policies {
    id     = "delete-old-untagged"
    action = "DELETE"
    condition {
      tag_state  = "UNTAGGED"
      older_than = "604800s"  # 7 days
    }
  }
}
```

### Azure Container Registry

```hcl
resource "azurerm_container_registry" "service" {
  name                = "acmemyappapi"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Standard"

  retention_policy {
    days    = 7
    enabled = true
  }
}
```

## Key Points

- Every image is tagged with the full git SHA (`a1b2c3d4e5f6...`), creating an unbreakable link from running container to source code
- `image_tag_mutability = "IMMUTABLE"` prevents overwriting tags -- once `a1b2c3d` is pushed, it cannot be replaced
- `scan_on_push = true` ensures every image is scanned for vulnerabilities before deployment
- Lifecycle policies prevent unbounded registry growth: keep 20 tagged images, delete untagged after 7 days
- OCI labels (`org.opencontainers.image.revision`) embed the git SHA in the image metadata for additional traceability
- The `image_tag` variable validates the format to ensure only git SHAs are accepted, catching misconfiguration at plan time
