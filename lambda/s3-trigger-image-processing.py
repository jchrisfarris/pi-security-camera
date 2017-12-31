import boto3
import botocore
from botocore.exceptions import ClientError
import os
import json
import time

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
  # logger.info("Received event: " + json.dumps(event, sort_keys=True))
  message = json.loads(event['Records'][0]['Sns']['Message'])
  logger.info("Received message: " + json.dumps(message, sort_keys=True))

  new_event = {}
  new_event['bucket'] = message['Records'][0]['s3']['bucket']['name']
  new_event['movie_key'] = message['Records'][0]['s3']['object']['key']

  new_event['movie_filename'] = new_event['movie_key'].split('/')[-1]
  new_event['movie_prefix'] = new_event['movie_filename'].replace(".mp4", "")

  new_event['config'] = json.load(open(os.environ['CONFIG_FILE']))

  new_event['execution_name'] = "{}-{}".format(new_event['movie_prefix'], int(time.time()))

  # The Choice requires these be present
  new_event['Alert'] = "false"
  new_event['Complete'] = "false"
  new_event['Misses'] = {}

  client = boto3.client('stepfunctions')
  response = client.start_execution(
      stateMachineArn=os.environ['STEP_MACHINE_ARN'],
      name=new_event['execution_name'],
      input=json.dumps(new_event, sort_keys=True)
  )

