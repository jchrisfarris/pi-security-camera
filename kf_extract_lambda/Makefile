
# Static, not sure if needed??
PYTHON=python3
PIP=pip3

FILES=extract_kf.py


package: test clean zipfile

#
# Lambda function management
#

clean: 
	rm -rf __pycache__ *.zip

# # Create the package Zip. Assumes all tests were done
zipfile: $(FILES) ffmpeg ffmpeg-COPYING.GPLv3 ../config.json
	zip -rj $(EXTRACT_PACKAGE) $^  

test: $(FILES)
	for f in $^; do $(PYTHON) -m py_compile $$f; if [ $$? -ne 0 ] ; then echo "$$f FAILS" ; exit 1; fi done