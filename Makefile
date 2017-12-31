
ifndef env
$(error env is not set)
endif

ifndef version
$(error version is not set)
endif

# Shouldn't be overridden
export AWS_LAMBDA_FUNCTION_PREFIX ?= smart-security-camera
export AWS_TEMPLATE ?= cloudformation/smart-security-camera-Template.yaml
export LAMBDA_PACKAGE ?= lambda-$(version).zip
export manifest ?= cloudformation/smart-security-camera-Manifest-$(env).yaml
export AWS_LAMBDA_FUNCTION_NAME=$(AWS_LAMBDA_FUNCTION_PREFIX)-$(env)
export DEPLOYBUCKET ?= pht-deploy
export OBJECT_KEY=$(AWS_LAMBDA_FUNCTION_NAME)/$(LAMBDA_PACKAGE)

FUNCTIONS= smartcamera-errorhandler-$(env) smartcamera-image-assessment-$(env) smartcamera-trigger-statemachine-$(env) smartcamera-send-email-$(env) smartcamera-archive-image-$(env) smartcamera-generate-index-page-$(env) smartcamera-publish-slack-notification-$(env)


# The ffmpeg binary is large and slows down upload and probably container starts. We make it its own package
export EXTRACT_PACKAGE ?= extract-lambda-$(version).zip
export EXTRACT_OBJECT_KEY=$(AWS_LAMBDA_FUNCTION_NAME)/$(EXTRACT_PACKAGE)
EXTRACT_FUNCTION=smartcamera-extract-keyframes-$(env)


.PHONY: $(FUNCTIONS)

# Run all tests
test: cfn-validate
	cd lambda && $(MAKE) test
	cd kf_extract_lambda && $(MAKE) test

deploy: package kf-extract cfn-deploy 

clean: 
	cd lambda && $(MAKE) clean
	cd kf_extract_lambda && $(MAKE) clean

#
# Cloudformation Targets
#

# Validate the template
cfn-validate: $(AWS_TEMPLATE)
	aws cloudformation validate-template --region us-east-1 --template-body file://$(AWS_TEMPLATE)
	
# Deploy the stack
cfn-deploy: cfn-validate $(manifest)
	aws s3 cp lambda/$(LAMBDA_PACKAGE) s3://$(DEPLOYBUCKET)/$(OBJECT_KEY)
	aws s3 cp kf_extract_lambda/$(EXTRACT_PACKAGE) s3://$(DEPLOYBUCKET)/$(EXTRACT_OBJECT_KEY)
	deploy_stack.rb -m $(manifest) pLambdaZipFile=$(OBJECT_KEY) pExtractLambdaZipFile=$(EXTRACT_OBJECT_KEY) pDeployBucket=$(DEPLOYBUCKET) pEnvironment=$(env)

#
# Lambda Targets
#
package:
	cd lambda && $(MAKE) package

# FFMPEG Binary is big, so we make t
kf-extract:
	cd kf_extract_lambda && $(MAKE) package

# # Update the Lambda Code without modifying the CF Stack
update: package $(FUNCTIONS)
	for f in $(FUNCTIONS) ; do \
	  aws lambda update-function-code --function-name $$f --zip-file fileb://lambda/$(LAMBDA_PACKAGE) ; \
	done

update-kf-extract: kf-extract
	aws lambda update-function-code --function-name $(EXTRACT_FUNCTION) --zip-file fileb://kf_extract_lambda/$(EXTRACT_PACKAGE)
