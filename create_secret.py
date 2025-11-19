import boto3
import json
from botocore.exceptions import ClientError

REGION = "us-east-1"
SECRET_NAME = "student-accommodation-secrets"

secret_value = {
    "DJANGO_SECRET_KEY": "django-insecure-k0_^ahy01jr9o5y5+!$7-_svf^+s4av9vmw(^*=1j#dk9seqr9",
    "AWS_S3_BUCKET": "studentaccommodation-media-harish-new-lab"
}

def create_secret():
    client = boto3.client("secretsmanager", region_name=REGION)

    try:
        client.create_secret(
            Name=SECRET_NAME,
            SecretString=json.dumps(secret_value)
        )
        print(f"✅ Secret created: {SECRET_NAME}")

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceExistsException':
            print(f"ℹ️ Secret already exists: {SECRET_NAME}")
        else:
            print("❌ Error creating secret:", e)


if __name__ == "__main__":
    print("🚀 Creating Secrets Manager secret...")
    create_secret()
import boto3
import json
from botocore.exceptions import ClientError

REGION = "us-east-1"
SECRET_NAME = "student-accommodation-secrets"

secret_value = {
    "DJANGO_SECRET_KEY": "django-insecure-k0_^ahy01jr9o5y5+!$7-_svf^+s4av9vmw(^*=1j#dk9seqr9",
    "AWS_S3_BUCKET": "studentaccommodation-media-harish-new-lab"
}

def create_secret():
    client = boto3.client("secretsmanager", region_name=REGION)

    try:
        client.create_secret(
            Name=SECRET_NAME,
            SecretString=json.dumps(secret_value)
        )
        print(f"✅ Secret created: {SECRET_NAME}")

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceExistsException':
            print(f"ℹ️ Secret already exists: {SECRET_NAME}")
        else:
            print("❌ Error creating secret:", e)


if __name__ == "__main__":
    print("🚀 Creating Secrets Manager secret...")
    create_secret()

