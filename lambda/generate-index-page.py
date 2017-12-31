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

prefix = "https://s3.amazonaws.com/{}/"

entry_html = "<a href={}><img src={} width=480></a>\n"

# https://s3.amazonaws.com/security-camera-images-dev1/movies/2017-09-09/20170909191639-01-02.mp4
movie_url = "https://s3.amazonaws.com/{}/movies/{}/{}.mp4"

header = """
<html>
<head><title>Index Page for {}</title></head>
<body>
"""

footer = """<br/>
Generated at {:%Y-%m-%d %H:%M:%S}
</body>
</html>
"""

def lambda_handler(event, context):
  logger.info("Received event: " + json.dumps(event, sort_keys=True))
  today = "{:%Y-%m-%d}".format(datetime.datetime.now(tz.gettz('US/Eastern')))
  html = header.format(today)
  object_list = get_objects()
  # pprint(object_list)
  for o in object_list:
    if "jpg" not in o:
      continue
    url = prefix.format(os.environ['BUCKET_NAME']) + o

    
    filename = o.split('/')[-1]
    fileprefix = filename.replace('.jpg', '')
    mp4 = movie_url.format(os.environ['BUCKET_NAME'], today, fileprefix)

    html = html + entry_html.format(mp4, url)

  html = html + footer.format(datetime.datetime.now(tz.gettz('US/Eastern')))

  # print(html)

  index_key = "archive/{}/index.html".format(today)
  index_url = prefix.format(os.environ['BUCKET_NAME']) + index_key

  client = boto3.client('s3')
  response = client.put_object(
    ACL='public-read',
    Body=html,
    Bucket=os.environ['BUCKET_NAME'],
    Key=index_key,
    ContentType="text/html; charset=utf-8"
  )
  # pprint(response)

  sns = boto3.client('sns')
  response = sns.publish(
    TopicArn='arn:aws:sns:us-east-1:379153516938:DoorAlert',
    Message="New Index File: {}".format(index_url),
    Subject='New Index File Generated',
    )

  event['index_url'] = index_url
  return(event)

def get_objects():
  output = []

  try:
    client = boto3.client('s3')
    response = client.list_objects(
      Bucket=os.environ['BUCKET_NAME'],
      MaxKeys=1024,
      Prefix="archive/{:%Y-%m-%d}/".format(datetime.datetime.now(tz.gettz('US/Eastern')))
    )

    sorted_list = sorted(response['Contents'], key=lambda s: s['LastModified'])

    for o in sorted_list:
      output.append(o['Key'])
  except ClientError as e:
    logger.error("Error: {}".format(e))

  return(output)
  
### END OF FUNCTION ###