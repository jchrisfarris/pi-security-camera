from __future__ import print_function
import boto3
import botocore
from botocore.exceptions import ClientError
import os
import json
from pprint import pprint
import datetime
from dateutil import tz
import logging
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event, sort_keys=True))

    image_key = event['keyframe_image']
    image_filename = event['keyframe_image'].split('/')[-1]

    s3_resource = boto3.resource('s3')
    s3_resource.Bucket(event['bucket']).download_file(image_key, "/tmp/" + image_filename )

    htmlString = "<table border=0><tr><td><b>Label</b></td><td><b>Confidence</b></td></tr>\n"
    row = "<tr><td>{}</td><td>{}</td></tr>\n"
    txtString = "Label\t\t\tConfidence\n"

    for l in event['Labels']:
        c = "{0:.2f}".format(float(l['Confidence']))
        htmlString = htmlString + row.format(l['Name'], c)
        txtString = txtString + "{}\t\t\t{}\n".format(l['Name'], c)

    movie_url = "https://s3.amazonaws.com/{}/{}".format(event['bucket'], event['movie_key'])
    txtString = txtString + "\nMovie Link: " + movie_url
    htmlString = htmlString + "<br><a href=\"{}\">Movie</a>".format(movie_url)


    message = MIMEMultipart()
    message['From'] = event['config']['mail-from']
    # Override this for testing
    message['To'] = event['config']['mail-to']
    message['Subject'] = '⏰ Alarm Event detected! ⏰'

    body = MIMEMultipart('alternative')
    body.attach(MIMEText(txtString, 'plain')) # Text body of the email
    body.attach(MIMEText(htmlString, 'html')) # Text body of the email
    message.attach(body)

    part = MIMEApplication(open("/tmp/" + image_filename, "rb").read())
    part.add_header('Content-Disposition', 'attachment', filename=image_filename)
    message.attach(part)

    ses_client = boto3.client('ses')
    response = ses_client.send_raw_email(
        Source=message['From'],
        RawMessage={
         'Data': message.as_string(),
    })














    return(event)