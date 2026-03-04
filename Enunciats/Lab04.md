# Lab Session #4: Deployment of a custom web app using additional cloud services

In this laboratory session, we are going to assume that you are working on a new subject on Cloud Computing that isn't 
ready for students to enroll yet. In the meantime, you plan to deploy a small placeholder app that collects contact 
information from the website visitors who sign up to hear more. The signup app will help you reach potential students 
who might take part in a private beta test of the laboratory sessions.

### The Signup App

The app will allow your future students to submit contact information and express interest in a preview of the new
subject on Cloud Computing that you're developing.

To make the app look good, we use [Bootstrap](https://getbootstrap.com/), a mobile-first front-end framework that
started as a Twitter project.

#### Django: web framework

[Django](https://www.djangoproject.com/start/) is a high-level Python web framework designed for rapid development and
clean, pragmatic design. Built by experienced developers, it handles many complexities of web development, allowing you
to focus on building your application without reinventing the wheel. Plus, it’s free and open source.

### AWS DynamoDB

**Amazon DynamoDB**, a NoSQL database service, is going to be used to store the contact information that users submit.

DynamoDB is a schema-less database, so you need to specify only a primary key attribute. Let us use the email field as a
key for each register.

### AWS Simple Notification Service (SNS)

We want to know when customers submit a form, therefore we are going to use **AWS Simple Notification Service** (AWS
SNS), a message pushing service that can deliver notifications over various protocols. For our web app, we are going to
push notifications to an email address.

### Docker

[Docker](https://www.docker.com/) is a **Platform as a Service (PaaS)** solution that leverages OS-level virtualization
to package software into
units known as **containers**. These containers ensure that applications can run consistently and efficiently across
various environments. Docker provides both free and premium options and operates through its core software, Docker
Engine, which has been maintained by Docker, Inc. since its initial release in 2013.

The primary purpose of Docker is to streamline the deployment process by isolating applications in lightweight
containers, enabling smooth operation in diverse environments.

# Pre-lab homework

Make sure that you install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
and [Docker Compose](https://docs.docker.com/compose/) on your machine.

If you need help with the installation, you can find detailed instructions on the Docker and Django websites.

Create a new **programmatic user** named **lab_webapp_user** that will have access to the AWS DynamoDB and AWS Simple Notification Service and any additional assets necessary to execute this lab session. The user will only be used inside the application.

> [!Important]
> Don't forget to use the *"principle of least privilege"* when creating and managing the programmatic user.

### Updating the AWS Credentials

Have **AWS Command Line Interface ([AWS CLI](https://aws.amazon.com/cli/))** installed and configured with the current
value of your AWS credentials.

Check the instructions
for [installing or updating to the latest version of the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) depending on the operating system of your laptop.

You can save your frequently used configuration settings and credentials in files that are maintained by the AWS CLI.

The files are divided into profiles. By default, the AWS CLI uses the settings found in the profile named **default**.
To use alternate settings, you can create and reference additional profiles.

Let's create the configuration files: `aws configure` asks you for the value of the different parameters that you've
obtained from the "lab_webapp_user".


```bash
_$ aws configure
AWS Access Key ID [None]: <YOUR-AWS-ACCESS-KEY-ID>
AWS Secret Access Key [None]: <YOUR-AWS-SECRET-ACCESS-KEY>
Default region name [None]: eu-south-2
Default output format [None]: json
_$ cat $HOME/.aws/config
[default]
region = eu-south-2
output = json
_$ cat $HOME/.aws/credentials
[default]
aws_access_key_id = <YOUR-AWS-ACCESS-KEY-ID>
aws_secret_access_key = <YOUR-AWS-SECRET-ACCESS-KEY>
```
As you can see above, the entered values end up in two different files in order to enable the separation of credentials from less sensitive configuration information.
- The *credentials* file is intended for storing just credential information for the configured profiles. (Currently limited to: aws_access_key_id, and aws_secret_access_key)
- The *config* file is intended for storing non-sensitive configuration options for the configured profiles.
- The *config* file can also be configured to contain any information which could also be stored in the credentials file.
- In the case of conflicting credential information being specified for a profile in the config and credentials file, those in the credentials file will take precedence.

Bear in mind that the AWS CLI commands obtain their **default values** (i.e. region), **credentials**, and access rights, from `$HOME/.aws/config` and `$HOME/.aws/credentials`. Such credentials must have the permissions necessary to run the commands. I.e. if the user has no access to AWS S3,  `aws s3 ls` will not work. If you see something like the error below, please go to your console and verify the permissions of the user associated to the credentials utilized

```
_$  aws s3 ls
An error occurred (AccessDenied) when calling the ListBuckets operation: User: arn:aws:iam::<AWS-USER-ACCOUNT-ID>:user/lab_webapp_user is not authorized to perform: s3:ListAllMyBuckets because no identity-based policy allows the s3:ListAllMyBuckets action
```

# Tasks for Lab session #4

* [Task 4.1: Create a DynamoDB Table](#Task41)
* [Task 4.2: Download the code for the Web App](#Task42)
* [Task 4.3: Test the web app locally](#Task43)
* [Task 4.4: Use AWS Simple Notification Service in your web app](#Task44)
* [Task 4.5: Configure Docker](#Task45)
* [Task 4.6: Deploy the target web app](#Task46)
* [Task 4.7: Analisys of the twelve-factor app methodology](#Task47)

<a id="Task41"/>

## Task 4.1: Create a DynamoDB Table

The signup app uses a DynamoDB table to store the contact information that users submit.

1. Go to your AWS console and, at the console search for "DynamoDB".

3. Go to Tables and **Create table**.

4. For Table name, type **ccbda-signup-table**.

5. For the `Partition key`, type `email`. Choose **Create**.

Now verify that the table is created by using AWS CLI. If the table does not appear verify that you are querying the same AWS Region where the table is created. Regarding the above configuration, the default AWS Region is eu-south-2.

```
_$  aws dynamodb list-tables
{
    "TableNames": [
        "ccbda-signup-table"
    ]
}
```

You can always add a parameter `--region` to supersede the default region by a particular region.

```
_$ aws dynamodb list-tables --region us-east-1
{
    "TableNames": []
}

```

<a id="Task42"/>

## Task 4.2: Download the code for the Web App

You are going to make a few changes to the base Python code. Therefore, download
the [repository](https://github.com/CCBDA-UPC/django-webapp) on your local disk drive
as a **zip file**.

<img alt="Lab04-webapp-zip.png" src="images/Lab04-webapp-zip.png" width="50%"/>

Unzip the file inside your responses repository for the current Lab session, and change the name of the folder to
**django-webapp**.

<a id="Task43"/>

## Task 4.3: Test the web app locally

### Configuration of the web application

Inside of the django-webapp folder, create a `.env` file with the configuration for the project.

```bash
_$ cat .env
DJANGO_DEBUG="True"
DJANGO_ALLOWED_HOSTS="localhost:127.0.0.1:0.0.0.0"
DJANGO_SECRET_KEY="-lm+)b44uap8!0-^1w9&2zokys(47)8u698=dy0mb&6@4ee-hh"
DJANGO_LOGLEVEL="INFO"
CCBDA_SIGNUP_TABLE="ccbda-signup-table"
AWS_REGION="eu-south-2"
AWS_DEFAULT_REGION=AWS_REGION
AWS_ACCESS_KEY_ID="<YOUR-AWS-ACCESS-KEY-ID>"
AWS_SECRET_ACCESS_KEY="<YOUR-AWS-SECRET-ACCESS-KEY>"
```

Bear in mind that the web application obtains its credentials, and access rights, from the `.env` file setting the correct values to `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. Such credentials must have the permissions necessary to run the Python code while accesing the different AWS Services. 

Open the .gitignore file and check that it contains rules to avoid pushing to the repository files such as `.env`
containing sensitive information. **Make sure to have such functionality present in your future projects**.

> [!Caution]
> Any git repo containing credentials will automatically be evaluated with a zero, and there is no exception to this. Beware that the git repo contains the values of the credentials even if you make the mistake and then delete the .env file. Hackers (and anybody else) may access any git repo history. Configure your **.gitignore** to prevent that from happening.

### Web application Virtual environment

Next, create a **new Python 3.13 virtual environment** specially for this web app and install the packages required to
run it. The new Python virtual environment is created locally only to keep the packages that the web app uses. Having a
small Python environment implies a faster web app startup avoiding, as much as possible, any hidden dependencies and
ambiguities.

Check the contents of the file **requirements.txt** that the web application declares as the set of Python packages, and
its version, that it requires to be executed successfully.

In particular, the package `boto3` is a library that hides de AWS REST API to the programmer and manages the
communication between the web app and all the AWS services. Check [**Boto 3 Documentation
**](https://boto3.readthedocs.io/en/latest/reference/services/index.html) for more details.

Please, note the different prompt  `(.env)_$`  vs. `_$` when you are inside or outside the Python virtual
environment.

```
_$ virtualenv -p python3 ../.venv
_$ source ../.venv/bin/activate
(.venv)_$ python --version
Python 3.13.2
(.venv)_$ pip install -r requirements.txt
```

If necessary you can exit the virtual environment:

```bash
(.venv)_$ deactivate
_$ 
```

### Web application running locally for testing and debugging

You will now need to run a local testing server. But just before we need to initialize the Django database (you'll find more about that step later in this session).

```
(.venv)_$ python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK
(.venv)_$ python manage.py runserver
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
January 08, 2025 - 19:36:44
Django version 5.1.7, using settings 'ccbda.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

You can also create a PyCharm configuration tu run or debug the code.

<img src="./images/Lab04-pycharm-config.png" alt="AWS service" title="AWS service" width="80%"/>

Once the web app is running, check that you have configured the access to DynamoDB correctly by interacting with the web
app through your browser [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

Go to the DynamoDB table browser tab and verify that the **ccbda-signup-table** table contains the new records that the
web app should have created. If all the above works correctly, you are almost ready to transfer the web app to Docker.

```
(.venv)_$ aws dynamodb scan --table-name ccbda-signup-table
{
    "Items": [
        {
            "email": {
                "S": "angel.toribio@upc.edu"
            },
            "name": {
                "S": "Angel Toribio"
            },
            "preview": {
                "S": "Yes"
            }
        }
    ],
    "Count": 1,
    "ScannedCount": 1,
    "ConsumedCapacity": null
}

```

> :question: **Question 1**: After filling the web application form a few times, what is the result of the command just above this question?. Add your thoughts on the above tasks.

<a id="Task44" />

## Task 4.4: Use AWS Simple Notification Service in your web app

### Create a AWS SNS Topic

Our signup web app wants to notify you each time a user signs up. When the data from the signup form is written to the
DynamoDB table, the app will send you an AWS SNS notification.

First, you need to create an AWS SNS topic, which is a stream for notifications, and then you need to create a
subscription that tells AWS SNS where and how to send the notifications.

**To set up AWS SNS notifications**

At the "AWS" console search for "Simple Notification Service"

- Choose **Create topic**.
- For Topic name, type *ccbda-signup-notifications*. Choose **Standard** type and **Create topic**.
- Choose  **Create subscription**.
- For **Protocol**, choose *Email*. For **Endpoint**, enter *your email address*. Choose **Create Subscription**.

To confirm the subscription, AWS SNS sends an email named *AWS Notification — Subscription Confirmation*. Open the
link in the email to confirm your subscription.

Do not forget that before testing the new functionality you need to have the AWS SNS subscription approved.

Now you can check that your topic and subscription are correctly setup.

```
_$  aws sns list-topics
{
    "Topics": [
        {
            "TopicArn": "arn:aws:sns:eu-south-2:<YOUR-AWS-ACCOUNT-ID>:ccbda-signup-notifications"
        }
    ]
}

_$ aws sns list-subscriptions-by-topic --topic-arn arn:aws:sns:eu-south-2:<YOUR-AWS-ACCOUNT-ID>:ccbda-signup-notifications
{
    "Subscriptions": [
        {
            "SubscriptionArn": "PendingConfirmation",
            "Owner": "<YOUR-AWS-ACCOUNT-ID>",
            "Protocol": "email",
            "Endpoint": "angel.toribio@upc.edu",
            "TopicArn": "arn:aws:sns:eu-south-2:<YOUR-AWS-ACCOUNT-ID>:ccbda-signup-notifications"
        }
    ]
}
```

### Modify the web app to send messages

Add the *unique identifier* for the AWS SNS topic to the configuration environment of your local deployment. It needs to
be instantiated in the  `settings.py` and `.env` files.

```bash
NEW_SIGNUP_TOPIC="arn:aws:sns:eu-south-2:YOUR-AWS-ACCOUNT-ID:ccbda-signup-notifications"
```

Open the files *form/models.py* and *form/views.py* read and understand what the code does.

Add the code below to *form/models.py* as a new operation of the model *Leads()*.

```python
def send_notification(self, email):
    sns = boto3.client('sns', region_name=settings.AWS_REGION,
                       aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                       aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    try:
        sns.publish(
            TopicArn=settings.NEW_SIGNUP_TOPIC,
            Message='New signup: %s' % email,
            Subject='New signup',
        )
        logger.error('SNS message sent.')

    except Exception as e:
        logger.error(
            'Error sending AWS SNS message: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
```

Go to *form/views.py* and modify the signup view: if the lead has been correctly inserted in our DynamoDB table we can
send the notification.

```python
def signup(request):
    leads = Leads()
    status = leads.insert_lead(request.POST['name'], request.POST['email'], request.POST['previewAccess'])
    if status == 200:
        leads.send_notification(request.POST['email'])
    return HttpResponse('', status=status)
```

Finally, add the following line to your  *ccbda/settings.py* file

```python
    NEW_SIGNUP_TOPIC = os.getenv('NEW_SIGNUP_TOPIC')
```

Close the file and execute the Django web app locally. You can post a new record. This time you see no error, and you
receive a notification in your e-mail.

```bash
New item added to database.
SNS message sent.
"POST /signup HTTP/1.1" 200 0
```

> :question: **Question 2**: Has everything gone alright? Quickly explain the code modifications.

<a id="Task45" />

## Task 4.5: Configure Docker

In this task, you will migrate the web application to run in a Docker container. The Docker container is portable and
could run on any OS that has the Docker engine installed.

The [Docker daemon](https://docs.docker.com/get-started/docker-overview/#docker-architecture) (dockerd) listens for
Docker API requests and manages Docker objects such as images, containers, networks, and volumes. A daemon can also
communicate with other daemons to manage Docker services.

For Windows and OSx operating systems, the Docker daemon is started by opening the
Docker [Desktop application](https://docs.docker.com/desktop/). Therefore, start the Docker Desktop application before
continuing.

### Create a Dockerfile

A Dockerfile is a script that tells Docker how to build your Docker image. Put it in the root directory of your Django
project. Here’s a basic Dockerfile setup for Django:

```dockerfile
# Use the official Python runtime image
FROM python:3.13.9  
 
# Create the app directory
RUN mkdir /app
 
# Set the working directory inside the container
WORKDIR /app
 
# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 
 
# Upgrade pip
RUN pip install --upgrade pip 
 
# Copy the Django project  and install dependencies
COPY requirements.txt  /app/
 
# run this command to install all dependencies 
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy the Django project to the container
COPY . /app/
 
# Expose the Django port
EXPOSE 8000
 
# Run Django’s development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

Each line in the Dockerfile serves a specific purpose:

- **FROM**: Selects the image with the Python version you need.

- **WORKDIR**: Sets the working directory of the application within the container.

- **ENV**: Sets the environment variables needed to build the application

- **RUN** and **COPY** commands: Install dependencies and copy project files.

- **EXPOSE** and **CMD**: Expose the Django server port and define the startup command.

Go to your Docker Desktop and open the terminal, move to the directory where the web application is stored and build the
docker image.

```bash
_$ cd django-webapp               
_$ docker build -t django-docker .
[+] Building 32.8s (12/12) FINISHED                                                                   docker:desktop-linux
 => [internal] load build definition from Dockerfile                                                                  0.0s
 => => transferring dockerfile: 836B                                                                                  0.0s
 => [internal] load metadata for docker.io/library/python:3.13.9                                                      1.0s
 => [internal] load .dockerignore                                                                                     0.0s
 => => transferring context: 108B                                                                                     0.0s
 => [1/7] FROM docker.io/library/python:3.13.9@sha256:bc336add24c507d3a11b68a08fe694877faae3eab2d0e18b0653097f1a0db9  1.9s
 => => resolve docker.io/library/python:3.13.9@sha256:bc336add24c507d3a11b68a08fe694877faae3eab2d0e18b0653097f1a0db9  0.0s
 => => sha256:5e9ad5aa09b47978b1d78d8e37974138d57e5ffddce0ae411463fac97bddca83 249B / 249B                            0.2s
 => => sha256:854e2aed8debacc19d5e07410cdb618bf78860003d6bc9eeccc889a097eadcb8 27.36MB / 27.36MB                      0.9s
 => => sha256:21754c21aa78844ad4c04fa8837c92d47f71c59dd5e450e93eddb2c2d368c197 6.16MB / 6.16MB                        0.8s
 => => extracting sha256:21754c21aa78844ad4c04fa8837c92d47f71c59dd5e450e93eddb2c2d368c197                             0.3s
 => => extracting sha256:854e2aed8debacc19d5e07410cdb618bf78860003d6bc9eeccc889a097eadcb8                             0.7s
 => => extracting sha256:5e9ad5aa09b47978b1d78d8e37974138d57e5ffddce0ae411463fac97bddca83                             0.0s
 => [internal] load build context                                                                                     0.0s
 => => transferring context: 17.40kB                                                                                  0.0s
 => [2/7] RUN mkdir /app                                                                                              0.5s
 => [3/7] WORKDIR /app                                                                                                0.0s
 => [4/7] RUN pip install --upgrade pip                                                                               8.0s
 => [5/7] COPY requirements.txt  /app/                                                                                0.0s
 => [6/7] RUN pip install --no-cache-dir -r requirements.txt                                                         16.0s
 => [7/7] COPY . /app/                                                                                                0.1s
 => exporting to image                                                                                                5.1s
 => => exporting layers                                                                                               2.9s
 => => exporting manifest sha256:5734e099389204152daa1dc7f776eac832a9a906e67b1a2cc3c59d56ca106758                     0.0s
 => => exporting config sha256:76e68189a7448ac9a3e587611ebc0024fa61182885a019ba7e1d0819241bc4b4                       0.0s
 => => exporting attestation manifest sha256:71a2d3653951af13b510378334de77508b6a21dc3a6209ec7811060e4cf70698         0.0s
 => => exporting manifest list sha256:a1545142ab1d416ac5770a752d595e05cc8bd688ab0c4a5b78fb49acd4b4c20e                0.0s
 => => naming to docker.io/library/django-docker:latest                                                               0.0s
 => => unpacking to docker.io/library/django-docker:latest                                                            2.2s

View build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/5yaxtomey9oe1bp7wuz8fud9b
```

To see the new image created, you can run:

```bash 
_$ docker image list
REPOSITORY          TAG       IMAGE ID       CREATED          SIZE
django-docker       latest    a1545142ab1d   51 seconds ago   1.85GB
```

You can now create a **container** from the image using the command below. This command maps the container's internal port `8000` to the local computer's port `8080` and supplies the latest values for the configuration variables via [environment variables](https://en.wikipedia.org/wiki/Environment_variable). Port `8080` is explicitly used to highlight Docker's port binding functionality.


The command will not return and will be updating the output with the requests that it is receiving. You need to type
CONTROL-C to stop the container. Open a new terminal if you need to issue additional commands such as "docker stop" to
alternativelly stop the container.

```bash
_$ docker run -p 8080:8000 --env-file .env django-docker
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
March 09, 2025 - 20:22:05
Django version 5.1.7, using settings 'ccbda.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.

"GET / HTTP/1.1" 200 7299
New item added to database.
SNS message sent.
"POST /signup HTTP/1.1" 200 0
"GET / HTTP/1.1" 200 7299
New item added to database.
SNS message sent.
"POST /signup HTTP/1.1" 200 0
```

Open the URL http://0.0.0.0:8080/ in your browser and test the web application. If you did all the steps correctly you
shall be able to add a new entry to the database.

> [!Important]
> See that the application complains about unapplied migrations. We'll fix this later.
> ```
> You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
> Run 'python manage.py migrate' to apply them.
> ```


> :question: **Question 3**: Has everything gone alright? Share your thoughts on the task developed above.


<a id="Task46" />

## Task 4.6: Deploy the target web app

Although this is a great start in containerizing the application, you’ll need to make a number of improvements to get it
ready for production.

- The CMD `manage.py` is only meant for development purposes and should be changed for
  a [WSGI](https://wsgi.readthedocs.io/en/latest/what.html) server.
- Reduce the size of the image by using a smaller linux image.
- Optimize the image by using a multistage build process.

Let’s get started with these improvements.

### Update requirements.txt

Make sure to add [`gunicorn`](https://gunicorn.org/) and `psycopg2-binary` to your `requirements.txt`. The updated file
should look something like this:

```text
Django==5.2.8
asgiref==3.10.0
boto3==1.40.74
botocore==1.40.74
dotenv==0.9.9
gunicorn==23.0.0
jmespath==1.0.1
packaging==25.0
psycopg2-binary==2.9.11
python-dateutil==2.9.0.post0
python-dotenv==1.2.1
s3transfer==0.14.0
six==1.17.0
sqlparse==0.5.3
typing_extensions==4.15.0
urllib3==2.5.0
```

### Make improvements to the Dockerfile

The Dockerfile below has changes that solve the three items on the list. The changes to the file are as follows:

- Updated the FROM python:3.13.9 image to FROM python:3.13.9-slim. This change reduces the size of the image
  considerably, as the image now only contains what is needed to run the application.
- Added a multi-stage build process to the Dockerfile. When you build applications, there are usually many files left on
  the file system that are only needed during build time and are not needed once the application is built and running.
  By adding a build stage, you use one image to build the application and then move the built files to the second image,
  leaving only the built code. Read more about [multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
  in the documentation.
- Add the Gunicorn WSGI server to enable a production-ready deployment of the application.

```dockerfile
# Stage 1: Base build stage
FROM python:3.13.9-slim AS builder
 
# Create the app directory
RUN mkdir /app
 
# Set the working directory
WORKDIR /app
 
# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
# Upgrade pip and install dependencies
RUN pip install --upgrade pip 
 
# Copy the requirements file first (better caching)
COPY requirements.txt /app/
 
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
 
# Stage 2: Production stage
FROM python:3.13.9-slim
 
RUN useradd -m -r appuser && \
   mkdir /app && \
   chown -R appuser /app
 
RUN apt-get update && \
   DEBIAN_FRONTEND=noninteractive && \
   apt-get install --no-install-recommends --assume-yes postgresql-client

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
 
# Set the working directory
WORKDIR /app
 
# Copy application code
COPY --chown=appuser:appuser . .
 
# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
# Switch to non-root user
USER appuser
 
# Expose the application port
EXPOSE 8000 
 
# Start the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "ccbda.wsgi:application"]
```

Build the Docker container image again.

```bash
_$ docker build -t django-docker .
[+] Building 0.9s (16/16) FINISHED                                                                    docker:desktop-linux
 => [internal] load build definition from Dockerfile                                                                  0.0s
 => => transferring dockerfile: 1.31kB                                                                                0.0s
 => [internal] load metadata for docker.io/library/python:3.13.9-slim                                                 0.4s
 => [internal] load .dockerignore                                                                                     0.0s
 => => transferring context: 108B                                                                                     0.0s
 => [builder 1/6] FROM docker.io/library/python:3.13.9-slim@sha256:f3614d98f38b0525d670f287b0474385952e28eb43016655d  0.0s
 => => resolve docker.io/library/python:3.13.9-slim@sha256:f3614d98f38b0525d670f287b0474385952e28eb43016655dd003d0e2  0.0s
 => [internal] load build context                                                                                     0.0s
 => => transferring context: 17.80kB                                                                                  0.0s
 => CACHED [stage-1 2/6] RUN useradd -m -r appuser &&    mkdir /app &&    chown -R appuser /app                       0.0s
 => CACHED [builder 2/6] RUN mkdir /app                                                                               0.0s
 => CACHED [builder 3/6] WORKDIR /app                                                                                 0.0s
 => CACHED [builder 4/6] RUN pip install --upgrade pip                                                                0.0s
 => CACHED [builder 5/6] COPY requirements.txt /app/                                                                  0.0s
 => CACHED [builder 6/6] RUN pip install --no-cache-dir -r requirements.txt                                           0.0s
 => CACHED [stage-1 3/6] COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site  0.0s
 => CACHED [stage-1 4/6] COPY --from=builder /usr/local/bin/ /usr/local/bin/                                          0.0s
 => CACHED [stage-1 5/6] WORKDIR /app                                                                                 0.0s
 => [stage-1 6/6] COPY --chown=appuser:appuser . .                                                                    0.0s
 => exporting to image                                                                                                0.2s
 => => exporting layers                                                                                               0.1s
 => => exporting manifest sha256:56db48fb15a56394b268acbe3c80d51b25d08f736d293ee89f62158b3ab619b8                     0.0s
 => => exporting config sha256:573556a701dae35a76b79413265d839d49ab2f7e402cb57aca462e1e9cca0432                       0.0s
 => => exporting attestation manifest sha256:f6b7d79f2dfdfdfef29bc20bae2f6b82dfbd21ab9d685482d92aaf704d8757ce         0.0s
 => => exporting manifest list sha256:bef8941dad38cae70d4b6cca04f98c5312074ce6b955c1af3d02ecbb1b86783f                0.0s
 => => naming to docker.io/library/django-docker:latest                                                               0.0s
 => => unpacking to docker.io/library/django-docker:latest                                                            0.0s

View build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/eozjf8cg6oqlycu26ukdja5sb
```

After making these changes, we can run a docker image list again:

```text
_$  docker image list  
REPOSITORY          TAG       IMAGE ID       CREATED              SIZE
django-docker       latest    bef8941dad38   About a minute ago   488MB
```

You can see a significant improvement in the size of the container.

The size was reduced from 1.85GB to 488MB, which leads to faster a deployment process when images are downloaded and
cheaper storage costs when storing images.

### Production-ready database

Django is configured to, by default use a [SQLite](https://www.sqlite.org/) database which is not suitable for
production environments. Let's add a [PostGreSQL](https://www.postgresql.org/) database that will be running in another
container. See below the definition of the databases usage in the file `settings.py`.

```python

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    "postgresql": {
        "ENGINE": "django.db.backends.postgresql",
        'DISABLE_SERVER_SIDE_CURSORS': True,
        "NAME": os.getenv('DB_NAME', '---no-db-name---'),
        "USER": os.getenv('DB_USER', '---no-db-user---'),
        "PASSWORD": os.getenv('DB_PASSWORD', '---no-db-password---'),
        "HOST": os.getenv('DB_HOST', '127.0.0.1'),
        "PORT": os.getenv('DB_PORT', 5432),
    }
}

DATABASES['default'] = DATABASES[os.getenv('DATABASE', 'default')]
```

### Configure the Docker Compose file

A `compose.yml` file allows you to manage multi-container applications.

<img alt="Lab04-containers.png" src="images/Lab04-containers.png" width="50%"/>

The following file creates two containers: `db` and `code` and one volume `postgres_data` that is used to store the
database contents. Volumes are mounted to filesystem paths in your containers. Additionally, each container exposes some
ports and connects them to external ports of the deployment.

[**Volumes**](https://docs.docker.com/engine/storage/volumes/) are the recommended method for persisting data used or generated by Docker containers. Unlike bind mounts, which depend on the host's directory structure and operating system, volumes are fully managed by Docker, ensuring seamless portability and consistency across environments.


```yaml
services:
  db:
    image: postgres:17
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
    container_name: postgress-db
    healthcheck:
      test: [ "CMD", "pg_isready", "-q", "-d", "${DB_NAME}", "-U", "${DB_USER}" ]
      interval: 1s
      timeout: 5s
      retries: 10
  code:
    build: .
    container_name: code
    ports:
      - "8080:8000"
    depends_on:
      - db
    environment:
      - DJANGO_DEBUG=${DJANGO_DEBUG}
      - DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS}
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
      - DJANGO_LOGLEVEL=${DJANGO_LOGLEVEL}
      - DATABASE=${DATABASE}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=${DB_HOST}
      - DB_PORT=${DB_PORT}
      - CCBDA_SIGNUP_TABLE=${CCBDA_SIGNUP_TABLE}
      - AWS_REGION=${AWS_REGION}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
volumes:
  postgres_data:
```

Let's now create a new file named `production.env` to define the same `.env` variables adding the ones related to using
the
PostGreSQL database.

```bash
_$ cat production.env
DJANGO_DEBUG="False"
DJANGO_ALLOWED_HOSTS="localhost:127.0.0.1:0.0.0.0"
DJANGO_SECRET_KEY="-lm+)b44uap8!0-^1w9&2zokys(47)8u698=dy0mb&6@4ee-hh"
DJANGO_LOGLEVEL="INFO"
CCBDA_SIGNUP_TABLE="ccbda-signup-table"
AWS_REGION="eu-south-2"
AWS_DEFAULT_REGION=AWS_REGION
AWS_ACCESS_KEY_ID="<YOUR-AWS-ACCESS-KEY-ID>"
AWS_SECRET_ACCESS_KEY="<YOUR-AWS-SECRET-ACCESS-KEY>"
NEW_SIGNUP_TOPIC="arn:aws:sns:eu-south-2:<YOUR-AWS-ACCOUNT-ID>:ccbda-signup-notifications"
DB_NAME="ccbdadb"
DB_USER="ccbdauser"
DB_PASSWORD="ccbdapassword"
DB_PORT="5432"
DB_HOST="db"
DATABASE="postgresql"
```

We need to add a new file named `.dockerignore`, similar to `.gitignore`, where we configure what files and folders
shall not be copied to the container when creating the Docker image.

```bash
_$ cat .dockerignore
.venv
*.env
.gitignore
README.md
compose.yml
*.sqlite
*.sqlite3
.DS_Store
.git
.idea
.private
```

### Build and run your new Django project

By running the following command, Docker pulls the PostGreSQL container image from a Docker repository. It then creates
a database with the name, user and password that we have defined. For the second container it copies the code, creates
the Pyton environment and everything that is detailed in the given Dockerfile. Please note that the docker image created
has a frozen copy of the code. If the web application code changes it will be necessary to rebuild the image and deploy
it into its container. Check the log after the command to follow the creation process for both containers.

```bash
_$ docker compose --env-file production.env up
[+] Running 14/14
 ✔ db Pulled                                                                                                                                      6.8s 
Compose now can delegate build to bake for better performances
Just set COMPOSE_BAKE=true
[+] Building 4.5s (18/18) FINISHED                                                                                                docker:desktop-linux
 => [code internal] load build definition from Dockerfile                                                                                          0.0s
 => => transferring dockerfile: 1.31kB                                                                                                            0.0s
 => [code internal] load metadata for docker.io/library/python:3.13.9-slim                                                                         0.8s
 => [code auth] library/python:pull token for registry-1.docker.io                                                                                 0.0s
 => [code internal] load .dockerignore                                                                                                             0.0s
 => => transferring context: 130B                                                                                                                 0.0s
 => [code builder 1/6] FROM docker.io/library/python:3.13.9-slim@sha256:f3614d98f38b0525d670f287b0474385952e28eb43016655dd003d0e28cf8652           0.0s
 => => resolve docker.io/library/python:3.13.9-slim@sha256:f3614d98f38b0525d670f287b0474385952e28eb43016655dd003d0e28cf8652                       0.0s
 => [code internal] load build context                                                                                                             0.1s
 => => transferring context: 22.11kB                                                                                                              0.1s
 => CACHED [code stage-1 2/6] RUN useradd -m -r appuser &&    mkdir /app &&    chown -R appuser /app                                               0.0s
 => CACHED [code builder 2/6] RUN mkdir /app                                                                                                       0.0s
 => CACHED [code builder 3/6] WORKDIR /app                                                                                                         0.0s
 => CACHED [code builder 4/6] RUN pip install --upgrade pip                                                                                        0.0s
 => CACHED [code builder 5/6] COPY requirements.txt /app/                                                                                          0.0s
 => CACHED [code builder 6/6] RUN pip install --no-cache-dir -r requirements.txt                                                                   0.0s
 => CACHED [code stage-1 3/6] COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/                0.0s
 => CACHED [code stage-1 4/6] COPY --from=builder /usr/local/bin/ /usr/local/bin/                                                                  0.0s
 => CACHED [code stage-1 5/6] WORKDIR /app                                                                                                         0.0s
 => [code stage-1 6/6] COPY --chown=appuser:appuser . .                                                                                            0.7s
 => [code] exporting to image                                                                                                                      2.6s
 => => exporting layers                                                                                                                           0.1s
 => => exporting manifest sha256:2222b5f73ed85273f12efae0558757fa351bab444311dc2386452c4c2baa975c                                                 0.0s
 => => exporting config sha256:926f8eaca3f3e66e3477352e6ab02c545db461429749568cc737a41ee4e0faae                                                   0.0s
 => => exporting attestation manifest sha256:4098f7bccec9fe7fde841baacf7ded8be6b98e84b22e7c9851e4492cdfa23529                                     0.0s
 => => exporting manifest list sha256:5308235bfe9356bf00b3c907e44248d5daac8f7ffe18fb2fd05360e4ee685db2                                            0.0s
 => => naming to docker.io/library/django-webapp-code:latest                                                                                       0.0s
 => => unpacking to docker.io/library/django-webapp-code:latest                                                                                    2.4s
 => [code] resolving provenance for metadata file                                                                                                  0.0s
[+] Running 5/5
 ✔ code                                   Built                                                                                                    0.0s 
 ✔ Network django-webapp_default         Created                                                                                                  0.1s 
 ✔ Volume "django-webapp_postgres_data"  Created                                                                                                  0.0s 
 ✔ Container postgress-db                Created                                                                                                  0.5s 
 ✔ Container django-docker               Created                                                                                                  0.2s 
Attaching to django-docker, postgress-db
postgress-db   | The files belonging to this database system will be owned by user "postgres".
postgress-db   | This user must also own the server process.
postgress-db   | 
postgress-db   | The database cluster will be initialized with locale "en_US.utf8".
postgress-db   | The default database encoding has accordingly been set to "UTF8".
postgress-db   | The default text search configuration will be set to "english".
postgress-db   | 
postgress-db   | Data page checksums are disabled.
postgress-db   | 
postgress-db   | fixing permissions on existing directory /var/lib/postgresql/data ... ok
postgress-db   | creating subdirectories ... ok
postgress-db   | selecting dynamic shared memory implementation ... posix
postgress-db   | selecting default "max_connections" ... 100
postgress-db   | selecting default "shared_buffers" ... 128MB
postgress-db   | selecting default time zone ... Etc/UTC
postgress-db   | creating configuration files ... ok
postgress-db   | running bootstrap script ... ok
django-docker  | [2026-03-14 14:27:55 +0000] [1] [INFO] Starting gunicorn 23.0.0
django-docker  | [2026-03-14 14:27:55 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
django-docker  | [2026-03-14 14:27:55 +0000] [1] [INFO] Using worker: sync
django-docker  | [2026-03-14 14:27:55 +0000] [7] [INFO] Booting worker with pid: 7
django-docker  | [2026-03-14 14:27:55 +0000] [8] [INFO] Booting worker with pid: 8
postgress-db   | performing post-bootstrap initialization ... ok
django-docker  | [2026-03-14 14:27:55 +0000] [9] [INFO] Booting worker with pid: 9
postgress-db   | initdb: warning: enabling "trust" authentication for local connections
postgress-db   | initdb: hint: You can change this by editing pg_hba.conf or using the option -A, or --auth-local and --auth-host, the next time you run initdb.
postgress-db   | syncing data to disk ... ok
postgress-db   | 
postgress-db   | 
postgress-db   | Success. You can now start the database server using:
postgress-db   | 
postgress-db   |     pg_ctl -D /var/lib/postgresql/data -l logfile start
postgress-db   | 
postgress-db   | waiting for server to start....2026-03-14 14:27:55.434 UTC [54] LOG:  starting PostgreSQL 17.4 (Debian 17.4-1.pgdg120+2) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit
postgress-db   | 2026-03-14 14:27:55.439 UTC [54] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
postgress-db   | 2026-03-14 14:27:55.446 UTC [57] LOG:  database system was shut down at 2026-03-14 14:27:55 UTC
postgress-db   | 2026-03-14 14:27:55.452 UTC [54] LOG:  database system is ready to accept connections
postgress-db   |  done
postgress-db   | server started
postgress-db   | CREATE DATABASE
postgress-db   | 
postgress-db   | 
postgress-db   | /usr/local/bin/docker-entrypoint.sh: ignoring /docker-entrypoint-initdb.d/*
postgress-db   | 
postgress-db   | waiting for server to shut down....2026-03-14 14:27:55.663 UTC [54] LOG:  received fast shutdown request
postgress-db   | 2026-03-14 14:27:55.667 UTC [54] LOG:  aborting any active transactions
postgress-db   | 2026-03-14 14:27:55.672 UTC [54] LOG:  background worker "logical replication launcher" (PID 60) exited with exit code 1
postgress-db   | 2026-03-14 14:27:55.672 UTC [55] LOG:  shutting down
postgress-db   | 2026-03-14 14:27:55.675 UTC [55] LOG:  checkpoint starting: shutdown immediate
postgress-db   | 2026-03-14 14:27:55.746 UTC [55] LOG:  checkpoint complete: wrote 921 buffers (5.6%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.023 s, sync=0.043 s, total=0.074 s; sync files=301, longest=0.011 s, average=0.001 s; distance=4238 kB, estimate=4238 kB; lsn=0/1908978, redo lsn=0/1908978
postgress-db   | 2026-03-14 14:27:55.751 UTC [54] LOG:  database system is shut down
postgress-db   |  done
postgress-db   | server stopped
postgress-db   | 
postgress-db   | PostgreSQL init process complete; ready for start up.
postgress-db   | 
postgress-db   | 2026-03-14 14:27:55.798 UTC [1] LOG:  starting PostgreSQL 17.4 (Debian 17.4-1.pgdg120+2) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit
postgress-db   | 2026-03-14 14:27:55.798 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
postgress-db   | 2026-03-14 14:27:55.798 UTC [1] LOG:  listening on IPv6 address "::", port 5432
postgress-db   | 2026-03-14 14:27:55.802 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
postgress-db   | 2026-03-14 14:27:55.808 UTC [70] LOG:  database system was shut down at 2026-03-14 14:27:55 UTC
postgress-db   | 2026-03-14 14:27:55.815 UTC [1] LOG:  database system is ready to accept connections                     
```

Finally, as we saw above, Django needs that the database contains some tables. That task needs to be done only at the beginning, or every
time that the Django code changes its data models. See that the command below **exec**utes in the container named "code"
the command line `python manage.py migrate`.

```bash
_$ docker compose --env-file production.env exec code python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK
```

### Test and access your application and its containers

Once the webapp is running, you can test it by navigating to http://localhost:8000. You should see Django’s welcome
page, indicating that your app is up and running.

Take into account that both containers are exporting their ports to the outside world and mapping them to the same port
number of the docker host (check the composer file and find ports:- "8080:8000", ports:- "5432:5432"). That means that you can access the web application through port 8080 and the PostGreSQL through port 5432 of the localhost machine, or the hosting machine of the containers. See below how PyCharm is able to connect to the database hosted in Docker.

<img alt="Lab04-postgres-config.png" src="images/Lab04-postgres-config.png" width="50%"/>

<img alt="Lab04-postgres-use.png" src="images/Lab04-postgres-use.png" width="50%"/>

Additionally, you can also create a command line connection with each container by issuing the commands below. See that
the command `docker exec -it 07 bash` executes a `bash` interactive command line interpreter (CLI) that shows the prompt
`appuser@07bd0798d09f:/app$` meaning that you are inside of the docker container. `07bd0798d09f` is the container ID
that shall be used in the `-it` parameter, but only a few initial distinctive characters are needed. Use CONTROL-D to
exit the CLI.

Please check that `.dockertignore` has prevented some files to be copied into the image of the code container.

```bash
_$ docker ps
CONTAINER ID   IMAGE               COMMAND                  CREATED          STATUS                    PORTS                    NAMES
07bd0798d09f   django-webapp-code   "gunicorn --bind 0.0…"   26 minutes ago   Up 26 minutes             0.0.0.0:8000->8080/tcp   django-docker
de27f59e7644   postgres:17         "docker-entrypoint.s…"   26 minutes ago   Up 26 minutes (healthy)   0.0.0.0:5432->5432/tcp   postgress-db
_$ docker exec -it 07 bash
appuser@07bd0798d09f:/app$  ls -l
total 168
-rw-r--r-- 1 appuser appuser   1230 Mar 12 21:48 Dockerfile
drwxr-xr-x 3 appuser appuser   4096 Mar 14 14:09 ccbda
drwxr-xr-x 3 appuser appuser   4096 Mar 14 14:09 form
-rwxr-xr-x 1 appuser appuser    661 Mar  8 18:52 manage.py
-rw-r--r-- 1 appuser appuser    285 Mar  9 15:11 requirements.txt
drwxr-xr-x 2 appuser appuser   4096 Mar  9 12:30 static
drwxr-xr-x 3 appuser appuser   4096 Mar  9 12:29 templates
^D

_$ docker exec -it de bash
root@de27f59e7644:/# ls -l
total 56
lrwxrwxrwx   1 root root    7 Feb 24 00:00 bin -> usr/bin
drwxr-xr-x   2 root root 4096 Dec 31 10:25 boot
drwxr-xr-x   5 root root  340 Mar 14 14:27 dev
drwxr-xr-x   2 root root 4096 Feb 28 23:24 docker-entrypoint-initdb.d
drwxr-xr-x   1 root root 4096 Mar 14 14:27 etc
drwxr-xr-x   2 root root 4096 Dec 31 10:25 home
lrwxrwxrwx   1 root root    7 Feb 24 00:00 lib -> usr/lib
lrwxrwxrwx   1 root root    9 Feb 24 00:00 lib64 -> usr/lib64
drwxr-xr-x   2 root root 4096 Feb 24 00:00 media
drwxr-xr-x   2 root root 4096 Feb 24 00:00 mnt
drwxr-xr-x   2 root root 4096 Feb 24 00:00 opt
dr-xr-xr-x 220 root root    0 Mar 14 14:27 proc
drwx------   1 root root 4096 Feb 28 23:24 root
drwxr-xr-x   1 root root 4096 Feb 28 23:24 run
lrwxrwxrwx   1 root root    8 Feb 24 00:00 sbin -> usr/sbin
drwxr-xr-x   2 root root 4096 Feb 24 00:00 srv
^D
```

> :question: **Question 4**: Share your thoughts on the task developed above.


<a id="Task47"/>

## Task 4.7: Analisys of the twelve-factor app methodology

The [twelve-factor app](https://12factor.net/) is a methodology for building software-as-a-service apps that:

- Use **declarative** formats for setup automation, to minimize time and cost for new developers joining the project;
- Have a **clean contract** with the underlying operating system, offering **maximum portability** between execution
  environments;
- Are suitable for **deployment** on modern **cloud platforms**, obviating the need for servers and systems
  administration;
- **Minimize divergence** between development and production, enabling **continuous deployment** for maximum agility;
- And can **scale up** without significant changes to tooling, architecture, or development practices.

### The Twelve Factors

1. **Codebase**:
   One codebase tracked in revision control, many deploys

1. **Dependencies**:
   Explicitly declare and isolate dependencies

1. **Config**:
   Store config in the environment

1. **Backing services**:
   Treat backing services as attached resources

1. **Build, release, run**:
   Strictly separate build and run stages

1. **Processes**:
   Execute the app as one or more stateless processes

1. **Port binding**:
   Export services via port binding

1. **Concurrency**:
   Scale out via the process model

1. **Disposability**:
   Maximize robustness with fast startup and graceful shutdown

1. **Dev/prod parity**:
   Keep development, staging, and production as similar as possible

1. **Logs**:
   Treat logs as event streams

1. **Admin processes**:
   Run admin/management tasks as one-off processes

> :question: **Question 5**: For the above lab session, explain, one by one, how each factor is taken into 
consideration, or what would you change or add to comply with each factor

## Submit Your Assignment

> :question: **Question 6:** How much time did you spend on this session?  
  
> :question: **Question 7:** What challenges did you encounter, and how did you overcome them?

> :question: **Question 8:** Using the AWS Billing and Cost Management Service, access the "Cost Explorer"  and capture the cost of last week Using the "Dimension" "Service" where you can see how much did you spend to complete the session in total and per  service.

Push your updated repository to GitHub https://github.com/CCBDA-UPC/2026_1-4-xx **before the deadline**, including:

- `README.md` with all your responses and documentation
- Any screenshots
- All new Python files required by the tasks