

# Process Flow

1. Raspberry Pi uploads image to s3://bucket/uploads/CameraName-DateStamp-EventNum.mp4
2. SNS Trigger on that prefix calls the s3-trigger function
3. s3-trigger function publishes to Extract Lambda trigger topic
4. Extract Lambda splits the mp4 into multiple jpgs
5. Extrct Lambda publishes to the SmartCamera Trigger Topic (which was passed to the Extract Lambda by the s3-trigger function)
