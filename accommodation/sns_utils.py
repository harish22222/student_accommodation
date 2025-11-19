# accommodation/sns_utils.py
import boto3
from botocore.exceptions import ClientError

REGION_NAME = "us-east-1"
TOPIC_NAME = "BookingNotifications"


def get_or_create_topic():
    sns = boto3.client("sns", region_name=REGION_NAME)

    # List existing topics
    topics = sns.list_topics().get("Topics", [])

    for t in topics:
        if TOPIC_NAME in t["TopicArn"]:
            return t["TopicArn"]

    print("⚠️ SNS topic not found. Creating a new one...")

    response = sns.create_topic(Name=TOPIC_NAME)
    return response["TopicArn"]


def send_sns_notification(subject, message):
    sns = boto3.client("sns", region_name=REGION_NAME)
    topic_arn = get_or_create_topic()

    try:
        response = sns.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )
        print("✅ SNS notification sent:", response)
        return True
    except ClientError as e:
        print("❌ SNS publish error:", e)
        return False
