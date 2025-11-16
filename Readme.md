# 2026_1-6-20
## Team Members
- Zixin Zhang
- Pol Plana

## Task 6.1: Centralize the logs of your application instances
### ❓ Question 1: What issues have you met when following the above instructions?
> The main issue we encountered was that the log files were not being uploaded to the S3 bucket immediately when running the web application locally. Initially, we expected to see logs appearing in the S3 bucket as soon as we started generating log entries through the application. However, after reviewing the logging configuration in `settings.py`, we discovered that the `maxBytes` parameter was set to 5 KB (`5 * 1024` bytes). This means that the log file must reach at least 5 KB in size before the log rotation mechanism triggers and uploads the file to S3. Once we understood this behavior, we were able to verify the functionality by generating enough log entries to exceed the threshold.

---

### ❓ Question 2: Run the web application locally and play with the log size of the s3 handler and see how the bucket keeps receiving log files. Share your thoughts. When you run the web application can you see the logs where you expected?
> After understanding the 5 KB minimum file size requirement, we tested the logging functionality by repeatedly submitting the signup form to generate log entries. Each signup creates multiple log messages, which helped us quickly reach the 5 KB threshold. Once the log file exceeded this size, the `S3RotatingFileHandler` automatically performed the rollover operation: it renamed the current log file with a timestamp (e.g., `s3.2025-11-16_11-06-49.log`), uploaded it to the S3 bucket under the `logs/` prefix, and created a new empty `s3.log` file to continue logging. 
>
> The logs appeared exactly where we expected them in the S3 bucket: `s3://team20.ccbda.upc.edu/logs/`. This centralized logging approach is very effective for production environments where multiple EC2 instances need to send logs to a common location for monitoring and analysis. The rotation mechanism ensures that log files don't grow indefinitely while maintaining a complete history in S3. The verbose log format with instance ID, module, and line numbers makes it easy to debug issues and trace activity across different instances.

![S3 Bucket with Logs](images/q2-s3-logs.png)

---

## Task 6.2: Deliver static content using a Content Delivery Network
### ❓ Question 3: Take a couple of screenshots of you S3 and CloudFront consoles to demonstrate that everything worked all right.
>
>
![S3 Uploaded Static Files](images/q3-s3-console.png)

![S3 Files in the AWS Console](images/q3-s3-aws-console.png)

![CloudFront Console Working](images/q3-cloudfront-console.png)

![CloudFront Distribution](images/q3-cdn.png)

![CDN Working Fonts Browser](images/q3-cdn-working-fonts.png)

---

## Task 6.3: Create a new option to retrieve the list of leads
![Admin Search](images/search.png)
### ❓ Question 4: Has everything gone alright? What have you changed to make it work in the cloud using Elasticbeanstalk?
>
>

---

### ❓ Question 5: Explain all the steps that you have followed after changing the web application code to have the web application updates running in the cloud.
> After implementing the search functionality (Task 6.3) in our web application, we followed these steps to deploy the updates to AWS Elastic Beanstalk:
>
> **Step 1: Test Locally**
> - First, we tested all changes locally using `python manage.py runserver`
> - Verified the search functionality works at `http://127.0.0.1:8000/search`
> - Confirmed the new menu item appears in the navigation bar
> - Tested different search scenarios (domain filter, preview filter, and no filters)
>
> **Step 2: Rebuild Docker Image with New Version**
> ```bash
> # Build new Docker image with updated code
> docker build -t django-docker:v1.0.2 .
> 
> # Tag the image for AWS ECR
> docker tag django-docker:v1.0.2 <aws-registry-id>.dkr.ecr.us-east-1.amazonaws.com/django-webapp-docker-repo:v1.0.2
> ```
>
> **Step 3: Authenticate with AWS ECR**
> ```bash
> # Get login password and authenticate Docker with ECR
> aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws-registry-id>.dkr.ecr.us-east-1.amazonaws.com
> ```
>
> **Step 4: Push New Image to AWS ECR**
> ```bash
> # Push the new version to ECR repository
> docker push <aws-registry-id>.dkr.ecr.us-east-1.amazonaws.com/django-webapp-docker-repo:v1.0.2
> 
> # Verify the image was uploaded
> aws ecr list-images --repository-name django-webapp-docker-repo
> ```
>
> **Step 5: Update Dockerrun.aws.json**
> - Navigate to `.housekeeping/elasticbeanstalk/` directory
> - Update `Dockerrun.aws.json` to reference the new image version:
> ```json
> {
>   "AWSEBDockerrunVersion": "1",
>   "Image": {
>     "Name": "<aws-registry-id>.dkr.ecr.us-east-1.amazonaws.com/django-webapp-docker-repo:v1.0.2"
>   },
>   "Ports": [
>     {
>       "ContainerPort": 8000
>     }
>   ]
> }
> ```
>
> **Step 6: Initialize and Create Elastic Beanstalk Environment**
> 
> If this is your first deployment, you need to initialize and create the EB environment:
> 
> ```bash
> cd .housekeeping/elasticbeanstalk
> 
> # Initialize Elastic Beanstalk application
> eb init --region us-east-1 -i django-webapp-eb
> # Select: Docker -> Docker running on 64bit Amazon Linux 2023 -> SSH: yes -> Select keypair
> 
> # Generate the create command using the Python script
> python ../scripts/ebcreate.py ../../aws.env team20
> 
> # Copy and run the output command (it will be very long)
> # Example: eb create team20 --min-instances 1 --max-instances 3 ...
> ```
> 
> If the environment already exists, use these commands instead:
> 
> ```bash
> cd .housekeeping/elasticbeanstalk
> 
> # List existing environments
> eb list
> 
> # Select your environment
> eb use team20
> 
> # Deploy the new version
> eb deploy
> ```
> 
> **Important Notes:**
> - The first `eb create` takes 5-15 minutes to provision all AWS resources
> - Subsequent deployments with `eb deploy` are much faster (2-5 minutes)
> - Make sure your IAM user has `AdministratorAccess-AWSElasticBeanstalk` policy
> - Ensure the `AmazonEC2ContainerRegistryReadOnly` and `AWSElasticBeanstalk` policies
>
> **Step 7: Monitor Deployment**
> - Watch the deployment progress in terminal
> - Check AWS Elastic Beanstalk console for health status
> - Wait for environment health to return to "Ok" (green)
> ```bash
> eb status  # Check deployment status
> eb health  # Monitor instance health
> ```
>
> **Step 8: Verify Deployment**
> ```bash
> # Open the web application in browser
> eb open
> ```
> - Test the search functionality at `/search`
> - Verify the Admin search menu item appears
> - Test filtering by domain and preview options
> - Check that data from DynamoDB is retrieved correctly
>

---

### ❓ Question 6: Draw a diagram of the current deployment of the web app using a tool such as Draw.io
>
>

---

### ❓ Question 7: Assess the current version of the web application against each of the twelve factor application.
>
>

---

## Wrap Up:
### ❓ Question 8: How long have you been working on this session? What have been the main difficulties that you have faced and how have you solved them? Add your answers to README.md.
>
>

---

### ❓ Question 9: Using the AWS Billing and Cost Management Service, access the "Cost Explorer" and capture the cost of last week Using the "Dimension" "Service" where you can see how much did you spend to complete the session in total and per service.
>
>

