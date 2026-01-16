import boto3
from botocore.exceptions import ClientError

def list_all_iam_roles(session):
    """
    List all IAM roles in the account.

    Args:
        session: boto3.Session object

    Returns:
        list: List of role dicts
    """
    iam_client = session.client('iam')

    response = iam_client.list_roles()
    roles = response['Roles']
    while response.get('IsTruncated', False):
        response = iam_client.list_roles(Marker=response['Marker'])
        roles.extend(response['Roles'])

    return(roles)


def get_role_policies(iam_client, role_name):
    """
    Get all policies attached to a role (both managed and inline).

    Args:
        iam_client: boto3 IAM client
        role_name: Role name string

    Returns:
        dict: {
            'managed': [list of managed policy ARNs],
            'inline': [list of inline policy names]
        }
    """
    managed_policies = []

    managed_response = iam_client.list_attached_role_policies(RoleName=role_name)
    for policy in managed_response['AttachedPolicies']:
        managed_policies.append(policy['PolicyArn'])

    inline_response = iam_client.list_role_policies(RoleName=role_name)

    inline_policies = inline_response['PolicyNames']

    return {
            'managed': managed_policies,
            'inline': inline_policies
            }

def get_policy_document(iam_client, policy_arn):
    """
    Get the actual policy document (JSON) for a managed policy.

    Args:
        iam_client: boto3 IAM client
        policy_arn: Policy ARN string

    Returns:
        dict: Policy document
    """
    # YOUR CODE HERE
    # This is tricky. AWS stores policy versions.
    # Steps:
    # 1. Get policy: iam_client.get_policy(PolicyArn=policy_arn)
    # 2. Get default version ID from response['Policy']['DefaultVersionId']
    # 3. Get policy version: iam_client.get_policy_version(PolicyArn=policy_arn, VersionId=version_id)
    # 4. Return response['PolicyVersion']['Document']

    pass


def get_inline_policy_document(iam_client, role_name, policy_name):
    """
    Get inline policy document.

    Args:
        iam_client: boto3 IAM client
        role_name: Role name
        policy_name: Inline policy name

    Returns:
        dict: Policy document
    """
    # YOUR CODE HERE
    # Simpler than managed policies
    # Call: iam_client.get_role_policy(RoleName=role_name, PolicyName=policy_name)
    # Return: response['PolicyDocument']

    pass

DANGEROUS_ACTIONS = {
    's3:*': 'Full S3 access',
    'iam:*': 'Full IAM access',
    'ec2:*': 'Full EC2 access',
    '*:*': 'Administrator access',
    's3:DeleteBucket': 'Can delete S3 buckets',
    'iam:CreateUser': 'Can create IAM users',
    'iam:AttachUserPolicy': 'Can escalate privileges',
}

def analyze_policy_document(policy_doc):
    """
    Analyze a policy document for dangerous permissions.

    Args:
        policy_doc: Policy document dict

    Returns:
        list: List of dangerous actions found
    """
    dangerous_found = []

    # Policy document structure:
    # {
    #   "Statement": [
    #     {
    #       "Effect": "Allow",
    #       "Action": ["s3:GetObject", "s3:*"],
    #       "Resource": "*"
    #     }
    #   ]
    # }

    # YOUR CODE HERE
    # Steps:
    # 1. Loop through policy_doc['Statement']
    # 2. For each statement with Effect="Allow"
    # 3. Check if any Action matches DANGEROUS_ACTIONS
    # 4. If match found, add to dangerous_found
    # 5. Return list

    # Hints:
    # - Action can be a string or a list
    # - Need to handle both cases
    # - Use wildcard matching (s3:* matches s3:GetObject, etc.)

    pass

if __name__ == '__main__':

    session = boto3.Session(
        profile_name='tooke',
        region_name='us-east-1'
    )

    iam_client = session.client('iam')

    roles = list_all_iam_roles(session)
    print(f"Found {len(roles)} IAM roles")

    for role in roles[:5]:
        print(f"    - {role['RoleName']}")

        policies = get_role_policies(iam_client, role['RoleName'])

        print(f"    Managed Policies: {len(policies['managed'])}")
        for policy in policies['managed']:
            print(f"    - {policy}")

        print(f"   Políticas inline: {len(policies['inline'])}")
        for policy in policies['inline']:
            print(f"     - {policy}")

