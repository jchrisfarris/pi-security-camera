import boto3
import botocore
from botocore.exceptions import ClientError
import os
import json

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
  logger.info("Received event: " + json.dumps(event, sort_keys=True))

  # Mark complete if the list is empty 
  if len(event['queue']) == 0:
    event['Complete'] = "true"
    return(event)

  # otherwise pop the first image and do it.
  event['active_image'] = event['queue'].pop(0) # pop(0) grabs from the front of the list

  logger.info("Calling Rekognition on {}".format(event['active_image']))
  # Now do what we came here to do - send to rekoginition
  client = boto3.client('rekognition')
  try:
    response = client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': event['bucket'],
                'Name': "{}/{}".format(event['config']['tempdir'], event['active_image'])
            }
        },
        MaxLabels=20,
        MinConfidence=20.0
    )
  except ClientError as e:
    logger.error("Unable to call Rekognition for image {}: {}".format(event['active_image'], e))
    return(event.pop('active_image', None))

  logger.info("Rekognition Response: {}".format(response))
  # Now process the results
  if 'Labels' in response:
    for label in response['Labels']:
      if label['Name'] in event['config']['alert-labels'] and label['Confidence'] >= float(event['config']['confidence']):
        # Winner Winner Chicken Dinner
        event['Alert'] = "true"
        # And add the results from Rekognition
        event['Labels'] = response['Labels']
        event['OrientationCorrection'] = response['OrientationCorrection']
        return(event)
  else:
    logger.error("No Labels in response from Rekognition: {}".format(response))

  # The following will cause the state machine to fail around 20 or so 
  # images due to the size of the json object that can be passed between states
  # event['Misses'][event['active_image']] = response['Labels']

  
  # Found Nothing. Move on to the next
  return(event)
### End of Function