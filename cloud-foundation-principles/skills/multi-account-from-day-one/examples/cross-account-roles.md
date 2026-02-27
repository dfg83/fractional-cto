# Cross-Account Roles -- OIDC Federation and Developer Access

Terraform configuration for CI/CD OIDC federation and developer cross-account access with least-privilege permissions.

## CI/CD OIDC Provider (Management Account)

```hcl
# root/oidc.tf -- Created once in the management account

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]

  tags = {
    managed_by = "terraform"
    purpose    = "cicd-oidc"
  }
}

output "oidc_provider_arn" {
  value = aws_iam_openid_connect_provider.github.arn
}
```

## Per-Account CI/CD Role (Each Workload Account)

```hcl
# per-account/cicd_role.tf -- Created in dev, prod, security accounts

variable "oidc_provider_arn" {
  description = "ARN of the OIDC provider from the management account"
  type        = string
}

variable "allowed_repos" {
  description = "GitHub repositories allowed to assume this role"
  type        = list(string)
  default     = ["repo:myorg/infrastructure:*"]
}

data "aws_iam_policy_document" "cicd_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [var.oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = var.allowed_repos
    }
  }
}

resource "aws_iam_role" "cicd" {
  name               = "CicdDeployRole"
  assume_role_policy = data.aws_iam_policy_document.cicd_trust.json
  max_session_duration = 3600   # 1 hour max -- CI/CD jobs should be short

  tags = {
    managed_by = "terraform"
    purpose    = "cicd-deployment"
  }
}

# Attach appropriate policies per account
# Dev: broader permissions for testing
# Prod: scoped to specific deployment actions
resource "aws_iam_role_policy_attachment" "cicd_policy" {
  role       = aws_iam_role.cicd.name
  policy_arn = var.cicd_policy_arn
}
```

## Developer Cross-Account Access via SSO

```hcl
# root/sso.tf -- Permission sets and assignments

# -----------------------------------------------------------------------------
# Permission Sets
# -----------------------------------------------------------------------------

resource "aws_ssoadmin_permission_set" "admin" {
  name             = "AdministratorAccess"
  instance_arn     = var.sso_instance_arn
  session_duration = "PT4H"   # 4-hour sessions for admin access

  tags = {
    managed_by = "terraform"
  }
}

resource "aws_ssoadmin_permission_set" "developer" {
  name             = "DeveloperAccess"
  instance_arn     = var.sso_instance_arn
  session_duration = "PT8H"   # 8-hour sessions for developer access

  tags = {
    managed_by = "terraform"
  }
}

resource "aws_ssoadmin_permission_set" "readonly" {
  name             = "ReadOnlyAccess"
  instance_arn     = var.sso_instance_arn
  session_duration = "PT8H"

  tags = {
    managed_by = "terraform"
  }
}

# -----------------------------------------------------------------------------
# Admin: Full access to all accounts (small team only)
# -----------------------------------------------------------------------------

resource "aws_ssoadmin_managed_policy_attachment" "admin_policy" {
  instance_arn       = var.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.admin.arn
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_ssoadmin_account_assignment" "admin_all" {
  for_each = toset([
    var.account_id_dev,
    var.account_id_prod,
    var.account_id_security,
  ])

  instance_arn       = var.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.admin.arn
  principal_id       = var.admin_group_id
  principal_type     = "GROUP"
  target_id          = each.value
  target_type        = "AWS_ACCOUNT"
}

# -----------------------------------------------------------------------------
# Developer: Full access in dev, read-only in prod
# -----------------------------------------------------------------------------

# Dev account: full access for rapid iteration
resource "aws_ssoadmin_managed_policy_attachment" "developer_full" {
  instance_arn       = var.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.developer.arn
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_ssoadmin_account_assignment" "developer_dev" {
  instance_arn       = var.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.developer.arn
  principal_id       = var.developer_group_id
  principal_type     = "GROUP"
  target_id          = var.account_id_dev
  target_type        = "AWS_ACCOUNT"
}

# Prod account: read-only with targeted exceptions
resource "aws_ssoadmin_permission_set" "developer_prod" {
  name             = "DeveloperProdAccess"
  instance_arn     = var.sso_instance_arn
  session_duration = "PT4H"   # Shorter sessions in prod

  tags = {
    managed_by = "terraform"
  }
}

resource "aws_ssoadmin_permission_set_inline_policy" "developer_prod_policy" {
  instance_arn       = var.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.developer_prod.arn

  inline_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ReadOnlyBase"
        Effect   = "Allow"
        Action   = [
          "ec2:Describe*",
          "ecs:Describe*",
          "ecs:List*",
          "rds:Describe*",
          "s3:GetObject",
          "s3:ListBucket",
          "logs:GetLogEvents",
          "logs:FilterLogEvents",
          "logs:DescribeLogGroups",
          "cloudwatch:GetMetricData",
          "cloudwatch:DescribeAlarms",
        ]
        Resource = "*"
      },
      {
        Sid      = "ContainerRegistryRead"
        Effect   = "Allow"
        Action   = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchGetImage",
          "ecr:DescribeImages",
        ]
        Resource = "*"
      },
      {
        Sid      = "DebugAccess"
        Effect   = "Allow"
        Action   = [
          "ssm:StartSession",
          "ecs:ExecuteCommand",
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = var.primary_region
          }
        }
      }
    ]
  })
}

resource "aws_ssoadmin_account_assignment" "developer_prod" {
  instance_arn       = var.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.developer_prod.arn
  principal_id       = var.developer_group_id
  principal_type     = "GROUP"
  target_id          = var.account_id_prod
  target_type        = "AWS_ACCOUNT"
}
```

## GCP Equivalent -- Workload Identity Federation for CI/CD

```hcl
# GCP: Workload Identity Federation for GitHub Actions

resource "google_iam_workload_identity_pool" "github" {
  project                   = var.project_id
  workload_identity_pool_id = "github-pool"
  display_name              = "GitHub Actions Pool"
}

resource "google_iam_workload_identity_pool_provider" "github" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub Actions"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
  }

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account" "cicd" {
  project      = var.project_id
  account_id   = "cicd-deploy"
  display_name = "CI/CD Deploy Service Account"
}

resource "google_service_account_iam_member" "cicd_wif" {
  service_account_id = google_service_account.cicd.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/myorg/infrastructure"
}
```

## Key Points

1. **Zero static credentials** -- OIDC federation means no API keys stored anywhere
2. **Per-account roles** -- Each account has its own CI/CD role with its own trust policy
3. **Repo-scoped trust** -- Only specific repositories can assume deployment roles
4. **Short sessions** -- CI/CD roles have 1-hour max sessions; admin has 4-hour sessions
5. **Prod is read-only by default** -- Developers can view logs and metrics but cannot modify resources
6. **Group-based, not user-based** -- Assignments target SSO groups, not individual users
