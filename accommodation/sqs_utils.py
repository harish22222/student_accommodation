# accommodation/sqs_utils.py
import boto3
import json

def send_booking_message(booking):
    """
    Send booking details to SQS after a booking is created.
    """
    # ✅ Match region with the queue’s actual region in AWS Console
    sqs = boto3.client('sqs', region_name='us-east-1')

    # ✅ Paste your exact queue URL from AWS Console here
    queue_url = "https://sqs.us-east-1.amazonaws.com/471112797649/BookingQueue"

    # ✅ Correct fields from Booking model
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

    try:
        # Send message to SQS
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message_body)
        )
        print("✅ Sent booking message to SQS:", response.get('MessageId'))
    except Exception as e:
        print("❌ Error sending message to SQS:", e)
