import boto3
from botocore.exceptions import ClientError

def send_sns_notification(subject, message):
    """
    Sends an SNS notification to the BookingNotifications topic.
    """
    # ✅ Your confirmed SNS topic ARN from AWS
    topic_arn = "arn:aws:sns:us-east-1:471112797649:BookingNotifications"

    # Create SNS client
    sns_client = boto3.client("sns", region_name="us-east-1")

    try:
        # Publish message to SNS topic
        response = sns_client.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )
        print("✅ SNS notification sent successfully!")
        print("Response:", response)
        return True
    except ClientError as e:
        print("❌ SNS notification failed:", e)
        return False
