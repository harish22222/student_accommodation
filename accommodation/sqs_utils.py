# accommodation/sqs_utils.py
import boto3
import json
from botocore.exceptions import ClientError


# ✅ Your actual SQS queue URL
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/471112797649/BookingQueue"

# ✅ AWS region
REGION_NAME = "us-east-1"


def send_sqs_message(message_body):
    """
    Sends any message (JSON string or dict) to the BookingQueue.
    Automatically converts dict to JSON if needed.
    """
    sqs = boto3.client("sqs", region_name=REGION_NAME)

    # Convert to JSON if a dict is passed
    if isinstance(message_body, dict):
        message_body = json.dumps(message_body)

    try:
        response = sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=message_body
        )
        print(f"✅ SQS message sent successfully! MessageId: {response['MessageId']}")
        return True
    except ClientError as e:
        print(f"❌ SQS ClientError: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error sending SQS message: {e}")
        return False


def send_booking_message(booking):
    """
    Sends booking details to SQS after a booking is created in Django.
    """
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

        # ✅ Send to queue
        send_sqs_message(message_body)
    except Exception as e:
        print(f"❌ Failed to prepare booking message: {e}")
