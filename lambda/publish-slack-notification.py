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

    if 'slack-webhook' not in event['config']:
        logger.info("No slack-webhook defined. Skipping Slack Function")
        return(event)

    if 'slack-alert-channel' not in event['config']:
        logger.error("No Slack Channel Defined. Cannot send slack message")
        return(event)

    filename = event['keyframe_image'].split('/')[-1]
    camera = filename.split('-')[0]
    icon = ":camera:"
    ping = "" # Default is no alert
    if event['Alert'] == "true":
        icon = ":camera_with_flash:"
        channel = event['config']['slack-alert-channel']
        if event['config']['slack-alert-handle']:
            ping = "{} - ".format(event['config']['slack-alert-handle']) 
    else:
        if 'slack-falsepositive-channel' not in event['config']:
            logger.info("No slack-falsepositive-channel defined. Not sending this message")
            return(event)
        channel = event['config']['slack-falsepositive-channel']
    
    movie_url = "https://s3.amazonaws.com/{}/{}".format(event['bucket'], event['movie_key'])
    image_url = "https://s3.amazonaws.com/{}/{}".format(event['bucket'], event['keyframe_image'])
    attachments = [{"image_url": image_url}]

    message = "{}Image from: {} Alert: {}\n{}\n{}".format(ping, datetime.datetime.now(tz.gettz('US/Eastern')), 
            event['Alert'], event['index_url'], movie_url)

    slack_message = {
        'channel': channel,
        'username': camera,
        'text': message,
        'icon_emoji': icon,
        'attachments': attachments
    }

    req = Request(event['config']['slack-webhook'], json.dumps(slack_message))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)

    return(event)

  
### END OF FUNCTION ###