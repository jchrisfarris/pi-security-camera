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

  today = "{:%Y-%m-%d}".format(datetime.datetime.now(tz.gettz('US/Eastern')))
  bucket = event['bucket'];

  alert = event['Alert']
  
  movie_key = event['movie_key']
  movie_filename = movie_key.split('/')[-1]


  if alert == "true":
    image_key = "{}/{}".format(event['config']['tempdir'], event['active_image'])
    image_filename = image_key.split('/')[-1]
    new_image_key = "archive/{}/alert/{}".format(today, image_filename)
    new_movie_key = "archive/{}/alert/{}".format(today, movie_filename)
  else:
    image_key = "{}/{}".format(event['config']['tempdir'], findMiddle(event['images']))
    image_filename = image_key.split('/')[-1]
    new_image_key = "archive/{}/falsepositive/{}".format(today, image_filename)
    new_movie_key = "archive/{}/falsepositive/{}".format(today, movie_filename)
    logger.info("Picked {} as random keyframe vs {}".format(image_key, event['active_image']))

    
  move_file(bucket, image_key, new_image_key)
  move_file(bucket, movie_key, new_movie_key)

  # Override the key to the new file name
  event['movie_key'] = new_movie_key
  event['keyframe_image'] = new_image_key
  del event['active_image']
  return(event)
### End of Function

def findMiddle(input_list):
  middle = float(len(input_list))/2
  if middle % 2 != 0:
      return(input_list[int(middle - .5)])
  else:
      return(input_list[int(middle)])

def move_file(bucket, old_key, new_key):
  s3client = boto3.client('s3')
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