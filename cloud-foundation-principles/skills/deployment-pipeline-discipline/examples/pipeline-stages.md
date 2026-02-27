# Pipeline Stages

Demonstrates a complete CI/CD pipeline with pre-commit hooks, CI validation that posts Terraform plans as PR comments, and CD with manual approval gates and OIDC authentication. Uses GitHub Actions as the reference platform; the patterns translate directly to GitLab CI, Azure Pipelines, or any other CI/CD system.

## Pre-Commit Configuration

```yaml
# .pre-commit-config.yaml
# Installed once: pre-commit install
# Runs automatically on every git commit

repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.96.0
    hooks:
      - id: terraform_fmt
        name: Terraform Format
        description: Ensures consistent HCL formatting

      - id: terraform_tflint
        name: Terraform Lint
        description: Detects errors, enforces best practices
        args:
          - --args=--config=__GIT_WORKING_DIR__/.tflint.hcl

      - id: terraform_checkov
        name: Security Scan
        description: Scans for security misconfigurations
        args:
          - --args=--quiet
          - --args=--compact

      - id: terraform_validate
        name: Terraform Validate
        description: Validates syntax and internal consistency
```

## TFLint Configuration

```hcl
# .tflint.hcl
config {
  module = true
}

plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

plugin "aws" {
  enabled = true
  version = "0.38.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}
```

## CI Pipeline (Pull Requests)

```yaml
# .github/workflows/ci.yml
name: Infrastructure CI

on:
  pull_request:
    paths:
      - "infrastructure/**"

permissions:
  id-token: write      # Required for OIDC
  contents: read
  pull-requests: write  # Required to post plan as comment

jobs:
  validate-and-plan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [dev]
        # Only plan dev on PRs; prod is planned on tag push
    defaults:
      run:
        working-directory: infrastructure/${{ matrix.environment }}

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.8.0"

      # OIDC authentication -- no stored credentials
      - name: Configure cloud credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID_DEV }}:role/acme-dev-cicd-deploy
          aws-region: eu-west-1

      - name: Terraform Init
        run: terraform init

      - name: Terraform Validate
        run: terraform validate

      - name: Terraform Plan
        id: plan
        run: terraform plan -no-color -out=tfplan
        continue-on-error: true

      # Post the plan as a PR comment for reviewer visibility
      - name: Post Plan to PR
        uses: actions/github-script@v7
        with:
          script: |
            const output = `#### Terraform Plan: \`${{ matrix.environment }}\`
            \`\`\`
            ${{ steps.plan.outputs.stdout }}
            \`\`\`
            *Triggered by @${{ github.actor }} on \`${{ github.event.pull_request.head.sha }}\`*`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: output
            });

      - name: Fail on Plan Error
        if: steps.plan.outcome == 'failure'
        run: exit 1
```

## CD Pipeline (Production Deployment via Tag)

```yaml
# .github/workflows/cd-prod.yml
name: Infrastructure CD (Production)

on:
  push:
    tags:
      - "v*"  # Only trigger on semantic version tags

permissions:
  id-token: write
  contents: read

jobs:
  plan:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: infrastructure/prod
    outputs:
      plan-exitcode: ${{ steps.plan.outputs.exitcode }}

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.8.0"

      - name: Configure cloud credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID_PROD }}:role/acme-prod-cicd-deploy
          aws-region: eu-west-1

      - name: Terraform Init
        run: terraform init

      - name: Terraform Validate
        run: terraform validate

      - name: Terraform Plan
        id: plan
        run: |
          terraform plan -no-color -out=tfplan -detailed-exitcode
          echo "exitcode=$?" >> $GITHUB_OUTPUT
        continue-on-error: true

      - name: Upload Plan Artifact
        uses: actions/upload-artifact@v4
        with:
          name: tfplan-prod
          path: infrastructure/prod/tfplan

  apply:
    needs: plan
    if: needs.plan.outputs.plan-exitcode == '2'  # Only apply if there are changes
    runs-on: ubuntu-latest
    environment: production  # Requires manual approval via GitHub Environment
    defaults:
      run:
        working-directory: infrastructure/prod

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.8.0"

      - name: Configure cloud credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID_PROD }}:role/acme-prod-cicd-deploy
          aws-region: eu-west-1

      - name: Terraform Init
        run: terraform init

      - name: Download Plan Artifact
        uses: actions/download-artifact@v4
        with:
          name: tfplan-prod
          path: infrastructure/prod

      - name: Terraform Apply
        run: terraform apply -auto-approve -parallelism=10 tfplan
```

## Application CI/CD (Image Build + Deploy)

```yaml
# .github/workflows/app-ci.yml
name: Application CI

on:
  push:
    branches: [develop, main]
    paths:
      - "src/**"
      - "Dockerfile"

permissions:
  id-token: write
  contents: read

jobs:
  build-and-push:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure cloud credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID_DEV }}:role/acme-dev-cicd-deploy
          aws-region: eu-west-1

      - name: Login to container registry
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push image
        env:
          REGISTRY: ${{ secrets.AWS_ACCOUNT_ID_DEV }}.dkr.ecr.eu-west-1.amazonaws.com
          IMAGE: myapp-api
          # Tag with git SHA for full traceability
          TAG: ${{ github.sha }}
        run: |
          docker build -t $REGISTRY/$IMAGE:$TAG .
          docker push $REGISTRY/$IMAGE:$TAG
          echo "Pushed: $REGISTRY/$IMAGE:$TAG"
```

## Key Points

- Pre-commit hooks (`terraform_fmt`, `tflint`, `checkov`, `validate`) are the cheapest quality gate -- they catch issues before code enters the repository
- CI pipelines post `terraform plan` output as PR comments so reviewers see exactly what will change
- CD pipelines use GitHub Environments with required reviewers for the manual approval gate
- OIDC authentication (`id-token: write` permission + `aws-actions/configure-aws-credentials`) eliminates stored credentials entirely
- Production deploys trigger only on `v*` tags, never on branch pushes
- The plan artifact is uploaded and downloaded between jobs to ensure the exact plan that was reviewed is the plan that gets applied
- Container images are tagged with `${{ github.sha }}` for full traceability
- `terraform apply -parallelism=10` speeds up large applies while staying within API rate limits
