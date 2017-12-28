
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
export OBJECT_KEY="$(AWS_LAMBDA_FUNCTION_NAME)/$(LAMBDA_PACKAGE)"


# Run all tests
test: cfn-validate
	cd lambda && $(MAKE) test
	echo $(PATH)

deploy: package cfn-deploy 

package:
	cd lambda && $(MAKE) package


clean: 
	cd lambda && $(MAKE) clean

#
# Cloudformation Targets
#

# Validate the template
cfn-validate: $(AWS_TEMPLATE)
	aws cloudformation validate-template --region us-east-1 --template-body file://$(AWS_TEMPLATE)
	
# Deploy the stack
cfn-deploy: cfn-validate modules $(manifest)
	aws s3 cp $(LAMBDA_PACKAGE) s3://$(DEPLOYBUCKET)/$(OBJECT_KEY)
	deploy_stack.rb -m $(manifest) pLambdaZipFile=$(OBJECT_KEY) pDeployBucket=$(DEPLOYBUCKET) pEnvironment=$(env)

# # Update the Lambda Code without modifying the CF Stack
update: package
	aws lambda update-function-code --function-name $(AWS_LAMBDA_FUNCTION_NAME) --zip-file fileb://$(LAMBDA_PACKAGE)

