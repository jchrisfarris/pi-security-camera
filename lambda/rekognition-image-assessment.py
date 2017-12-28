import boto3
import botocore
from botocore.exceptions import ClientError
import os
import json

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

LABELS=['Human', 'People', 'Person', 'Male', 'Female', 'Apparel', 'Clothing', 'Selfie', 'Costume', 'Portrait']

def lambda_handler(event, context):
  logger.info("Received event: " + json.dumps(event, sort_keys=True))

  # Mark complete if the list is empty 
  if len(event['images']) == 0:
    event['Complete'] = "true"
    return(event)

  # otherwise pop the first image and do it.
  event['active_image'] = event['images'].pop()

  # Now do what we came here to do - send to rekoginition
  client = boto3.client('rekognition')
  try:
    response = client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': event['bucket'],
                'Name': event['active_image']
            }
        },
        MaxLabels=20,
        MinConfidence="20.0"
    )
  except ClientError as e:
    logger.error("Unable to call Rekognition for image {}: {}".format(event['active_image'], e))
    return(event.pop('active_image', None))

  # Now process the results
  if 'Labels' in response:
    for label in response['Labels']:
      if label['Name'] in LABELS and label['Confidence'] >= float(os.environ['MIN_CONFIDENCE']):
        # Winner Winner Chicken Dinner
        event['Alert'] = "true"
        # And add the results from Rekognition
        event.update(response)
        return(event)

  # Found Nothing. Move on to the next
  return(event)
### End of Function