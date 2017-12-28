
ifndef env
$(error env is not set)
endif

ifndef version
$(error version is not set)
endif

# Shouldn't be overridden
AWS_LAMBDA_FUNCTION_PREFIX ?= smart-security-camera
AWS_TEMPLATE ?= cloudformation/smart-security-camera-Template.yaml
LAMBDA_PACKAGE ?= lambda-$(version).zip
manifest ?= cloudformation/smart-security-camera-Manifest-$(env).yaml
AWS_LAMBDA_FUNCTION_NAME=$(AWS_LAMBDA_FUNCTION_PREFIX)-$(env)
DEPLOYBUCKET ?= pht-deploy
OBJECT_KEY="$(AWS_LAMBDA_FUNCTION_NAME)/$(LAMBDA_PACKAGE)"



# Static, not sure if needed??
PYTHON=python3
PIP=pip3


# Run all tests
test: cfn-validate
	echo $(PATH)

deploy: package.zip cfn-deploy 


#
# Cloudformation Targets

# Validate the template
cfn-validate: $(AWS_TEMPLATE)
	aws cloudformation validate-template --region us-east-1 --template-body file://$(AWS_TEMPLATE)
	
# Deploy the stack
cfn-deploy: cfn-validate modules $(manifest)
	deploy_stack.rb -m $(manifest) pLambdaZipFile=$(OBJECT_KEY) pDeployBucket=$(DEPLOYBUCKET) pEnvironment=$(env)

	# aws s3 cp $(LAMBDA_PACKAGE) s3://$(DEPLOYBUCKET)/$(OBJECT_KEY)

#
# Lambda function management
#

clean: 
	rm -rf __pycache__ *.zip

# Install Lambda modules
modules: clean
	# pip3 install $(MODULE_HOME) -t . --upgrade	

# # Create the package Zip. Assumes all tests were done
# package.zip:  index.py actions/*.py config-*.json
# 	zip -r $(LAMBDA_PACKAGE) $^  

# package: modules package.zip

# # Update the Lambda Code without modifying the CF Stack
# update: package
# 	aws lambda update-function-code --function-name $(AWS_LAMBDA_FUNCTION_NAME) --zip-file fileb://$(LAMBDA_PACKAGE)

