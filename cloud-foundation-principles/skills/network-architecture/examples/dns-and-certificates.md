# Example: DNS Zones and Certificate Management

## DNS Zone Configuration

### Public Zone (Production)

```hcl
# Route53 public zone for production
resource "aws_route53_zone" "production" {
  name    = "myapp.com"
  comment = "Production public DNS zone"
  tags    = local.tags
}

# Wildcard record pointing to the production load balancer
resource "aws_route53_record" "wildcard_prod" {
  zone_id = aws_route53_zone.production.zone_id
  name    = "*.myapp.com"
  type    = "A"

  alias {
    name                   = module.alb.dns_name
    zone_id                = module.alb.zone_id
    evaluate_target_health = true
  }
}

# API subdomain pointing to the API gateway load balancer
resource "aws_route53_record" "api_prod" {
  zone_id = aws_route53_zone.production.zone_id
  name    = "api.myapp.com"
  type    = "A"

  alias {
    name                   = module.api_alb.dns_name
    zone_id                = module.api_alb.zone_id
    evaluate_target_health = true
  }
}
```

### Public Zone (Development)

```hcl
# Separate zone for dev environment
resource "aws_route53_zone" "development" {
  name    = "dev.myapp.com"
  comment = "Development public DNS zone"
  tags    = local.tags
}

# Dev wildcard
resource "aws_route53_record" "wildcard_dev" {
  zone_id = aws_route53_zone.development.zone_id
  name    = "*.dev.myapp.com"
  type    = "A"

  alias {
    name                   = module.dev_alb.dns_name
    zone_id                = module.dev_alb.zone_id
    evaluate_target_health = true
  }
}
```

### Private Zone (VPC-bound Internal DNS)

```hcl
# Private zone only resolvable within the VPC
resource "aws_route53_zone" "internal" {
  name    = "internal"
  comment = "Internal service discovery zone"

  vpc {
    vpc_id = module.vpc.vpc_id
  }

  tags = local.tags
}

# Internal API gateway
resource "aws_route53_record" "api_internal" {
  zone_id = aws_route53_zone.internal.zone_id
  name    = "api.internal"
  type    = "A"

  alias {
    name                   = module.internal_alb.dns_name
    zone_id                = module.internal_alb.zone_id
    evaluate_target_health = true
  }
}

# Database CNAME (points to managed DB endpoint)
resource "aws_route53_record" "db_internal" {
  zone_id = aws_route53_zone.internal.zone_id
  name    = "db.internal"
  type    = "CNAME"
  ttl     = 300
  records = [module.rds.db_instance_endpoint]
}

# Cache CNAME
resource "aws_route53_record" "cache_internal" {
  zone_id = aws_route53_zone.internal.zone_id
  name    = "cache.internal"
  type    = "CNAME"
  ttl     = 300
  records = [module.redis.primary_endpoint_address]
}
```

## Certificate Configuration

### Primary Region Certificate (Load Balancers)

```hcl
# Wildcard certificate for production
resource "aws_acm_certificate" "prod" {
  domain_name       = "myapp.com"
  subject_alternative_names = ["*.myapp.com"]
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = local.tags
}

# DNS validation records (automated, no manual steps)
resource "aws_route53_record" "prod_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.prod.domain_validation_options :
    dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id = aws_route53_zone.production.zone_id
  name    = each.value.name
  type    = each.value.type
  ttl     = 60
  records = [each.value.record]
}

resource "aws_acm_certificate_validation" "prod" {
  certificate_arn         = aws_acm_certificate.prod.arn
  validation_record_fqdns = [for r in aws_route53_record.prod_cert_validation : r.fqdn]
}
```

### CDN Region Certificate (us-east-1 for CloudFront)

```hcl
# CloudFront requires certificates in us-east-1
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

resource "aws_acm_certificate" "cdn" {
  provider = aws.us_east_1

  domain_name               = "myapp.com"
  subject_alternative_names = ["*.myapp.com"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = local.tags
}

# Validation uses the same Route53 zone (DNS validation is global)
resource "aws_route53_record" "cdn_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.cdn.domain_validation_options :
    dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id = aws_route53_zone.production.zone_id
  name    = each.value.name
  type    = each.value.type
  ttl     = 60
  records = [each.value.record]
}
```

### Development Certificate

```hcl
# Wildcard certificate for development
resource "aws_acm_certificate" "dev" {
  domain_name               = "dev.myapp.com"
  subject_alternative_names = ["*.dev.myapp.com"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = local.tags
}
```

## Load Balancer with Certificate

```hcl
# Application Load Balancer with HTTPS termination
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 9.0"

  name               = "${local.prefix}alb"
  load_balancer_type = "application"
  vpc_id             = module.vpc.vpc_id
  subnets            = module.vpc.public_subnets
  security_groups    = [aws_security_group.alb.id]

  listeners = {
    # Redirect HTTP to HTTPS
    http = {
      port     = 80
      protocol = "HTTP"
      redirect = {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }

    # HTTPS with wildcard certificate
    https = {
      port            = 443
      protocol        = "HTTPS"
      certificate_arn = aws_acm_certificate.prod.arn

      # Default action: return 404 (services register their own rules)
      fixed_response = {
        content_type = "application/json"
        message_body = "{\"error\": \"not found\"}"
        status_code  = "404"
      }
    }
  }

  tags = local.tags
}

# ALB security group: public HTTP/HTTPS only
resource "aws_security_group" "alb" {
  name_prefix = "${local.prefix}alb-"
  vpc_id      = module.vpc.vpc_id
  description = "Public HTTP/HTTPS access for ALB"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP from internet"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS from internet"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [module.vpc.vpc_cidr_block]
    description = "All traffic to VPC"
  }

  tags = merge(local.tags, {
    Name = "${local.prefix}alb-sg"
  })
}
```

## DNS Summary

```
Production DNS:
  myapp.com                -> Production zone
  api.myapp.com            -> API load balancer (A record / alias)
  *.myapp.com              -> Default load balancer (A record / alias)

Development DNS:
  dev.myapp.com            -> Development zone
  api.dev.myapp.com        -> Dev API load balancer
  *.dev.myapp.com          -> Dev default load balancer

Internal DNS (VPC only):
  api.internal             -> Internal API load balancer
  db.internal              -> RDS endpoint (CNAME)
  cache.internal           -> Redis endpoint (CNAME)

Certificates:
  *.myapp.com              -> Primary region (ALB)
  *.myapp.com              -> us-east-1 (CloudFront/CDN)
  *.dev.myapp.com          -> Primary region (Dev ALB)
```
