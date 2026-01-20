# AWS Infrastructure Tools

A collection of Python-based CLI tools for auditing and managing AWS infrastructure and security.

##  Purpose

These tools help DevOps engineers, Cloud Architects, and Security teams:
- Audit VPC configurations across AWS accounts
- Classify subnets as public or private
- Analyze IAM roles for security vulnerabilities
- Identify overpermissioned roles and dangerous actions
- Generate comprehensive infrastructure and security reports

Built with production-grade error handling, proper AWS SDK patterns, and security best practices.

##  Tools Included

### 1. VPC Inventory Tool (`vpc_inventory.py`)

Comprehensive network inventory tool that lists all VPCs and their associated resources in a region.

**Features:**
- Lists all VPCs with CIDR blocks
- Inventories subnets with availability zone information
- Automatically classifies subnets as PUBLIC or PRIVATE based on route table analysis
- Lists route tables and Internet Gateways
- Supports multiple AWS profiles
- Clean, formatted output for easy analysis

**Usage:**
```bash
# List VPCs in a specific region
python vpc_inventory.py --region us-east-1

# Use a specific AWS profile
python vpc_inventory.py --profile production --region us-west-2
```

**Example Output:**
```
Found 2 VPCs

VPC: vpc-abc123 (10.0.0.0/16)
  Route Tables: 2
  Internet Gateways: 1
    - igw-xyz789
  Subnets: 4
    - [PUBLIC] subnet-pub1 (10.0.1.0/24) in us-east-1a
    - [PUBLIC] subnet-pub2 (10.0.2.0/24) in us-east-1b
    - [PRIVATE] subnet-prv1 (10.0.11.0/24) in us-east-1a
    - [PRIVATE] subnet-prv2 (10.0.12.0/24) in us-east-1b
```

**Use Cases:**
- Network security audits
- Compliance verification
- Troubleshooting connectivity issues
- Infrastructure documentation

---

### 2. IAM Security Auditor (`iam_auditor.py`)

Production-grade security tool that analyzes IAM roles for overpermissioned policies and dangerous actions.

**Features:**
- Scans all IAM roles in an AWS account
- Analyzes both managed and inline policies
- Identifies dangerous permissions (full S3 access, IAM user creation, admin access, etc.)
- Handles IAM API pagination automatically
- Generates security risk reports with actionable recommendations
- Calculates account-wide security risk percentage

**Dangerous Actions Detected:**
- `*:*` - Full administrator access (CRITICAL)
- `iam:*` - Full IAM access (can create admin users)
- `s3:*` - Full S3 access (can delete all buckets)
- `ec2:*` - Full EC2 access
- `s3:DeleteBucket` - Can permanently delete S3 buckets
- `iam:CreateUser` - Can create new IAM users
- `iam:AttachUserPolicy` - Can escalate privileges

**Usage:**
```bash
# Audit IAM roles in default profile
python iam_auditor.py --region us-east-1

# Use specific AWS profile
python iam_auditor.py --profile production --region us-east-1
```

**Example Output:**
```
=== IAM Security Audit Report ===

Total IAM roles: 23

⚠️  HIGH RISK ROLES (3):

Role: legacy-admin-role
    - *:*: Administrator access (CRITICAL)
    - iam:*: Full IAM access

Role: data-processing-role
    - s3:*: Full S3 access
    - s3:DeleteBucket: Can delete S3 buckets

Role: backup-automation
    - iam:CreateUser: Can create IAM users

=== Summary ===
Roles analyzed: 23
High-risk roles: 3
Risk percentage: 13.0%
```

**Use Cases:**
- Security audits and compliance checks
- Identifying overpermissioned roles for least privilege enforcement
- Pre-deployment security validation
- Regular security posture assessment
- Incident response and threat hunting

##  Requirements

- Python 3.8+
- boto3
- botocore
- argparse (standard library)
- AWS credentials configured

##  Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/aws-infra-tools.git
cd aws-infra-tools
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure AWS credentials:
```bash
aws configure
```

## 🔧 Configuration

### AWS Credentials

All tools support multiple authentication methods (in priority order):
1. Command-line `--profile` argument
2. `AWS_PROFILE` environment variable
3. `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables
4. AWS credentials file (`~/.aws/credentials`)
5. IAM role (when running on EC2/ECS)

### Example: Using Profiles
```bash
# Configure a profile
aws configure --profile production

# Use with any tool
python vpc_inventory.py --profile production --region us-east-1
python iam_auditor.py --profile production --region us-east-1
```

### Required IAM Permissions

**For VPC Inventory:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeVpcs",
        "ec2:DescribeSubnets",
        "ec2:DescribeRouteTables",
        "ec2:DescribeInternetGateways"
      ],
      "Resource": "*"
    }
  ]
}
```

**For IAM Auditor:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:ListRoles",
        "iam:GetRole",
        "iam:ListAttachedRolePolicies",
        "iam:ListRolePolicies",
        "iam:GetPolicy",
        "iam:GetPolicyVersion",
        "iam:GetRolePolicy"
      ],
      "Resource": "*"
    }
  ]
}
```

**For Terraform State Auditor:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::your-terraform-state-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeVpcs"
      ],
      "Resource": "*"
    }
  ]
}
```

## How It Works

### VPC Subnet Classification Algorithm

The VPC inventory tool determines if a subnet is PUBLIC or PRIVATE by analyzing route tables:

1. Find the route table associated with the subnet
2. If no explicit association, use the VPC's main route table
3. Check if the route table contains a route to an Internet Gateway (target starts with `igw-`)
4. If IGW route exists → PUBLIC, otherwise → PRIVATE

**Why this matters:**
- Databases should NEVER be in public subnets
- Application servers typically belong in private subnets
- Only load balancers and bastion hosts should be public

### IAM Policy Analysis

The IAM auditor performs deep analysis of IAM policies:

1. Lists all IAM roles in the account (with pagination)
2. For each role, retrieves both managed and inline policies
3. For managed policies, fetches the default policy version
4. Parses policy documents to extract allowed actions
5. Compares actions against a list of dangerous permissions
6. Flags roles with overly permissive access

**Security Principles:**
- Least privilege: Roles should have minimum necessary permissions
- Separation of duties: No single role should have multiple dangerous actions
- Defense in depth: Multiple layers of security controls

##  Security Best Practices

### Running These Tools Safely

✅ **Do:**
- Use read-only IAM credentials when possible
- Run in a separate audit account with cross-account roles
- Store output in secure locations
- Review findings with security team
- Implement least privilege for the tools themselves

❌ **Don't:**
- Run with admin credentials unless necessary
- Store credentials in code or logs
- Share audit reports publicly (may contain sensitive info)
- Make infrastructure changes based solely on automated findings

##  Learning Resources

These tools were built following industry best practices from:

- [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [OWASP Cloud Security](https://owasp.org/www-project-cloud-security/)

##  Contributing

Contributions are welcome! Areas for improvement:

**VPC Inventory:**
- [ ] Add VPC peering connections
- [ ] Add NAT Gateway analysis
- [ ] Export to JSON/CSV formats
- [ ] Multi-region support in single run

**IAM Auditor:**
- [ ] Add wildcard permission matching (s3:* catches s3:GetObject)
- [ ] Support for IAM users and groups
- [ ] Policy simulation for "what-if" analysis
- [ ] Integration with AWS Access Analyzer

##  License

MIT License - feel free to use these tools in your own projects.

## 👤 Author

**Bruno Levy**

