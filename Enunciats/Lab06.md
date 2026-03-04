# Lab Session #6: Improving the environment of a web app running in the cloud

This lab session builds upon the work from the previous sessions. Make sure that you have available and working
everything done in the previous sessions.

As the number of instances fluctuates with creation and termination, it’s essential to track the web application’s
activity by securely storing log files for monitoring and future analysis.

Finally, we’ll reduce the load on the web application server by distributing static assets (such as images, CSS, and
JavaScript) to edge locations closer to the visitors, improving response times and overall performance.

### AWS S3

AWS Simple Storage Service (AWS S3) is an object storage service renowned for its industry-leading scalability, data
availability, security, and performance. Millions of customers across various industries rely on S3 to store, manage,
analyze, and protect vast amounts of data for a wide range of use cases, including data lakes, cloud-native
applications, and mobile apps. With its cost-effective storage classes and intuitive management features, S3 enables
customers to optimize costs, efficiently organize and analyze data, and configure precise access controls to meet
specific business and compliance needs.

### AWS CloudFront CDN

A content delivery network or content distribution network (CDN) is a geographically distributed network of proxy
servers that disseminate a service spatially, as close to end-users as possible, to provide high availability, low
latency, and high performance.

<img alt="Lab05-CDN.png" src="images/Lab05-CDN.png" width="50%"/>

The information that flows every day on the Internet can be classified as "static" and "dynamic" content. The "dynamic"
part is the one that changes depending on the user's input. It is distributed by, for instance, PaaS servers with load
balancers. The "static" part does not change based on the user's input, and it can be moved as close to the end user as
possible to improve the "user experience".

Nowadays, CDNs serve a substantial portion of the "static" content of the Internet: text, graphics, scripts,
downloadable media files (documents, software products, videos, etc.), live streaming media, on-demand streaming media,
social networks and so much more.

Content owners pay CDN operators to deliver the content that they produce to their end users. In turn, a CDN pays ISPs (
Internet Service Providers), carriers, and network operators for hosting its servers in their data centers.

**AWS CloudFront CDN** is a global CDN service that securely delivers static content with low latency and high transfer
speeds. CloudFront CDN works seamlessly with other AWS services including **AWS Shield** for DDoS mitigation,
**AWS S3**, **Elastic Load Balancing** or **AWS EC2** as origins for your applications, and **AWS Lambda** to run
custom code close to final viewers.

### AWS Secrets Manager

**AWS Secrets Manager** is a cloud service that helps managing, retrieving, and rotating database credentials, API
keys, OAuth tokens, and other secrets throughout their lifecycles. It is designed to secure access to the user's
applications,
services, and IT resources, eliminating the need to hard-code sensitive information in the application source code.

Key Features and Benefits:

- **Secure Storage and Encryption**: Secrets are encrypted at rest using AWS Key Management Service (KMS) keys and
  securely transmitted over TLS when retrieved.
- **Automatic Rotation**: You can configure an automatic rotation schedule for secrets, replacing long-term credentials
  with short-term ones without impacting applications. This significantly reduces the risk of compromise.
- **Programmatic Retrieval**: Applications can retrieve secrets dynamically at runtime using Secrets Manager APIs and
  SDKs, rather than storing them in configuration files.
- **Fine-grained Access Control**: Access to secrets is managed using AWS Identity and Access Management (IAM) policies,
  allowing administrators to define who can access specific secrets under what conditions.
- **Auditing and Monitoring**: Secrets Manager integrates with AWS logging and monitoring services like AWS CloudTrail
  and Amazon CloudWatch, providing an audit trail of when a secret was accessed or modified.
- **Multi-Region Replication**: Secrets can be automatically replicated to multiple AWS Regions to support multi-region
  applications and disaster recovery scenarios.

# Tasks for Lab session #6

* [**Task 6.1: Centralize the logs of your application instances**](#Task61)
* [**Task 6.2: Deliver static content using a Content Delivery Network**](#Task62)
* [**Task 6.3: Create a new option to retrieve the list of leads**](#Task63)
* [**Task 6.4: Manage the configuration parameters in a more secure way**](#Task64)

<a id="Task61" />

## Task 6.1: Centralize the logs of your application instances

Centralized logging plays a critical role in ensuring the reliability, performance, security, and scalability of web
applications. It makes monitoring, debugging, and analysis much easier, while also providing key insights into the
behavior of your application and users.

To centralize the logs of your application instances, you can use a cloud-based service like AWS S3, which offers
durable and scalable object storage. Here’s how you can implement this:

1. **Choose a Logging Solution**: Use a logging framework (like Logback, Log4j, or Winston) in your application to
   output logs in a structured format (e.g., JSON, plain text, or XML). Ensure your logs are stored in a centralized
   location, so all application instances can send logs to a common destination.

2. **Configure Cloud Storage (e.g., Amazon S3)**: Set up an S3 bucket to store the logs. You can create a dedicated S3
   bucket for logs.

3. **Use Cloud Storage SDK or API**: Use the AWS SDK (boto3) or AWS CLI to upload logs from your application instances
   to the S3 bucket. Set up a script or logic in your application to upload logs periodically or after each log event.

4. **Implement Log Rotation and Retention Policies**: S3 supports lifecycle policies to automatically archive, delete,
   or transition older log files to cheaper storage classes (like S3 Glacier). Configure the retention policy to manage
   the logs effectively, especially when handling large volumes of logs.

5. **Monitor and Analyze Logs**: Once logs are stored in S3, you can integrate with services like AWS CloudWatch Logs or
   use third-party log analysis tools (e.g., ELK Stack, Splunk, or Datadog) for searching and analyzing logs in
   real-time.

### Log management in Django

The [Django framework utilizes and extends Python's built-in logging module](https://docs.djangoproject.com/en/5.1/topics/logging/)
to handle system logging.

The code below needs to be included into the `settings.py` file. It defines two formats for the log lines named verbose
and simple, as shown below. In the verbose log format we include the instance name and the module, file and line that
outputs the message.

```text
2026-03-21 19:42:31,740 ERROR [localhost] [home:views:9] This is an error log message
2026-03-21 19:42:31,741 INFO [localhost] [home:views:10] This is an information log message
2026-03-21 19:42:31,741 WARNING [localhost] [home:views:10] This is a warning log message
```

```text
2026-03-21 19:42:31,740 ERROR This is an error log message
2026-03-21 19:42:31,741 INFO This is an information log message
2026-03-21 19:42:31,741 WARNING This is a warning log message
```

```python
AWS_EC2_INSTANCE_ID = get_metadata('instance-id', '--instance-id--')

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} [" + AWS_EC2_INSTANCE_ID + "] [{module}:{funcName}:{lineno}] {message}",
            "style": "{",
        },
        "simple": {
            "format": "{asctime} {levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "INFO",
            "formatter": "verbose",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "file.log"),
            "maxBytes": 5 * 1024,  # 5 K
            "backupCount": 1,
            "encoding": None,
            "delay": 0,
        },
        "s3": {
            "level": "INFO",
            "formatter": "verbose",
            "class": "ccbda.S3RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "s3.log"),
            "maxBytes": 5 * 1024,  # 5 K
            "backupCount": 1,
            "encoding": None,
            "delay": 0,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file", "s3"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
```

See the different variables that can be used in the log formatting.

```python
# Fetch specific metadata fields
#     %(name)s            Name of the logger (logging channel)
#     %(levelno)s         Numeric logging level for the message (DEBUG, INFO, WARNING, ERROR, CRITICAL)
#     %(levelname)s       Text logging level for the message ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
#     %(pathname)s        Full pathname of the source file where the logging call was issued (if available)
#     %(filename)s        Filename portion of pathname
#     %(module)s          Module (name portion of filename)
#     %(lineno)d          Source line number where the logging call was issued (if available)
#     %(funcName)s        Function name
#     %(created)f         Time when the LogRecord was created (time.time() return value)
#     %(asctime)s         Textual time when the LogRecord was created
#     %(msecs)d           Millisecond portion of the creation time
#     %(relativeCreated)d Time in milliseconds when the LogRecord was created, relative to the time the logging module was loaded (typically at application startup time)
#     %(thread)d          Thread ID (if available)
#     %(threadName)s      Thread name (if available)
#     %(process)d         Process ID (if available)
#     %(message)s         The result of record.getMessage(), computed just as the record is emitted
```

You have probably noticed the variable named `AWS_EC2_INSTANCE_ID` that is used inside the log formatting. It will
contain the AWS EC2 instance number that is used to run the code. To be able to analyze what is happening, it is very
important to distinguish what instance is producing every log line, as well as when. We can use the function
`get_metadata()` to obtain the EC2 instance ID.

In the handlers section we have three outputs for the messages: console, file and s3. We not only define the log file
path but also the maximum number or bytes before the [file is rotated](https://en.wikipedia.org/wiki/Log_rotation).

### Log rotation in Django

Finally, the configuration states that administrative logs will only be sent to the console while the django application
will output its content simultaneously to the console, a local rotated log file and an AWS S3 bucket.

**Log rollover** is the process of starting a new log file when the current one reaches a certain size or age. This
helps manage log file sizes, preventing them from growing too large and making them easier to organize and analyze.

We can include the `ccbda.S3RotatingFileHandler` class (see the logs configuration) in the `ccbda/__init__.py` file.
When the class is first instantiated, as the web application starts, it creates a connection to the S3 bucket that will
be used in the log rotate operation.

The function `emit` is invoked everytime a function like `logging.info(f'ROLLOVER {record.name}')` is called.

The function `doRollover` receives two full file path names. It renames the source file, which contains the full log,
and sends the contents to AWS S3 with a **unique name** that is built using the original source file name and the
current timestamp.

```python

import logging.handlers
import boto3
import os
from botocore.exceptions import ClientError
from django.conf import settings
import pathlib
from datetime import datetime, timezone


class S3RotatingFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, filename, maxBytes=0, backupCount=0, encoding=None, delay=0):
        super().__init__(
            filename=filename, maxBytes=maxBytes, backupCount=backupCount, encoding=encoding, delay=delay
        )
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket_name = settings.AWS_S3_BUCKET_NAME
        self.logs_prefix = settings.AWS_S3_LOGS_PREFIX
        if not self.logs_prefix.endswith("/"):
            self.logs_prefix += "/"

    def rotate(self, source, dest):
        if callable(self.rotator):
            self.rotator(source, dest)
        else:
            stem = pathlib.Path(source).stem
            suffix = pathlib.Path(source).suffix
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
            s3_key = f'{self.logs_prefix}{stem}.{now}{suffix}'

            if os.path.exists(source):
                os.rename(source, dest)
                if os.stat(dest).st_size > 0:
                    self.s3_client.upload_file(dest, self.bucket_name, s3_key)
                os.remove(dest)

    def emit(self, record):
        try:
            log_data = self.format(record)
            try:
                if self.shouldRollover(record):
                    logging.info(f'ROLLOVER {record.name}')
                    self.doRollover()
                self.stream.write(log_data + self.terminator)
            except Exception as err:
                self.handleError(record)
        except ClientError as e:
            logging.error(f"Error sending log to S3: {e}")

```

You need to add two additional variables to the web application environment which need to be also included inside of
settings.py. Make sure that the directory specified in `AWS_S3_LOGS_PREFIX` and the bucket specified in
`AWS_S3_BUCKET_NAME` do exist before running the web application.

```text
AWS_S3_BUCKET_NAME=team<YOUR-TEAM-NUMBER>.ccbda.upc.edu
AWS_S3_LOGS_PREFIX=logs/
```

> :question: **Question 1**: What issues have you met when following the above instructions?

Use additional `logging.error()` or `logging.info()` inside of the web application to provide logging feedback of what
is happening.

> :question: **Question 2**: Run the web application locally and play with the log size of the s3 handler and see how
> the bucket keeps receiving log files. Share your thoughts. When you run the web application can you see the logs where
> you expected?

<a id="Task62" />

## Task 6.2: Deliver static content using a Content Delivery Network

### The static content in our web app

If you check line 11 of the file *templates/generic.html* you will see that, instead of loading in our server
Bootstrap CSS, we are already using a CDN to retrieve the CSS and send it to the final users. Bootstrap uses
*maxcdn.bootstrapcdn.com* as their CDN distribution point.

```html

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet"
      crossorigin="anonymous">
```

We can now add our CSS code to customize the look and feel of our web app even more. In that same file, add the
following line just before closing the **head** HTML tag:

```html

<link href="{% static 'custom.css' %}" rel="stylesheet"></head>
```

If you check the contents of the file *static/custom.css* you will see that it includes some images, also available in
the same folder. If you save the modifications to *form/templates/generic.html* and review your web
app locally, http://127.0.0.1:8080, you will see that it appears slightly different.

> [!Caution]
> Verify that your `settings.py` file contains the following two variables instantiation
> ```
> STATIC_URL = 'static/'
> STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
> ```

### Upload your static content to AWS S3 and grant object permissions

All the distributed static content overloads our server with requests. Moving it to a CDN will reduce our server's load
and, at the same time, the visitors will experience a much lower latency while using our web app. We only have few
static files
in this app, but a typical web app distributes hundreds of pieces of static content.

To configure our CDN, we are going to follow the steps
at ["Getting Started with CloudFront"](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GettingStarted.html).
Check that document if you need extra details.

Create a new bucket in `eu-south-2` region to deposit the web app static content. Let us name this bucket *
*ccbda-webapp-YOUR-ID** (YOUR-ID can be your AWS account number or any other distinctive string because you
will not be allowed to create two buckets with the same name, regardless the owner).

You can also use AWS CLI to sync the contents of your static folder with that
bucket. [Synchronize with your S3 bucket](https://docs.aws.amazon.com/cli/latest/reference/s3/sync.html) using the
following command:

```bash
_$ aws s3 sync ./static s3://ccbda-webapp-YOUR-ID
upload: ./static/custom.css to s3://ccbda-webapp-YOUR-ID/custom.css
upload: ./static/CCBDA-Square.png to s3://ccbda-webapp-YOUR-ID/CCBDA-Square.png
upload: ./static/startup-bg.png to s3://ccbda-webapp-YOUR-ID/startup-bg.png
```

### Create a CloudFront CDN Web Distribution

Following the steps
at ["Getting Started with CloudFront"](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GettingStarted.html)
we end up having to wait until the files are distributed. It takes five minutes or more, be patient. Once the first
distribution is set up, whenever you resync your static contents it will take much less.

 <img src="./images/Lab05-10.png " alt="CloudFront CDN distribution" title="CloudFront CDN distribution"/>

> [!Caution]
> Use the same region for the bucket and the CloudFront distribution. 
> Otherwise, you will not be able to make it work.

### Change the code and test your links

The HTML code of our web app has only one direct access to a static file; the images referenced (using a relative route)
through the CSS stylesheet. We just need to change *form/templates/generic.html* and our web app is now retrieving all
static content from our CDN distribution.

Consider that we are now borrowing a CloudFront URL (<RANDOM-ID-FROM-CLOUDFRONT>.cloudfront.net) but usually, in the
setup, we will use a URL from our domain, something like *static.mydomain.com* to map the CDN distribution.

```html

<link href="//<RANDOM-ID-FROM-CLOUDFRONT>.cloudfront.net/custom.css" rel="stylesheet">
```

> :question: **Question 3**: Take a couple of screenshots of you S3 and CloudFront consoles to demonstrate that
> everything worked all right.

Commit the changes on your web app, deploy them on Docker and check that it also works fine from there: **use
Google Chrome and check the origin of the files that you are loading**:

 <img src="./images/Lab06-cdn.png " alt="Files loaded" title="Files loaded" width="40%" />

### Django support for CDN

Having to go through the code of a web app to locate all the static files is a not only tedious task but also prone to
errors. Since Django Framework distinguishes the static content from the dynamic content, it supports the smooth
integration of a CDN to distribute it. Try configuring this feature if you are curious and have time.

First of all, you need to add the following package to your environment:

```bash
(venv)_$ pip install django-storages
```

Then modify `ccbda-webapp\ccbda-webapp\settings.py` by adding 'storages' as an installed
application and tell Django to use the new storage schema as well as the name of your bucket and the name of the
CloudFront domain.

```python
INSTALLED_APPS = [
    ...
    'storages',
    ...
]

...

CLOUD_FRONT = os.environ.get("CLOUD_FRONT", default='False') == 'True'

if CLOUD_FRONT:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_STORAGE_BUCKET_NAME = 'ccbda-webapp-YOUR-ID'
    AWS_S3_CUSTOM_DOMAIN = '<RANDOM-ID-FROM-CLOUDFRONT>.cloudfront.net'
else:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
```

Having done that you should be able to keep all static files declared the way Django expects to and, at the same time,
access them using a CDN.

```html

<link href="{% static 'custom.css' %}" rel="stylesheet"></head>
```

This should be the last step on the deployment of the web app and you can activate it only if the variable DEBUG is set
to False.

Django can also assume the synchronization of the static files to the CDN by means of the maintenace command
`python manage.py collectstatic`.

<a id="Task63" />

## Task 6.3: Create a new option to retrieve the list of leads

Edit the file *form/urls.py* to add the new URL and associate it to the new view *search*.

```python
urlpatterns = [
    # ex: /
    path('', views.home, name='home'),
    # ex: /signup
    path('signup', views.signup, name='signup'),
    # ex: /search
    path('search', views.search, name='search'),
]
```

To create the controller for the new view edit *form/views.py* and include the following code:

```python
from collections import Counter


def search(request):
    domain = request.GET.get('domain')
    preview = request.GET.get('preview')
    leads = Leads()
    items = leads.get_leads(domain, preview)
    if domain or preview:
        return render(request, 'search.html', {'items': items})
    else:
        domain_count = Counter()
        domain_count.update([item['email'].split('@')[1] for item in items])
        return render(request, 'search.html', {'domains': sorted(domain_count.items())})
```

The search view gets two parameters:

- preview: (*values are Yes/No*) lists the leads that are interested, or not, in a preview.
- domain: (*value is the part right after the @ of an e-mail address*) will list only the leads from that domain.

Reading the code, we understand that the search view retrieves the value of the parameters, gets the complete list of
leads and then:

- if any parameter is set, the program just lists all the records matching the search.
- if both parameters are empty the program extracts the domain from each e-mail address and counts how many addresses
  belong to each domain.

To access the records stored at the NoSQL table *ccbda-signup-table* you need to add a method *get_leads* to the model
*Leads()* file *form/models.py*.
The [Scan](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_Scan.html) operation allows us to filter
values from the table.

```python
def get_leads(self, domain, preview):
    try:
        dynamodb = boto3.resource('dynamodb',
                                  region_name=AWS_REGION,
                                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        table = dynamodb.Table('ccbda-signup-table')
    except Exception as e:
        logger.error(
            'Error connecting to database table: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
        return None
    expression_attribute_values = {}
    FilterExpression = []
    if preview:
        expression_attribute_values[':p'] = preview
        FilterExpression.append('preview = :p')
    if domain:
        expression_attribute_values[':d'] = '@' + domain
        FilterExpression.append('contains(email, :d)')
    if expression_attribute_values and FilterExpression:
        response = table.scan(
            FilterExpression=' and '.join(FilterExpression),
            ExpressionAttributeValues=expression_attribute_values,
        )
    else:
        response = table.scan(
            ReturnConsumedCapacity='TOTAL',
        )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return response['Items']
    logger.error('Unknown error retrieving items from database.')
    return None
```

*form/templates/search.html* receives the data from the view controller and creates the HTML to show the results.

Save the changes and, before committing them, check that everything works fine by typing *http://127.0.0.1:8080/search*
in your browser.

<img src="./images/Lab05-6.fw.png " alt="Search" title="Search"/>

To add the new option to the menu bar, simply edit the file *form/templates/generic.html*, go to line 28 and add the
second navbar as shown below. Save the file and, with no further delay, check that you have it added in the version that
runs in your computer.

```html

<div class="collapse navbar-collapse" id="navbarResponsive">
    <ul class="navbar-nav">
        <li class="nav-item active">
            <a class="nav-link active" href="{% url 'form:home' %}">Home</a>
        </li>
        <li class="nav-item">
            <a class="nav-link" href="#">About</a>
        </li>
        <li class="nav-item">
            <a class="nav-link" href="#">Blog</a>
        </li>
        <li class="nav-item">
            <a class="nav-link" href="#">Press</a>
        </li>
    </ul>
    <ul class="nav navbar-nav ml-auto">
        <li class="nav-item">
            <a class="nav-link" href="{% url 'form:search' %}">Admin search</a>
        </li>
    </ul>
</div>
```

<img src="./images/Lab05-7.png " alt="Search" title="Search"/>

If the web app works correctly in your computer commit the changes and deploy the new version in the cloud. Change
whatever is necessary to make it work.

> :question: **Question 4**: Has everything gone alright? What have you changed to make it work in the cloud using
> Elasticbeanstalk?

> :question: **Question 5**: Explain all the steps that you have followed after changing the web application code to
> have the web application updates running in the cloud.

> :question: **Question 6**: Draw a diagram of the current deployment of the web app using a tool such
> as [Draw.io](https://www.drawio.com/blog/aws-diagrams)

> :question: **Question 7**: Assess the current version of the web application against each of the twelve factor
> application.

<a id="Task64" />

## Task 6.4: Manage the configuration parameters in a more secure way

The first step is to allow the current AWS user to access the AWS Secret Manager. To do so, go to the IAM console and
add the *SecretsManagerReadWrite* policy to the user.

Verify that it all works correctly by adding a new secret and retrieving its value.

```bash
_$ aws secretsmanager list-secrets
{
    "SecretList": []
}
_$ aws secretsmanager create-secret --name DJANGO_DEBUG --secret-string False
{
    "ARN": "arn:aws:secretsmanager:eu-south-2:<YOUR-AWS-ACCOUNT-ID>:secret:DJANGO_DEBUG-X7ohmy",
    "Name": "DJANGO_DEBUG",
    "VersionId": "709a02bd-82d3-4bef-8561-192801dcb1b5"
}
_$ aws secretsmanager list-secrets                                           
{
    "SecretList": [
        {
            "ARN": "arn:aws:secretsmanager:eu-south-2:<YOUR-AWS-ACCOUNT-ID>:secret:DJANGO_DEBUG-X7ohmy",
            "Name": "DJANGO_DEBUG",
            "LastChangedDate": "2025-11-18T19:24:38.768000+01:00",
            "SecretVersionsToStages": {
                "709a02bd-82d3-4bef-8561-192801dcb1b5": [
                    "AWSCURRENT"
                ]
            }
        }
    ]
}
_$  django-webapp-2026_1 % aws secretsmanager get-secret-value --secret-id "arn:aws:secretsmanager:eu-south-2:<YOUR-AWS-ACCOUNT-ID>:secret:DJANGO_DEBUG-X7ohmy"
{
    "ARN": "arn:aws:secretsmanager:eu-south-2:<YOUR-AWS-ACCOUNT-ID>:secret:DJANGO_DEBUG-X7ohmy",
    "Name": "DJANGO_DEBUG",
    "VersionId": "709a02bd-82d3-4bef-8561-192801dcb1b5",
    "SecretString": "False",
    "VersionStages": [
        "AWSCURRENT"
    ],
    "CreatedDate": "2025-11-18T19:24:38.762000+01:00"
}
```

```bash
_$ pip install aws-secretsmanager-caching
```


> :question: **Question 8**: What is the contents of the `aws-elasticbeanstalk-ec2-role`? 
> Include the JSON code of each of the policies attached to that role and **briefly explain** what they do.

## How to submit this assignment:

> :question: **Question 9**: How long have you been working on this session? What have been the main
> difficulties faced and how you have solved them? Add your answers to `README.md`.

> :question: **Question 10**: Using the AWS Billing and Cost Management Service, access the "Cost Explorer" and capture
> the cost of last week Using the "Dimension" "Service" where you can see how much you did spend to complete the session
> in total and per service.

Make sure that you have updated your local GitHub repository (using the git commands add, commit, and push) with all the
files generated during this session.

Before the deadline, all team members shall push their responses to their
private https://github.com/CCBDA-UPC/2025_1-6-xx repository.

Add all the web application files to your repository and comment what you think is relevant in your session's
*README.md*.


