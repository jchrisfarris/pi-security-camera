
# pi-security-camera

**Author:** [Chris Farris](http://www.chrisfarris.com) <chris@room17.com>

pi-security-camera is a motion sensing Raspberry Pi Camera that leverages AWS Machine Intelligence to detect objects of interest. It was inspired by @markwest1972 's [smart-security-camera](https://github.com/markwest1972/smart-security-camera). 

# Installation
The Installation consists of two parts, Chef is used to configure the Raspberry Pi, and CloudFormation is used to configure AWS.
See the Installation file for more details.

## Config File
```json
{
    "mail-to": "a-validated-email-address, another-validated-email-address", //required
    "mail-from": "a-validated-email-address",   // required
    "confidence": "65.0",  // required
    "slack-webhook": "https://hooks.slack.com/services/KEEPTHISCONFIDENTIAL",
    "slack-alert-channel": "#camera",
    "slack-falsepositive-channel": "#camera",
    "slack-alert-handle": "@here",
    "alert-labels": ["Human", "People", "Person", "Male", "Female", "Apparel", "Clothing", "Selfie", "Costume", "Portrait"], //required
    "framerate": "1",  //required
    "tempdir": "tmp" // required
}
```
* Note on framerate, this is 1/interval-between-frames, so to get 1 frame very 4 seconds, use 1/4 or 0.25
* if slack-webhook is missing, no slack notifications will be sent
* if slack-webhook is present, slack-alert-channel must also be present
* if slack-falsepositive-channel is missing, no false positive notifications are sent

## Installation Prerequisites

1. Configure SES
  * AWS Requires new accounts to [validate both the sender and receiver email addresses](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/verify-addresses-and-domains.html) when sending with SES.
1. Install [deploy_stack.rb](https://github.com/jchrisfarris/aws_scripts/blob/master/README-deploy_stack.md)
1. Configure a [deploy bucket & Cloudtrail](http://www.chrisfarris.com/what-i-do-to-a-new-aws-account/)
2. Install and configure the chef-sdk on my local box. Make sure to use chef12!!!
3. Open a free Slack account and configure the webhook service (if you want to use slack for notifications)

# How it works
## Process Flow

1. Raspberry Pi runs the [motion](https://motion-project.github.io/) software to detect motion using pixel differences
1. When motion is detected, the Raspberry Pi uploads image to s3://${bucket}/upload/${CameraName}-${DateStamp}-${EventNum}.mp4
2. S3 Notification on that prefix calls the s3-trigger function
3. s3-trigger Calls the StepFunction
4. Extract Lambda splits the mp4 into multiple jpgs (Adds "Images" array to event)
5. RekognitionImageAssessmentLambdaFunction pops the first entry in event['Images'] and looks for a match. If a match is found it sets event['Alert'] to true. Otherwise it returns the event with one less entry in event['Images']
6. If Alert is true, it proceeds to archive the image, Otherwise it calls RekognitionImageAssessmentLambdaFunction again.
7. If there are no more entries in event['Images'], the event['Complete'] is set to true and the S3ArchiveImageLambdaFunction function is called
8. The movie and images are archived in the YYYY-MM-DD folder in the alert or falsepositive directories
9. The new Index file is created (GenerateIndexLambdaFunction)
10. If event['Alert'] is true, an email is sent with the matching keyframe (SendEmailLambdaFunction)
11. Slack notification is sent with the matching keyframe or middle keyframe


## Bucket Layout
* upload/${CameraName}-${DateStamp}-${EventNum}.mp4 (new files dumped here to start the workflow)
* archive/YYYY-MM-DD/alert/${CameraName}-${DateStamp}-${EventNum}.mp4
* archive/YYYY-MM-DD/alert/${CameraName}-${DateStamp}-${EventNum}\_NNN.jpg (first image w/ a valid Rekognition label)
* archive/YYYY-MM-DD/falsepositive/${CameraName}-${DateStamp}-${EventNum}.mp4
* archive/YYYY-MM-DD/falsepositive/${CameraName}-${DateStamp}-${EventNum}\_NNN.jpg (Where NNN is in the middle of the array)
* archive/YYYY-MM-DD/index.html (all alerts and falsepositive images)
* tmp/ (working directory where extract lambda dumps the keyframes)

## Event Data
```json
{
  "bucket": "security-camera-images-dev1",                  # From S3 Trigger
  "movie_key": "upload/DrivewayCam-201712301547-1116.mp4",  # From S3 Trigger
  "movie_filename": "DrivewayCam-201712301547-1116.mp4",    # From S3 Trigger
  "movie_prefix": "DrivewayCam-201712301547-1116",          # From S3 Trigger
  "config": { --contents of config.json -- },               # From S3 Trigger
  "execution_name": "$movie_prefix-epochtimestamp",         # From S3 Trigger

  "Labels": [ ... ],                                        # Added by Rekognition
  "OrientationCorrection": "ROTATE_0",                      # Added by Rekognition
  "Alert": "false",                                         # set by Evaluate Labels
  "Complete": "false",                                      # set by Evaluate Labels when list is exhausted
  "index_url": "https://s3.amazonaws.com/security-camera-images-dev1/archive/2017-12-30/index.html",
  "config": {

    }
  "keyframe_image"  # Added by archive-image, replacing active_image
  A bunch of things are missing here. 
}
```


# Things to do
1. Better Documentation
2. Add Dashboard to CFT
3. Figure out if chef-solo is an option for deployment
4. Figure out how to remove dependency on deploy_stack.rb 
5. Auto-enable the S3 to SNS Notification in the CFT (or provide CLI if the dependency loop cannot be resolved)
6. Better docs on building the Pi
7. Explain why Slack is used and how to set it up




