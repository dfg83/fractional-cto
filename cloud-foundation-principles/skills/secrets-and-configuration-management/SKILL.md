---
name: secrets-and-configuration-management
description: "This skill should be used when the user is storing credentials, managing API keys, setting up secret rotation, choosing between secrets managers and parameter stores, designing configuration hierarchies, naming secrets or parameters, creating database users, managing environment-specific configuration, or deciding how applications should access secrets at runtime. Covers strict separation of secrets vs configuration, secrets manager with auto-rotation, parameter/config stores for plain values, role-based database users, and hierarchical naming conventions."
version: 1.0.0
---

# Secrets Are Not Configuration, and Configuration Is Not Secrets

The most common infrastructure mistake with credentials is treating everything the same -- stuffing database passwords, feature flags, service endpoints, and API keys into the same store with the same access patterns. This creates two problems: secrets that should rotate automatically sit in a plain-text config file, and configuration values that change frequently get locked behind the slow, expensive secrets management API.

Separate them cleanly from day one. Secrets are credentials that grant access and need rotation -- database passwords, API keys, TLS certificates, OAuth client secrets. Configuration is everything else -- service endpoints, feature flags, resource IDs, environment names, connection pool sizes. Different stores, different access patterns, different cost profiles.

## The Separation Matrix

| Property | Secrets | Configuration |
|----------|---------|---------------|
| **Contains** | Credentials that grant access | Values that configure behavior |
| **Examples** | DB passwords, API keys, OAuth secrets, TLS private keys | Endpoints, IDs, feature flags, pool sizes, region names |
| **Rotation** | Automatic, on a schedule (30-90 days) | Manual, when values change |
| **Encryption** | Mandatory, customer-managed keys | Optional (often plaintext is fine) |
| **Access audit** | Every read logged and auditable | Standard logging sufficient |
| **Cost** | Per-secret, per-API-call pricing | Free tier or minimal cost |
| **Store** | Secrets manager service | Parameter/config store service |
| **Terraform managed** | Yes -- created and stored via IaC | Yes -- created and stored via IaC |

**The test is simple:** if leaking this value would grant unauthorized access to a system, it is a secret. If leaking it would be embarrassing but not exploitable, it is configuration.

## Secrets Manager: For Credentials Only

Use a dedicated secrets manager service for every credential. No exceptions. No environment variables with hardcoded passwords. No `.env` files committed to version control. No Terraform outputs containing raw secrets.

### Principles

1. **Secrets as code.** Every secret is created and stored via Terraform. The Terraform state contains the secret ARN/ID, never the plaintext value. The secret value is set at creation time and rotated automatically thereafter.

2. **No hardcoded secrets.** Application containers receive secret references (ARNs, resource paths), not plaintext values. The application or runtime resolves the reference at startup.

3. **Auto-rotation enabled.** Database credentials rotate on a 30-90 day schedule using the cloud provider's native rotation mechanism. If a secret cannot auto-rotate (third-party API keys), document it and set a calendar reminder.

4. **Customer-managed encryption keys.** Every secret is encrypted with a KMS key you control, not the provider default. This enables key rotation, cross-account access policies, and audit trails on decryption.

### Good Pattern vs Bad Pattern

```hcl
# Good: secret reference passed to container, resolved at runtime

resource "aws_secretsmanager_secret" "db_password" {
  name       = "/prod/myapp/db-password"
  kms_key_id = aws_kms_key.secrets.arn
}

resource "aws_ecs_task_definition" "myapp" {
  # ...
  container_definitions = jsonencode([{
    name = "myapp"
    secrets = [{
      name      = "DB_PASSWORD"
      valueFrom = aws_secretsmanager_secret.db_password.arn
    }]
  }])
}
```

```hcl
# Bad: plaintext password in environment variable via Terraform

resource "aws_ecs_task_definition" "myapp" {
  container_definitions = jsonencode([{
    name = "myapp"
    environment = [{
      name  = "DB_PASSWORD"
      value = "hunter2"  # Plaintext in state file, logs, and console
    }]
  }])
}
```

## Configuration Store: For Everything Else

Configuration values that do not grant access belong in a parameter or configuration store. These services are cheaper (often free tier), support hierarchical organization, and do not need the rotation machinery of a secrets manager.

### What Goes in the Config Store

- VPC IDs, subnet IDs, security group IDs
- Service endpoints and DNS names
- Resource ARNs that are not secrets (SNS topic ARN, SQS queue URL)
- Feature flags and toggles
- Connection pool sizes, timeout values, retry counts
- Environment identifiers (dev, staging, prod)
- Bastion instance IDs, cluster ARNs

### What Does Not Go in the Config Store

- Database passwords (secrets manager)
- API keys for third-party services (secrets manager)
- TLS private keys (secrets manager or certificate manager)
- OAuth client secrets (secrets manager)
- Anything where exposure grants unauthorized access

## Naming Hierarchy: /{environment}/{service}/{key}

A consistent naming hierarchy makes secrets and configuration discoverable, auditable, and automatable. Use the same hierarchy for both stores.

```
/{environment}/{service}/{key}

Examples:
  /prod/myapp/db-password          (secret)
  /prod/myapp/db-host              (config)
  /prod/myapp/db-port              (config)
  /prod/myapp/redis-url            (config)
  /prod/myapp/stripe-api-key       (secret)
  /dev/myapp/feature-new-checkout  (config)
  /prod/shared/vpc-id              (config)
  /prod/shared/private-subnet-ids  (config)
```

**Why this hierarchy works:**

- **Environment-first** enables IAM policies that grant access to all of `/dev/*` but nothing in `/prod/*`. Developers can read dev secrets but not production credentials.
- **Service-scoped** ensures each application only accesses its own secrets. The `myapp` service has no reason to read `/prod/payments/stripe-api-key`.
- **Shared namespace** (`/prod/shared/`) holds cross-service values like VPC IDs and subnet lists, readable by all services in that environment.

```hcl
# Good: hierarchical naming with environment-scoped IAM policy

resource "aws_ssm_parameter" "db_host" {
  name  = "/prod/myapp/db-host"
  type  = "String"
  value = aws_db_instance.myapp.address
}

resource "aws_iam_policy" "myapp_config_read" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = ["ssm:GetParameter", "ssm:GetParametersByPath"]
      Resource = "arn:aws:ssm:*:*:parameter/prod/myapp/*"
    }]
  })
}
```

```
# Bad: flat naming with no hierarchy

db_password_prod
myapp-db-host
MYAPP_REDIS
prod.myapp.feature_flag
MyApp-Stripe-Key

# Inconsistent separators (-, _, .), no path hierarchy,
# impossible to scope IAM policies, no environment isolation
```

## Database Users: Role-Based, Never Person-Specific

Database users follow the same separation principle. Never create person-specific database accounts (`john_doe`, `jane_smith`). Create role-based users that describe purpose and access level.

### Role Naming Convention: {purpose}_{access}

```
app_readwrite     -- Application service (read + write)
app_readonly      -- Application service (read only, e.g., replica queries)
analytics_readonly -- Analytics/BI tools (read only, all tables)
migration_admin    -- Schema migration runner (DDL permissions, time-boxed)
generic_readonly   -- All team members (read only, for debugging)
```

### Access Model

```
Individual developer access:
  Developer --> SSO --> Cloud console --> Database proxy --> generic_readonly role
  (No personal credentials. Access revoked by disabling SSO account.)

Application access:
  Container --> Secret reference --> Secrets manager --> app_readwrite password
  (Auto-rotated. No human knows the password.)

Analytics access:
  BI tool --> Secret reference --> Secrets manager --> analytics_readonly password
  (Scoped to SELECT on reporting tables only.)

Emergency admin access:
  SRE --> SSO --> Temporary admin session --> migration_admin role
  (Time-boxed to 1 hour. Fully audited. Requires approval.)
```

### Why No Personal Database Users

- **Offboarding is instant.** Disable the SSO account, and all access revokes. No need to find and delete database users across dozens of instances.
- **Credential sprawl is eliminated.** Ten developers do not mean ten passwords to manage, rotate, and audit.
- **Audit trails are cleaner.** Actions are traceable to SSO identity through the cloud provider's audit log, not to a database username that might be shared.

## Cloud Provider Translation

| Concept | AWS | GCP | Azure |
|---------|-----|-----|-------|
| Secrets storage | Secrets Manager | Secret Manager | Key Vault (secrets) |
| Configuration storage | SSM Parameter Store | Secret Manager (non-secret) or Firestore | App Configuration |
| Auto-rotation | Secrets Manager rotation lambdas | Secret Manager rotation (Cloud Functions) | Key Vault rotation policies |
| Encryption keys | KMS (customer-managed CMK) | Cloud KMS | Key Vault (keys) |
| Hierarchical naming | SSM path hierarchy (`/env/svc/key`) | Secret labels + naming convention | App Configuration labels + key prefixes |
| IAM path-scoped access | IAM policy on `parameter/prod/*` | IAM condition on `secret.name` | RBAC on Key Vault + label filters |
| Database proxy | RDS Proxy / IAM DB auth | Cloud SQL Auth Proxy | Azure AD DB auth |

## Examples

Working implementations in `examples/`:
- **`examples/secrets-and-config-separation.md`** -- Complete Terraform configuration showing secrets in a secrets manager with KMS encryption and auto-rotation alongside configuration values in a parameter store, both following the `/{env}/{service}/{key}` hierarchy
- **`examples/database-role-management.md`** -- Role-based database user creation with purpose-named roles, secrets manager storage for each credential, and IAM-based developer access through a database proxy

## Review Checklist

When designing or reviewing secrets and configuration management:

- [ ] Credentials (passwords, API keys, TLS keys) are in a secrets manager, not environment variables or config files
- [ ] Configuration values (IDs, endpoints, flags) are in a parameter/config store, not the secrets manager
- [ ] All secrets are encrypted with customer-managed KMS keys, not provider defaults
- [ ] Auto-rotation is enabled for database credentials on a 30-90 day schedule
- [ ] Third-party API keys that cannot auto-rotate are documented with manual rotation reminders
- [ ] Naming follows `/{environment}/{service}/{key}` hierarchy consistently
- [ ] IAM policies scope access by environment and service path (no wildcard access to all secrets)
- [ ] Applications receive secret references (ARNs/paths), not plaintext values
- [ ] No secrets exist in Terraform outputs, environment variable literals, or committed `.env` files
- [ ] Database users are role-based (`app_readwrite`, `analytics_readonly`), not person-specific
- [ ] Developer database access uses SSO + database proxy with a shared read-only role
- [ ] Emergency admin database access is time-boxed, audited, and requires approval
