# OIDC Trust Policies for CI/CD

Complete OIDC federation setup for authenticating CI/CD pipelines to cloud providers without stored credentials. Covers provider configuration, role trust policies with subject claim restrictions, and workflow usage.

## AWS: GitHub Actions OIDC Federation

### Step 1: Create the OIDC Provider (Once Per AWS Account)

```hcl
# oidc.tf -- Created in each AWS account that pipelines need to access

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]

  tags = merge(module.labels.tags, {
    description = "GitHub Actions OIDC provider for CI/CD authentication"
  })
}
```

### Step 2: Create Roles with Subject Claim Restrictions

```hcl
# iam-cicd-roles.tf

# --- Plan-Only Role (used during PRs) ---
# Can only read state and generate plans, never apply
resource "aws_iam_role" "github_actions_plan" {
  name = "${module.labels.prf}github-actions-plan"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringLike = {
            # Any branch or PR from these repos can plan
            "token.actions.githubusercontent.com:sub" = [
              "repo:myorg/infra-global:*",
              "repo:myorg/myapp-api:*",
              "repo:myorg/billing-service:*"
            ]
          }
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = module.labels.tags
}

resource "aws_iam_role_policy_attachment" "plan_read_only" {
  role       = aws_iam_role.github_actions_plan.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

# Additional policy for state bucket access (plan needs to read/write state lock)
resource "aws_iam_role_policy" "plan_state_access" {
  name = "terraform-state-access"
  role = aws_iam_role.github_actions_plan.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.state_bucket_name}",
          "arn:aws:s3:::${var.state_bucket_name}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem"
        ]
        Resource = "arn:aws:dynamodb:*:*:table/${var.state_lock_table_name}"
      }
    ]
  })
}

# --- Deploy Role (used for terraform apply and app deployments) ---
# Restricted to tag pushes only
resource "aws_iam_role" "github_actions_deploy" {
  name = "${module.labels.prf}github-actions-deploy"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringLike = {
            # ONLY tag pushes can assume this role
            "token.actions.githubusercontent.com:sub" = [
              "repo:myorg/infra-global:ref:refs/tags/v*",
              "repo:myorg/myapp-api:ref:refs/tags/v*",
              "repo:myorg/billing-service:ref:refs/tags/v*"
            ]
          }
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = module.labels.tags
}

# Deploy role gets broader permissions (scoped to what Terraform needs)
resource "aws_iam_role_policy_attachment" "deploy_permissions" {
  role       = aws_iam_role.github_actions_deploy.name
  policy_arn = aws_iam_policy.terraform_deploy.arn
}

# --- Build Role (used for container image builds) ---
# Can push to ECR, nothing else
resource "aws_iam_role" "github_actions_build" {
  name = "${module.labels.prf}github-actions-build"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringLike = {
            # Any branch push can build (dev deploys from branches)
            "token.actions.githubusercontent.com:sub" = [
              "repo:myorg/myapp-api:ref:refs/heads/*",
              "repo:myorg/myapp-api:ref:refs/tags/v*"
            ]
          }
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = module.labels.tags
}

resource "aws_iam_role_policy" "build_ecr_push" {
  name = "ecr-push"
  role = aws_iam_role.github_actions_build.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = "arn:aws:ecr:${var.region}:${var.account_id}:repository/*"
      }
    ]
  })
}
```

### Step 3: Use in Workflows

```yaml
# CI workflow (PRs): uses plan-only role
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::role/acme-dev-github-actions-plan
    aws-region: eu-west-1
    # No access key, no secret key -- OIDC only

# Build workflow (pushes): uses build role
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::role/acme-dev-github-actions-build
    aws-region: eu-west-1

# CD workflow (tags): uses deploy role
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::role/acme-prod-github-actions-deploy
    aws-region: eu-west-1
```

## GCP: GitHub Actions Workload Identity Federation

```hcl
# Workload Identity Pool
resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github-actions"
  display_name              = "GitHub Actions"
  description               = "OIDC federation for GitHub Actions CI/CD"
}

# Workload Identity Provider
resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
    "attribute.ref"        = "assertion.ref"
  }

  # Restrict to your GitHub organization
  attribute_condition = "assertion.repository_owner == 'myorg'"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Service account for deployments
resource "google_service_account" "github_actions_deploy" {
  account_id   = "github-actions-deploy"
  display_name = "GitHub Actions Deploy"
}

# Bind WIF to service account with repository restriction
resource "google_service_account_iam_member" "github_actions_wif" {
  service_account_id = google_service_account.github_actions_deploy.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/myorg/infra-global"
}
```

## Role Summary

| Role | Can Assume From | Permissions | Use Case |
|------|----------------|-------------|----------|
| Plan | Any branch/PR from listed repos | ReadOnly + state access | `terraform plan` in PR CI |
| Build | Any branch or tag from listed repos | ECR push only | Docker build and push |
| Deploy | Only tag pushes (`v*`) from listed repos | Terraform deploy permissions | `terraform apply` in production |

### Security Boundaries

- **Plan role**: Cannot modify any infrastructure. Even if compromised, the worst case is information disclosure (reading resource configurations).
- **Build role**: Can only push container images. Cannot deploy, cannot modify infrastructure, cannot read secrets.
- **Deploy role**: Full deployment permissions but only assumable from tag pushes. A compromised branch cannot trigger a production deployment.
