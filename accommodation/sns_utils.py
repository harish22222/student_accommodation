import boto3
from botocore.exceptions import ClientError

def send_sns_notification(subject, message):
    """
    Sends an SNS notification to a predefined topic.
    Replace the ARN with your actual SNS Topic ARN.
    """
    # ⚙️ Paste your SNS Topic ARN here
    topic_arn = "arn:aws:sns:us-east-1:471112797649:BookingNotifications"

    sns_client = boto3.client("sns", region_name="us-east-1")

    try:
        response = sns_client.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )
        print("✅ SNS message sent:", response)
        return True
    except ClientError as e:
        print("❌ SNS error:", e)
        return False
