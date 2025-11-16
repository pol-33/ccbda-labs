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
![S3 Uploaded Static Files](images/q3-console.png)

![S3 Files in the AWS Console](images/q3-aws-console.png)

![CloudFront Distribution](images/q3-cdn.png)

---

## Task 6.3: Create a new option to retrieve the list of leads
### ❓ Question 4: Has everything gone alright? What have you changed to make it work in the cloud using Elasticbeanstalk?
>
>

---

### ❓ Question 5: Explain all the steps that you have followed after changing the web application code to have the web application updates running in the cloud.
>
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

