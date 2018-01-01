

ifndef env
$(error env is not set)
endif

ifndef version
$(error version is not set)
endif


# Static, not sure if needed??
PYTHON=python3
PIP=pip3

FILES=error-handler.py publish-slack-notification.py s3-trigger-image-processing.py archive-image.py generate-index-page.py rekognition-image-assessment.py send-notification.py


package: test clean zipfile

#
# Lambda function management
#

clean: 
	rm -rf __pycache__ *.zip

# Install Lambda modules
modules: clean
	# pip3 install $(MODULE_HOME) -t . --upgrade	

# # Create the package Zip. Assumes all tests were done
zipfile: $(FILES) ../config.json
	zip -rj $(LAMBDA_PACKAGE) $^  

test: $(FILES)
	for f in $^; do $(PYTHON) -m py_compile $$f; if [ $$? -ne 0 ] ; then echo "$$f FAILS" ; exit 1; fi done