import json
import cv2
import tempfile
from PIL import Image
from io import BytesIO
import boto3


s3 = boto3.client('s3')

def get_video_file(bucket, key):
    video_file = s3.get_object(Bucket=bucket, Key=key)['Body'].read()
    return video_file


def upload_image_file(image_byte_data, bucket, key):
    s3.put_object(Bucket=bucket, Key=key, Body=image_byte_data, ContentType="image/png")

def generate_thumbnail(video_byte_data):

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(video_byte_data)


    video_capture = cv2.VideoCapture(temp_file_path, cv2.CAP_ANY)

    success, frame = video_capture.read()

    if success:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        thumbnail_image = Image.fromarray(frame_rgb)

        thumbnail_size = (320,320)
        thumbnail_image.resize(thumbnail_size)

        thumbnail_data = BytesIO()

        thumbnail_image.save(thumbnail_data, format='PNG')

        thumbnail_bytes = thumbnail_data.getvalue()

        return thumbnail_bytes
    else:
        raise ValueError('Unable to read video frame')


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']


    video_file = get_video_file(bucket, key)
    image_output_file = generate_thumbnail(video_file)
    upload_image_file(image_output_file, "thumbnail876", key.split(".")[0]+".png")
    
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
            }
        ),
    }
