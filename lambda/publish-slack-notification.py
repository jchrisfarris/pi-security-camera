# Lambda to send SNS Messages to Slack
from __future__ import print_function

import boto3
import json
import logging
import os
import datetime
from dateutil import tz

from base64 import b64decode
from urllib2 import Request, urlopen, URLError, HTTPError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event, sort_keys=True))
    filename = event['key'].split('/')[-1]
    camera = filename.split('-')[0]
    icon = ":camera:"
    if event['Alert'] == "true":
        icon = ":camera_with_flash:"
    
    image_url = "https://s3.amazonaws.com/{}/{}".format(event['bucket'], event['key'])
    attachments = [{"image_url": image_url}]

    slack_message = {
        'channel': os.environ['SLACK_CHANNEL'],
        'username': camera,
        'text': "Image from: {} Alert: {}\n{}".format(datetime.datetime.now(tz.gettz('US/Eastern')), 
            event['Alert'], event['index_url']),
        'icon_emoji': icon,
        'attachments': attachments
    }

    req = Request(os.environ['HOOK_URL'], json.dumps(slack_message))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)

  
### END OF FUNCTION ###