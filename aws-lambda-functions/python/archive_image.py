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

class FailedToMoveFile(Exception): pass


def lambda_handler(event, context):
  logger.info("Received event: " + json.dumps(event, sort_keys=True))
  s3client = boto3.client('s3')

  today = "{:%Y-%m-%d}".format(datetime.datetime.now(tz.gettz('US/Eastern')))
  bucket = event['bucket'];
  old_key = event['key'];
  try:
    alert = event['Alert'];
  except KeyError:
    alert = False 

  filename = old_key.split('/')[-1]
  fileprefix = filename.replace('.jpg', '')

  if alert == "true":
    new_key = "archive/{}/alert/{}".format(today, filename)
    event_key = "archive/{}/alert/{}.json".format(today, fileprefix)
  else:
    new_key = "archive/{}/falsepositive/{}".format(today, filename)
    event_key = "archive/{}/falsepositive/{}.json".format(today, fileprefix)
    
  logger.info("copying {} to {}".format(old_key, new_key))
  try:
    response = s3client.copy_object(
      Bucket=bucket,
      CopySource="{}/{}".format(bucket, old_key),
      Key=new_key
    )
    logger.info("Copy Response: {}".format(response))
    
  except ClientError as e:
    logger.error("Unable to move {} to {}: {}".format(old_key, new_key, e))
    raise FailedToMoveFile("Unable to move {} to {}: {}".format(old_key, new_key, e))
  if response['ResponseMetadata']['HTTPStatusCode'] == 200:
      logger.info("deleting {}".format(old_key))
      try:
        response = s3client.delete_object(
          Bucket=bucket,
          Key=old_key
        )
      except ClientError as e:
        logger.error("Unable to move {} to {}: {}".format(old_key, new_key, e))

  # Override the key to the new file name
  event['key'] = new_key

  logger.info("Saving Event data as {}".format(event_key))
  response = s3client.put_object(
    ACL='public-read',
    Body=json.dumps(event, sort_keys=True),
    Bucket=event['bucket'],
    Key=event_key,
    ContentType="application/json; charset=utf-8"
  )


  return(event)
### End of Function