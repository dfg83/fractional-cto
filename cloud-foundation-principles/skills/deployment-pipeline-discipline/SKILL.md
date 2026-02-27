---
name: deployment-pipeline-discipline
description: "This skill should be used when the user is designing CI/CD pipelines for infrastructure or application deployments, choosing container image tagging strategies, configuring production release triggers, setting up pre-commit hooks for Terraform, implementing OIDC authentication for pipelines, or consolidating multiple CI/CD platforms. Covers git SHA image tagging, tag-based production deploys, unified CI/CD platform strategy, pipeline stages, OIDC auth, and pre-commit quality gates."
version: 1.0.0
---

# Three Rules That Prevent Deployment Disasters

Most deployment incidents share a root cause: someone deployed something they could not trace, to an environment they did not intend, through a process that had no gate. Deployment pipeline discipline prevents all three failure modes with three non-negotiable rules: tag container images with git SHAs for traceability, trigger production deploys from git tags for intentionality, and use one CI/CD platform for everything to eliminate operational confusion. These rules are simple. Violating them is expensive.

## Rule 1: Container Images Tagged with Git SHA

Every container image must be tagged with the git commit SHA that produced it. This creates an unbreakable chain from running container to source code. When a production incident occurs at 3am, the first question is always "what code is running?" -- a git SHA answers that instantly.

**The format:**
```
<registry>/<service>:<git-sha>
```

**Example:**
```
registry.example.com/myapp-api:a1b2c3d4e5f6
```

### Good vs. Bad Tagging

| Pattern | Verdict | Why |
|---------|---------|-----|
| `myapp-api:a1b2c3d4e5f6` | Good | Full traceability to exact commit |
| `myapp-api:v1.4.2-a1b2c3d` | Good | Semantic version + short SHA for human readability |
| `myapp-api:latest` | Bad | Which commit? Which build? Nobody knows at 3am |
| `myapp-api:stable` | Bad | "Stable" according to whom? When? |
| `myapp-api:dev` | Bad | Overwrites previous image, no rollback path |
| `myapp-api:20260215` | Bad | Multiple commits per day; which one? |

**Never use `latest` in production.** The `latest` tag is mutable -- it points to whatever was pushed most recently. Two services pulling `latest` five minutes apart may get different images. Rolling back means figuring out which previous image was "latest" before the current one. This is chaos.

### Registry Lifecycle Policies

Container registries accumulate images fast. Set lifecycle policies to retain a fixed number of tagged images (20 is a sensible default) and delete untagged images after 7 days.

```hcl
# Container registry lifecycle policy
resource "aws_ecr_lifecycle_policy" "cleanup" {
  repository = aws_ecr_repository.myapp.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 20 tagged images"
        selection = {
          tagStatus   = "tagged"
          tagPrefixList = [""]
          countType   = "imageCountMoreThan"
          countNumber = 20
        }
        action = { type = "expire" }
      },
      {
        rulePriority = 2
        description  = "Delete untagged images after 7 days"
        selection = {
          tagStatus = "untagged"
          countType = "sinceImagePushed"
          countUnit = "days"
          countNumber = 7
        }
        action = { type = "expire" }
      }
    ]
  })
}
```

## Rule 2: Production Deploys Triggered by Git Tags

Development environments deploy continuously from branch pushes. Production environments deploy only when a git tag is explicitly created. This distinction is the difference between "code was merged" and "we decided to release."

| Environment | Trigger | Branch/Tag | Intent |
|-------------|---------|------------|--------|
| Dev/Staging | Push to `develop` or `main` | Branch | Continuous integration, fast feedback |
| Production | Git tag creation (`v1.4.2`) | Tag on `main` | Explicit, deliberate release decision |

### Why Tags, Not Branches

- **Audit trail**: Git tags are immutable references. You can answer "what was deployed to production on March 5th?" with `git tag --contains`.
- **Intentionality**: Creating a tag is a deliberate act. Pushing to a branch can be accidental.
- **Rollback clarity**: Rolling back means deploying the previous tag. No ambiguity about which commit to target.
- **Compliance**: Regulated environments require evidence that production changes were intentional. Tags provide this natively.

### Tag Naming Convention

Use semantic versioning with a `v` prefix:
```
v1.0.0      # Major release
v1.1.0      # Feature addition
v1.1.1      # Patch/bugfix
v1.2.0-rc.1 # Release candidate (optional, for staged rollouts)
```

### Pipeline Flow

```
Developer pushes to develop
  |
  v
CI Pipeline (automatic):
  1. Lint (application + infrastructure)
  2. Test (unit, integration)
  3. Build container image
  4. Push image to registry with git SHA tag
  5. Terraform plan (infrastructure changes)
  |
  v  (no automatic deploy to prod)

Release manager creates git tag on main
  |
  v
CD Pipeline (triggered by tag):
  1. Pull image by git SHA
  2. Terraform plan
  3. Manual approval gate  <-- human confirms
  4. Terraform apply
  5. Update container service (new task definition)
  6. Wait for steady state (health checks pass)
  7. Post-deploy verification
```

The manual approval gate before `terraform apply` in production is non-negotiable. Automated deploys to dev are fine. Automated deploys to production without human confirmation are reckless.

## Rule 3: One CI/CD Platform for Everything

Using CircleCI for application builds, GitLab CI for infrastructure, and GitHub Actions for deployments is an operational nightmare. Every platform has different syntax, different secrets management, different debugging tools, and different failure modes. When an incident requires tracing a deployment from commit to production, crossing platform boundaries wastes critical time.

**Pick one. Use it for everything.** The specific platform matters less than the consistency.

| Consideration | Recommendation |
|---------------|----------------|
| Source code on GitHub | GitHub Actions |
| Source code on GitLab | GitLab CI |
| Multi-provider, complex workflows | GitHub Actions or GitLab CI |
| Existing investment in Jenkins | Migrate. The maintenance cost of Jenkins exceeds the migration cost within 12 months. |

### What "Everything" Means

One platform handles:
- Application CI (lint, test, build, push image)
- Infrastructure CI (terraform fmt, validate, plan)
- Infrastructure CD (terraform apply)
- Application CD (service update, deployment)
- Scheduled jobs (drift detection, cleanup)

## Pipeline Stages in Detail

### Pre-Commit: Quality Before the Repository

Pre-commit hooks run before code enters the repository. They are the first and cheapest quality gate.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.96.0
    hooks:
      - id: terraform_fmt          # Consistent formatting
      - id: terraform_tflint       # Linting and best practices
      - id: terraform_checkov      # Security and compliance scanning
      - id: terraform_validate     # Syntax validation
```

Every infrastructure repository must have these four hooks. No exceptions. A developer who commits unformatted Terraform or code that fails a security scan creates noise for every subsequent reviewer.

### CI Stage: Validate and Plan

```yaml
# Triggered on pull request
ci-infrastructure:
  steps:
    - checkout
    - setup-terraform
    - terraform init
    - terraform validate
    - terraform plan -out=tfplan
    - post-plan-as-pr-comment    # Make the plan visible in the review
```

Post the `terraform plan` output as a PR comment. Reviewers should see exactly what will change before approving. A plan that shows 47 resources being destroyed should raise immediate questions.

### CD Stage: Apply with Gates

```yaml
# Triggered on git tag push
cd-infrastructure:
  steps:
    - checkout
    - setup-terraform
    - terraform init
    - terraform validate
    - terraform plan -out=tfplan
    - manual-approval            # Human gate
    - terraform apply tfplan
    - post-deploy-verification
```

## OIDC Authentication: No Stored Credentials

CI/CD pipelines must authenticate to cloud providers via OIDC federation, not stored API keys or access tokens. OIDC issues short-lived, scoped credentials for each pipeline run.

```hcl
# OIDC provider for CI/CD platform (created once in each account)
resource "aws_iam_openid_connect_provider" "cicd" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

# Role assumed by CI/CD pipelines
resource "aws_iam_role" "cicd_deploy" {
  name = "${module.labels.prf}cicd-deploy"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = aws_iam_openid_connect_provider.cicd.arn
      }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        StringLike = {
          # Restrict to specific repository
          "token.actions.githubusercontent.com:sub" = "repo:myorg/myapp-api:*"
        }
      }
    }]
  })
}
```

**Key principle**: the OIDC subject claim restricts which repositories can assume which roles. A CI/CD pipeline for `myapp-api` cannot assume a role intended for `billing-service`. This is scope isolation at the authentication layer.

## Cloud Provider Translation

| Concept | AWS | GCP | Azure |
|---------|-----|-----|-------|
| OIDC federation for CI/CD | STS AssumeRoleWithWebIdentity | Workload Identity Federation | Federated Credentials (Entra ID) |
| Container registry | ECR | Artifact Registry | ACR |
| Image lifecycle policy | ECR Lifecycle Policy | Artifact Registry Cleanup Policy | ACR Retention Policy |
| Pipeline platform | GitHub Actions / CodePipeline | Cloud Build / GitHub Actions | Azure Pipelines / GitHub Actions |
| Secrets in pipelines | OIDC (no secrets stored) | Workload Identity (no secrets stored) | Federated Identity (no secrets stored) |
| Manual approval gate | GitHub Environments + Required Reviewers | Cloud Build Approval | Azure Pipelines Approvals |
| Pre-commit scanning | checkov, tfsec, tflint | checkov, tfsec, tflint | checkov, tfsec, tflint |

## Examples

Working implementations in `examples/`:
- **`examples/pipeline-stages.md`** -- Complete CI/CD pipeline configuration showing pre-commit hooks, CI validation with plan-as-PR-comment, and CD with manual approval gate and OIDC authentication
- **`examples/image-tagging-and-lifecycle.md`** -- Container image build pipeline with git SHA tagging, registry lifecycle policies, and deployment traceability patterns

## Review Checklist

When designing or reviewing deployment pipelines:

- [ ] Container images are tagged with the git commit SHA, never `latest`, `stable`, or date-based tags
- [ ] Production deployments are triggered by git tag creation, not branch pushes
- [ ] A manual approval gate exists before any `terraform apply` to production
- [ ] One CI/CD platform is used for all pipelines (application CI, infrastructure CI, infrastructure CD, application CD)
- [ ] Pre-commit hooks enforce `terraform fmt`, `tflint`, `checkov`/`tfsec`, and `terraform validate`
- [ ] `terraform plan` output is posted as a PR comment for reviewer visibility
- [ ] CI/CD authenticates to cloud providers via OIDC, not stored access keys or tokens
- [ ] OIDC subject claims restrict which repositories can assume which deployment roles
- [ ] Container registry lifecycle policies retain a fixed number of images (20) and clean up untagged images
- [ ] The pipeline flow is: pre-commit -> validate -> plan -> review -> approve -> apply -> verify
- [ ] Dev/staging environments deploy continuously from branches; production deploys only from tags
- [ ] Rollback procedure is documented: deploy the previous git tag, not "revert and push"
