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
  message = json.loads(event['Records'][0]['Sns']['Message'])
  logger.info("Received message: " + json.dumps(message, sort_keys=True))

  message['movie_filename'] = message['movie_key'].split('/')[-1]
  message['movie_prefix'] = movie_filename.replace(".mp4", "")

  client = boto3.client('stepfunctions')
  response = client.start_execution(
      stateMachineArn=os.environ['STEP_MACHINE_ARN'],
      name=message['movie_prefix'],
      input=message
  )
### End of Function