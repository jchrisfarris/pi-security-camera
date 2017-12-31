from __future__ import print_function
import boto3
import json
import logging
import os
import subprocess
from botocore.exceptions import ClientError
from datetime import datetime
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Idea from: https://superuser.com/questions/135117/how-to-convert-video-to-images

# Lambda main routine
def handler(event, context):
    logger.info("Received event: " + json.dumps(event, sort_keys=True))

    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')

    movie_key = event['movie_key']
    movie_fileprefix = event['movie_prefix']

    logger.info("New Movie Object is s3://{}/{} - FilePrefix: {}".format(event['bucket'], movie_key, movie_fileprefix))


    # Create the Temp Dir for my stills
    base_dir = "/tmp/{}".format(movie_fileprefix)
    output_dir = base_dir + "/stills"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    logger.info("Using {} as my base dir and {} as my output_dir".format(base_dir, output_dir))

    try:
        movie_url = s3_client.generate_presigned_url('get_object', Params = {'Bucket': event['bucket'], 'Key': movie_key}, ExpiresIn = 300)
        logger.info("Presigned movie url: {}".format(movie_url))
    except ClientError as e:
        logger.error("Unable to get presigned url for s3://{}/{}: {}".format(event['bucket'], movie_key, e))
        raise Exception("Unable to get presigned url for s3://{}/{}: {}".format(event['bucket'], movie_key, e))


    # movie_local_path = "{}/{}".format(base_dir, movie_filename)

    # try:
    #     s3_resource.Bucket(movie_bucket).download_file(movie_key, movie_local_path)
    #     time.sleep(1)
    # except ClientError as e:
    #     if e.response['Error']['Code'] == "404":
    #         logger.error("The object does not exist.")
    #     else:
    #         logger.error("Error downloading movie: {}".format(e))

    # If I'm in the lambda, I won't get the path via the event
    # Use the default lambda location
    ffmpeg_path = '/var/task/ffmpeg'
    if ffmpeg_path in event:
        ffmpeg_path = event['ffmpeg_path']

    # Run ffmpeg to extract them
    command = "{} -i '{}' -r {} {}/{}_%04d.jpg".format(ffmpeg_path, movie_url, event['config']['framerate'], 
        output_dir, movie_fileprefix)
    logger.info("About to execute ffmpeg command: {}".format(command))
    try:
        cmd_status = subprocess.call(command, shell=True)
        logger.info("ffmpeg output: {}".format(cmd_status))
    except Exception as e:
        logger.info("ffmpeg Error: {}".format(e))

    # Get a list of the created files
    output_keys = []
    for f in os.listdir(output_dir):
        logger.info("Output file: {}".format(f))
        image_key = "{}/{}".format(movie_fileprefix, f)

        # Push files to S3
        try:
            file  = open("{}/{}".format(output_dir, f), 'rb')
            response = s3_client.put_object(
                Body=file,
                Bucket=event['bucket'],
                ContentType='image/jpeg',
                Key='{}/{}'.format(event['config']['tempdir'], image_key),
            )
            file.close()
            output_keys.append(image_key)
        except ClientError as e:
            logger.error("Error Putting {} in {}".format(image_key, event['bucket']))

    output_keys.sort()
    event['num_images'] = len(output_keys)
    event['images'] = output_keys
    event['queue'] = output_keys
    return(event)
