# accommodation/sqs_utils.py
import boto3
import json
from botocore.exceptions import ClientError

REGION_NAME = "us-east-1"
QUEUE_NAME = "BookingQueue"


def get_or_create_queue():
    """Create the SQS queue automatically if not present."""
    sqs = boto3.client("sqs", region_name=REGION_NAME)

    try:
        queue_url = sqs.get_queue_url(QueueName=QUEUE_NAME)["QueueUrl"]
        return queue_url
    except ClientError:
        print("⚠️ Queue not found. Creating a new one...")

        response = sqs.create_queue(
            QueueName=QUEUE_NAME,
            Attributes={
                "VisibilityTimeout": "30"
            }
        )
        return response["QueueUrl"]


def send_sqs_message(message_body):
    sqs = boto3.client("sqs", region_name=REGION_NAME)
    queue_url = get_or_create_queue()

    if isinstance(message_body, dict):
        message_body = json.dumps(message_body)

    try:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body
        )
        print(f"✅ SQS message sent! MessageId: {response['MessageId']}")
        return True
    except Exception as e:
        print(f"❌ Failed to send SQS message: {e}")
        return False


def send_booking_message(booking):
    """Send formatted booking data to SQS."""
    try:
        message_body = {
            "booking_id": booking.id,
            "student": booking.student.user.username,
            "room_number": booking.room.room_number,
            "accommodation": booking.room.accommodation.title,
            "date_booked": str(booking.date_booked),
            "original_price": float(booking.original_price),
            "discount_applied": float(booking.discount_applied),
            "final_price": float(booking.final_price),
        }
        send_sqs_message(message_body)
    except Exception as e:
        print(f"❌ Failed to prepare booking message: {e}")
