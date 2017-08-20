#!/bin/bash

BUCKET=$1
VERSION=$2
if [ -z $VERSION ] ; then
	echo "Usage: $0 <bucket_name> <version_id>"
	exit 1
fi

cd ../aws-lambda-functions/nodejs
for dir in * ; do

	if [ -d $dir ] ; then
		if [ -f $dir/package.json ] ; then
			cd $dir
			npm install
			zip -r ../$dir.zip *
			cd ..
		else
			zip -j $dir.zip $dir/* 
		fi
		if [ ! -f $dir.zip ] ; then
			echo "Aborting. $dir.zip is missing"
			exit 1
		fi
		aws s3 cp $dir.zip s3://$BUCKET/lambda/$VERSION/$dir.zip
		rm $dir.zip
	fi
done
aws s3 ls s3://$BUCKET/lambda/$VERSION/