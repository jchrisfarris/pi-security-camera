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
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64


def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event, sort_keys=True))

    try:
        txtString = "Error occured in {}:\n{}\n\nMovie File: {}".format(event['execution_name'], event, event['movie_key'])
    except KeyError:
        txtString = "Smart Pi Camera Error occured: {}".format(event)

    message = MIMEMultipart()
    message['From'] = event['config']['mail-from']
    # Override this for testing
    message['To'] = event['config']['mail-to']
    message['Subject'] = "⚠️ Error processing image ⚠️"

    body = MIMEMultipart('alternative')
    body.attach(MIMEText(txtString, 'plain')) # Text body of the email
    message.attach(body)

    # part = MIMEApplication(open("/tmp/" + image_filename, "rb").read())
    # part.add_header('Content-Disposition', 'attachment', filename=image_filename)
    # message.attach(part)

    ses_client = boto3.client('ses')
    response = ses_client.send_raw_email(
        Source=message['From'],
        RawMessage={
         'Data': message.as_string(),
    })

    raise Exception("Failed Stack")
    return(event)