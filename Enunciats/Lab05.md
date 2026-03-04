# Lab Session #5: Running a custom web app in the cloud

This lab session **builds upon the work from the previous session** where we isolated the web application within a Docker container running locally. Make sure that you have available and working everything done in the previous session.

In this session, we will use a more robust SQL database engine and scale the application by running multiple instances. A load balancer will be used to distribute incoming requests across these instances, ensuring optimal performance.

AWS provides different services to execute Docker containers, one of them is AWS Elastic Beanstalk.

At the end of this session you will have the custom web application running in the cloud while accessing a set of robust database systems. The web application will be able to automatically adapt to a variable number of requests by using a load balancer and as many computing instances as necessary.

### AWS RDS: AWS Relational Database Service

**AWS RDS** is a managed database service that simplifies the setup, operation, and scaling of relational databases in the cloud. It allows you to run databases such as MySQL, PostgreSQL, MariaDB, Oracle Database, and Microsoft SQL Server without the need to manage the underlying infrastructure manually.

#### Key Features:
1. **Managed Service**: Automates time-consuming tasks like provisioning, upgrading, patching, backups, and recovery.
2. **Performance**: Offers high performance with support for read replicas, caching, and optimized configurations.
3. **Scalability**: Easily scale database instances up or down to adjust to workload demands.
4. **Security**: Provides built-in security features like encryption at rest, encryption in transit, and integration with AWS Identity and Access Management (IAM).
5. **Backup and Recovery**: Comes with automated backups and point-in-time restoration capabilities.
6. **Multi-AZ Deployment**: Supports high availability through Multi-AZ deployments, which provide automatic failover to a secondary instance in case of a failure.

#### Benefits:
- Reduces administrative overhead by automating routine database tasks.
- Ensures better reliability and uptime with features like replication and Multi-AZ deployments.
- Pay-as-you-go pricing makes it cost-effective for a broad range of use cases.

AWS RDS is widely used for hosting production databases, applications, and even analytics workloads while reducing operational complexity.

### AWS ECR: Elastic Container Registry

AWS Elastic Container Registry (AWS ECR) is an AWS managed container image registry service that is secure, scalable, and reliable. AWS ECR supports private repositories with resource-based permissions using AWS IAM. This is so that specified users or AWS EC2 instances can access your container repositories and images. You can use your preferred CLI to push, pull, and manage Docker images.

### AWS Elastic Beanstalk 
With AWS Elastic Beanstalk, you can quickly deploy and manage applications in the AWS Cloud without worrying about the infrastructure that runs those applications. AWS Elastic Beanstalk reduces management complexity without restricting choice or control. You simply upload your application, and AWS Elastic Beanstalk automatically handles the details of capacity provisioning, load balancing, scaling, and application health monitoring.

## Pre-lab homework

You need to install the Elastic Beanstalk CLI. You can find more information on  **[eb
command line interface](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-getting-started.html)**.

On macOS you can use:

``` 
_$ brew install awsebcli
```

# Tasks for Lab session #5

* [Task 5.1: AWS Relational Database Service](#Task51)
* [Task 5.2: Adding the Docker images to AWS ECR](#Task52)
* [Task 5.3: Running Docker Container images on AWS Elastic Beanstalk](#Task53)


<a id="Task51"/>

## Task 5.1: AWS Relational Database Service

In lab session 4 we used a PostGreSQL database installed in a container. In this session we are going to be using a more robust database provided by the AWS RDS service.

### Create your AWS RDS PostGreSQL instance

Navigate to the AWS `Aurora and RDS` console to create a new PostGreSQL database engine that will replace the database engine used in the previous lab session.

For the `database creation method` use `Easy create` and `PostGreSQL` for the `Configuration` box. A `DB instance size` of `Free tier` will be enough for the Lab session.

In `DB instance identifier` type `database-lab`, for `Master username` keep `postgres`, for `Credentials management` select `self managed`, for `Master password` type `MyP4ssW0rd!`, and finally click on the `Create database` button. Skip the add-on screen and wait a few minutes until the database is created. 

Click on the database links, find and copy the database `Endpoint` in the text file. That is the DNS name for the new database engine to be accessed by any application.

<img alt="Lab06-rds.png" src="images/Lab05-rds.png" width="80%"/>

> [!Caution]
> AWS RDS is a **very expensive** service, and it runs 24/7 draining your budget. 
> DO NOT FORGET to stop the database when you don't need it anymore.

### Temporarily open the database access to your laptop

By default, following the `Easy create` wizard, the database engine is only accessible inside the Virtual Private Cloud, therefore the DNS name is initialized with a class B [private IP address](https://en.wikipedia.org/wiki/Private_network).

```bash
_$  ping database-lab.<YOUR-DB-INSTANCE-ID>.eu-south-2.rds.amazonaws.com
PING database-lab.<YOUR-DB-INSTANCE-ID>.eu-south-2.rds.amazonaws.com (172.31.79.242): 56 data bytes
```

To have a public IP assigned you need to `Modify` the database engine configuration, scroll down to the `Connectivity` box, unfold the `Additional configuration` and change from `Not publicly accessible` to `Publicly accessible` as shown below. Click on `Continue` and then `Modify database` buttons.


<img alt="Lab06-publicIP.png" src="images/Lab05-publicIP.png" width="" height="300px"/>

The Status will change to `Modifying` and in a few minutes it will turn green and return to `Available`. A new public IP appear then associated to the DNS name.

```bash
_$ ping database-lab.<YOUR-DB-INSTANCE-ID>.eu-south-2.rds.amazonaws.com
PING ec2-54-198-59-77.compute-1.amazonaws.com (54.198.59.77): 56 data bytes
```

Now go back to the `database-lab` properties display, where you obtained the `Endpoint` and now click on the **"default" security group** link. You will see that there is a single rule for the inbound traffic allowing any traffic inside the same security group (see screenshot below).

<img alt="Lab06-default-security-group.png" src="images/Lab05-default-security-group.png"/>

Now, you need to temporarily add a new rule to allow PostgreSQL traffic (port 5432) from your laptop. If necessary, you can add multiple rules to allow access from additional IP addresses.

<img alt="Lab06-add-security-group-rule.png" src="images/Lab05-add-security-group-rule.png"/>

If you have followed the above steps correctly, using the PyCharm database wizard you could access the database engine from your laptop as shown below. Once all the parameters are in place click on `Apply` and then `Test Connection`. You shall be getting the response shown below.

<img alt="Lab06-pycharm-rds.png" src="images/Lab05-pycharm-rds.png" width="80%"/>

> :question: **Question 1**: Explain why you will not keep that access open on a production system. How can you do manual maintenance on the database using SQL commands, when necessary? 

### Use your AWS RDS PostGreSQL instance

Let's now build a new Docker image, tagging it with a version number. Next test the web application running in Docker inside of your laptop and connect it to the AWS RDS database. 
Once the above step works, copy the production environment to a new file named `aws.env` and replace the PostGreSQL variable `DB_HOST` and adding `PGPASSWORD` with the master password as shown below.

> [!Caution]
> Since AWS EC2 by default provides instances based on Intel x86 architecture, if your laptop is **using a different architecture** (i.e. Apple M4) you need to create Docker images that use Intel x86 in order to deploy then on AWS EC2 instances by adding to `docker create` the parameter `--platform`. Please check "[Set the target platforms for the build](https://docs.docker.com/reference/cli/docker/buildx/build/#platform)".

```bash
_$ docker build -t django-docker:v1.0.0 .
_$ docker images
REPOSITORY                                                               TAG       IMAGE ID       CREATED          SIZE
django-docker                                                            latest    d8bc6a1aed71   20 minutes ago   476MB
django-docker                                                            v1.0.0    0a325b16e03d   20 minutes ago   476MB
_$ cat aws.env
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=127.0.0.1:localhost:0.0.0.0
DJANGO_SECRET_KEY=-lm+)b44uap8!0-^1w9&2zokys(47)8u698=dy0mb&6@4ee-hh
DJANGO_LOGLEVEL=INFO
CCBDA_SIGNUP_TABLE=ccbda-signup-table
AWS_REGION=eu-south-2
AWS_DEFAULT_REGION=AWS_REGION
AWS_ACCESS_KEY_ID=<YOUR-AWS-ACCESS-KEY-ID>
AWS_SECRET_ACCESS_KEY=<YOUR-AWS-SECRET-ACCESS-KEY>
NEW_SIGNUP_TOPIC=arn:aws:sns:eu-south-2:<YOUR-AWS-ACCOUNT-ID>:ccbda-signup-notifications
DB_NAME=ccbdadb
DB_USER=ccbdauser
DB_PASSWORD=ccbdapassword
DB_PORT=5432
DB_HOST=database-lab.<YOUR-DB-INSTANCE-ID>.eu-south-2.rds.amazonaws.com
DATABASE=postgresql
PGPASSWORD=MyP4ssW0rd!
```

> :question: **Question 2**: Using the above configuration file, what steps will you follow to have the web application running in your local Docker use the AWS RDS database engine?

The unix command `psql` is installed in the `django-docker` image, and you can use it by typing the command below. The values of `$DB_HOST` and `$DB_PORT` are declared inside the unix environment of the container. If an evironment variable named `PGPASSWORD` exits, psql uses its value to authenticate against the PostGreSQL database engine.

```bash
_$ env
....
HOSTNAME=307613c5c952
DB_PORT=5432
PWD=/app
DB_HOST=database-lab.<YOUR-DB-INSTANCE-ID>.eu-south-2.rds.amazonaws.com
PGPASSWORD=MyP4ssW0rd!
.....
_$ cat > init_db.sql
CREATE DATABASE ccbdadb;
CREATE USER ccbdauser
    WITH ENCRYPTED PASSWORD 'ccbdapassword'
    createdb
    createrole
    bypassrls;
ALTER USER ccbdauser SET TimeZone = utc;
ALTER DATABASE ccbdadb OWNER TO ccbdauser;
^D
_$ psql --host=$DB_HOST --port=$DB_PORT --username=postgres < init_db.sql
CREATE DATABASE
CREATE ROLE
ALTER ROLE
GRANT
_$ python manage.py migrate
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

> :question: **Question 3**: Explain what does the code in the box above. How can you execute it inside the Docker container?

> :question: **Question 4**: What is the result of "select * FROM django_migrations;"


<a id="Task52"/>

## Task 5.2: Adding the Docker image to AWS ECR

Before being able to deploy in the cloud the Docker image for the web application, that you've created in the previous lab session, we need to push it to a Docker images repository hosted in AWS: the **AWS Elastic Container Registry (AWS ECR)**.

Verify what is your `<AWS-USER-ACCOUNT-ID>` using:

```bash
_$ aws sts get-caller-identity | grep Account
    "Account": "383312122003",
```

To authorize your Docker command line client, you need to execute the following command:

```bash
_$ aws ecr get-login-password | docker login --username AWS --password-stdin <AWS-USER-ACCOUNT-ID>.dkr.ecr.eu-south-2.amazonaws.com
Login Succeeded
```


But you'll see it is not working simply because the user that your AWS CLI is using cannot retrieve the login password.

```bash
_$ aws ecr get-login-password 
An error occurred (AccessDeniedException) when calling the GetAuthorizationToken operation: User: arn:aws:iam::<AWS-USER-ACCOUNT-ID>:user/lab_webapp_user is not authorized to perform: ecr:GetAuthorizationToken on resource: * because no identity-based policy allows the ecr:GetAuthorizationToken action

```

To fix that, check that the user has all the following policies associated:

- AmazonDynamoDBFullAccess
- **AmazonEC2ContainerRegistryFullAccess**
- **AmazonElasticContainerRegistryPublicFullAccess**
- AmazonS3FullAccess
- AmazonSNSFullAccess



Verify that the command below is not throwing an error message and proceed seeing ``Login Succeeded`` as the result.

```bash
_$ aws ecr get-login-password
eyJwYXlsb2FkIjoidzJhbzJ4ZzBjcmJ6YldTMEhPVmR5Vm5hQ1ZaZlhLVldudWdBSXkxRzFaK0QyTTlpMjhONC93cndlenVFT0pRZmtTdjBnK3BOSGE0c0JrcEhvbjcxVzZyMkVLdUxKWjBmbUZQdnljYzI2Y0svM053..........cGlyYXRpb24iOjE3NjIyMzI2MDR9
```

```bash
_$ aws ecr get-login-password | docker login --username AWS --password-stdin <AWS-USER-ACCOUNT-ID>.dkr.ecr.eu-south-2.amazonaws.com
Login Succeeded
```

### Create an AWS ECR Docker repository named `django-webapp-docker-repo`

To create the repository, run the following command:

```bash
_$ aws ecr create-repository --repository-name django-webapp-docker-repo
{
    "repository": {
        "repositoryArn": "arn:aws:ecr:eu-south-2:<aws-registry-id>:repository/django-webapp-docker-repo",
        "registryId": "<aws-registry-id>",
        "repositoryName": "django-webapp-docker-repo",
        "repositoryUri": "<aws-registry-id>.dkr.ecr.eu-south-2.amazonaws.com/django-webapp-docker-repo",
        "createdAt": "2026-03-15T16:44:17.171000+01:00",
        "imageTagMutability": "MUTABLE",
        "imageScanningConfiguration": {
            "scanOnPush": false
        }
    }
}
```

The response data is in JSON format and includes a repository Arn value. This is the URI that you would use to reference your image for future deployments. The response also includes a registryId, which you will use in a moment.

### Tag the Docker image.

In this step, you will tag the image with your unique registryId value to make it easier to manage and keep track of
this image. Run the following command. Replace <aws-registry-id> with your actual registry ID number.

```
_$ docker tag django-docker:v1.0.0 <aws-registry-id>.dkr.ecr.eu-south-2.amazonaws.com/django-webapp-docker-repo:v1.0.0
_$ docker image list
<aws-registry-id>.dkr.ecr.eu-south-2.amazonaws.com/django-webapp-docker-repo   v1.0.0    1cb356277c4a   42 hours ago   433MB
django-docker                                                             v1.0.0    1cb356277c4a   42 hours ago   433MB
postgres                                                                  17        81f32a88ec56   2 weeks ago    621MB
```

The command `docker tag` does not provide a response. To verify that the tag was applied we query the images available. This time, notice that the latest tag was applied and the image name includes the remote repository name where you intend to store it.

### Push the Docker image to the AWS ECR repository.

To push your image to AWS ECR, run the following command. Replace <aws-registry-id> with your actual registry ID number:

```bash
_$ docker push <aws-registry-id>.dkr.ecr.eu-south-2.amazonaws.com/django-webapp-docker-repo:v1.0.0
The push refers to repository [<aws-registry-id>.dkr.ecr.eu-south-2.amazonaws.com/django-webapp-docker-repo]
4b785e93aa71: Pushed 
be1449717b1e: Pushed 
ff1399ac0930: Pushed 
7cf63256a31a: Pushed 
dac1d3453b30: Pushed 
e1599d0f5c4d: Pushed 
8b6fcbaf930d: Pushed 
000e068808cd: Pushed

v1.0.0: digest: sha256:79e93509f63df0e0808ba8780fdd08bb5dc597b400807637c77044c04f361125 size: 856
```

To confirm that the django-webapp-docker-repo image is now stored in AWS ECR, run the following aws `aws ecr list-images` command:

```bash
_$ aws ecr list-images --repository-name django-webapp-docker-repo
{
    "imageIds": [
        {
            "imageDigest": "sha256:e33b3087f42f9b5b23ee5ce33a8a279fc1c2a2d1070a9eaae3c298cd8d3c803f"
        },
        {
            "imageDigest": "sha256:8f1ee7414d796b6ed70dcfa9facff56438bba6b2665066362eea9b5dca2c667d"
        },
        {
            "imageDigest": "sha256:79e93509f63df0e0808ba8780fdd08bb5dc597b400807637c77044c04f361125",
            "imageTag": "v1.0.0"
        }
    ]
}
```

You can also find more details about the repositories that you have created.

```bash
_$ aws ecr describe-repositories
{
    "repositories": [
        {
            "repositoryArn": "arn:aws:ecr:eu-south-2:<aws-registry-id>:repository/django-webapp-docker-repo",
            "registryId": "<aws-registry-id>",
            "repositoryName": "django-webapp-docker-repo",
            "repositoryUri": "<aws-registry-id>.dkr.ecr.eu-south-2.amazonaws.com/django-webapp-docker-repo",
            "createdAt": "2026-03-15T16:44:17.171000+01:00",
            "imageTagMutability": "MUTABLE",
            "imageScanningConfiguration": {
                "scanOnPush": false
            }
        }
    ]
}
```

And information about the images of the repository.

```bash
_$ aws ecr describe-images --repository-name django-webapp-docker-repo
{
    "imageDetails": [
        {
            "registryId": "<aws-registry-id>",
            "repositoryName": "django-webapp-docker-repo",
            "imageDigest": "sha256:e33b3087f42f9b5b23ee5ce33a8a279fc1c2a2d1070a9eaae3c298cd8d3c803f",
            "imageSizeInBytes": 1348,
            "imagePushedAt": "2026-03-15T16:47:53.153000+01:00"
        },
        {
            "registryId": "<aws-registry-id>",
            "repositoryName": "django-webapp-docker-repo",
            "imageDigest": "sha256:8f1ee7414d796b6ed70dcfa9facff56438bba6b2665066362eea9b5dca2c667d",
            "imageSizeInBytes": 75387102,
            "imagePushedAt": "2026-03-15T16:47:53.161000+01:00"
        },
        {
            "registryId": "<aws-registry-id>",
            "repositoryName": "django-webapp-docker-repo",
            "imageDigest": "sha256:79e93509f63df0e0808ba8780fdd08bb5dc597b400807637c77044c04f361125",
            "imageTags": [
                "v1.0.0"
            ],
            "imageSizeInBytes": 75387102,
            "imagePushedAt": "2026-03-15T16:47:53.707000+01:00"
        }
    ]
}
```

<a id="Task53" />

## Task 5.3: Running Docker Container images on AWS Elastic Beanstalk

### Identification of the current EC2 instance

AWS Elastic Beanstalk automatically provisions a set of AWS EC2 instances to run containerized web applications concurrently, scaling the number of instances based on demand. It also monitors these instances by periodically sending requests to a URL on each EC2 instance and checking for an HTTP status code of 200 (success). If the code differs, it triggers a response to handle potential issues.

On the other hand, Django requires the hostnames and IP addresses of the servers to be included in the ALLOWED_HOSTS variable. This is a security measure designed to prevent HTTP Host header attacks, which can occur even with seemingly secure web server configurations. To maintain a high level of security, it is important to explicitly add the IP addresses of the AWS EC2 instances. Using a wildcard in ALLOWED_HOSTS would reduce security by allowing unintended hosts to access the application.

AWS provides a [mechanism to retrieve information for each EC2 inside the running instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html#instancedata-inside-access). If you go to the AWS EC2 console and open a terminal, type the following code that creates a token for 1h that is used to query about the local instance.

```bash
_$ TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 3600"`
_$ curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id/
i-1234567898abcdef0
_$ curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-type/
t2.nano
_$ curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/availability-zone/
eu-south-2f
_$ curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/local-ipv4/
172.17.25.45
```

We can define the `get_metadata()` function at the top of the settings.py file. Since http://169.254.169.254 is only accessible from within an EC2 instance, we set a connection timeout of 5 seconds to ensure the function doesn’t hang indefinitely.

This function is executed when the web application starts, and it keeps the value of ALLOWED_HOSTS accessible throughout the code, ensuring it is available for any necessary security checks.

```python
....
import requests
import logging

logger = logging.getLogger('django')

def get_metadata(path='', default=''):
    if DEBUG:
        logger.warning(f"Returning default value because the app it is in DEBUG mode {default} ")
        return default
    try:
        headers = {"X-aws-ec2-metadata-token-ttl-seconds": "60"}
        response = requests.put('http://169.254.169.254/latest/api/token', headers=headers, timeout=5)
        if response.status_code == 200:
            response = requests.get(f'http://169.254.169.254/latest/meta-data/{path}/',
                                    headers={'X-aws-ec2-metadata-token': response.text})
            return response.text
        else:
            logger.warning(f"Didn't get metadata token: {response.status_code}")
            return default
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error accessing metadata: {e}")
        return default
...
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS').split(':')
LOCAL_IP = get_metadata('local-ipv4','127.0.0.1')
ALLOWED_HOSTS.append(LOCAL_IP)
ALLOWED_HOSTS = list(set(ALLOWED_HOSTS))
logger.warning(f'LOCAL_IP {LOCAL_IP}\nALLOWED_HOSTS {ALLOWED_HOSTS}')
...
```

> [!Caution]
> Every change on the source code that you commit to the repo as final will need a rebuild of the Docker image

After this small code change we must create a new Docker image going to the root of the repo and typing the following commands which will create a new local Docker image tagged v1.0.1 and push it to AWS ECR.


```bash
_$ docker build -t django-docker:v1.0.1 .

_$ docker images
REPOSITORY      TAG       IMAGE ID       CREATED         SIZE
...
django-docker   v1.0.1    7b37628462cb   2 minutes ago   489MB

_$  docker tag django-docker:v1.0.1 <aws-registry-id>.dkr.ecr.eu-south-2.amazonaws.com/django-webapp-docker-repo:v1.0.1

_$ docker image list
REPOSITORY                                                                     TAG       IMAGE ID       CREATED         SIZE
...
<aws-registry-id>.dkr.ecr.eu-south-2.amazonaws.com/django-webapp-docker-repo   v1.0.1    7b37628462cb   6 minutes ago   489MB
django-docker                                                                  v1.0.1    7b37628462cb   6 minutes ago   489MB

_$ docker push <aws-registry-id>.dkr.ecr.eu-south-2.amazonaws.com/django-webapp-docker-repo:v1.0.1
The push refers to repository [<aws-registry-id>.dkr.ecr.eu-south-2.amazonaws.com/django-webapp-docker-repo]
964deb1231a9: Pushed 
7fa5f2ae2c21: Pushed 
ca65217c578a: Pushed 
d7ecded7702a: Pushed 
ad0b8045daed: Pushed 
132640288d0e: Pushed 
cf9f58e78157: Pushed 
da5a8471b1b2: Pushed 
a30891418460: Pushed 
4f4fb700ef54: Layer already exists 
1999950b614c: Pushed 
v1.0.1: digest: sha256:79e93509f63df0e0808ba8780fdd08bb5dc597b400807637c77044c04f361125 size: 856

_$ aws ecr list-images --repository-name django-webapp-docker-repo
{
    "imageIds": [
        {
            "imageDigest": "sha256:7acbd6d3d80f76dc647ed2197803c8b5a7d97852ca04833631901bf34d803acb"
        },
        {
            "imageDigest": "sha256:8b0c3520ae18de7a74493ef1a72d407130c97694a5bd3ffb4c9d4f4a06d46a76"
        },
        {
            "imageDigest": "sha256:7b37628462cb1544ee113e4ad8db07eb2993baf128d1443aa882e90654b6639e",
            "imageTag": "v1.0.1"
        }
    ]
}
```

### Launch your new Elastic Beanstalk environment

Before proceeding, please make sure that your AWS CLI user includes the following policies:

- **AdministratorAccess-AWSElasticBeanstalk**
- AmazonDynamoDBFullAccess
- AmazonEC2ContainerRegistryFullAccess
- AmazonElasticContainerRegistryPublicFullAccess
- AmazonS3FullAccess
- AmazonSNSFullAccess

Open a terminal and create a folder named `.housekeeping/elasticbeanstalk` at the top of your web application. Have the `elasticbeanstalk` folder as your working directory initialize the creation of an Elastic Beanstalk application:

```
_$ cd .housekeeping/elasticbeanstalk
_$ eb init --region eu-south-2 -i django-webapp-eb
Select a platform.
1) .NET Core on Linux
2) .NET on Windows Server
3) Docker
4) Go
5) Java
6) Node.js
7) PHP
8) Python
9) Ruby
10) Tomcat
(make a selection): 3

Select a platform branch.
1) Docker running on 64bit Amazon Linux 2023
2) ECS running on 64bit Amazon Linux 2023
3) Docker running on 64bit Amazon Linux 2
4) ECS running on 64bit Amazon Linux 2
(default is 1): 1

Do you want to set up SSH for your instances?
(Y/n): yes

Select a keypair.
1) aws-eb
2) [ Create new KeyPair ]
(default is 1): 1
```

The command `eb init` creates a configuration file at `.housekeeping/elasticbeanstalk/.elasticbeanstalk/config.yml`. You can edit it if necessary.

```yaml
branch-defaults:
  default:
    environment: null
global:
  application_name: django-webapp-eb
  branch: null
  default_ec2_keyname: aws-eb
  default_platform: Docker running on 64bit Amazon Linux 2023
  default_region: eu-south-2
  include_git_submodules: true
  instance_profile: null
  platform_name: null
  platform_version: null
  profile: null
  repository: null
  sc: null
  workspace_type: Application
```

Now, you need to create an Elastic Beanstalk environment and run the application. That needs a quite complex command line that we are going to create using a python script in the file `ebcreate.py` that you'll save inside the `.housekeeping/scripts` folder.

```python
from dotenv import dotenv_values
import sys

ebOptions = {
    'min-instances': '1',
    'max-instances': '3',
    'instance_profile': 'aws-elasticbeanstalk-ec2-role',
    'service-role': 'aws-elasticbeanstalk-service-role',
    'elb-type': 'application',
    'instance-types':'t3.micro',
    'keyname':'aws-eb'
}

try:
    CONFIGURATION_FILE = sys.argv[1]
    HOSTNAME = sys.argv[2]
except:
    print('ERROR: filename missing\npython ebcreate.py environment hostname')
    exit()
config = dotenv_values(CONFIGURATION_FILE)

hostname = f'{HOSTNAME}.{config["AWS_REGION"]}.elasticbeanstalk.com'

hosts = config['DJANGO_ALLOWED_HOSTS'].split(':')
if hostname not in hosts:
    hosts.append(hostname)
    config['DJANGO_ALLOWED_HOSTS'] = ':'.join(hosts)
opt = []
for k, v in config.items():
    opt.append(f'{k}={v}')
ebOptions['cname'] = HOSTNAME
ebOptions['envvars'] = '"%s"' % ','.join(opt)

opt = []
for k, v in ebOptions.items():
    opt.append(f'--{k} {v}')

print(f'eb create {HOSTNAME} %s ' % ' '.join(opt))
```

 Execute it as shown below. The script creates the command to type in order to create an Elastic Beanstalk that has:

- one EC2 instance minimum and three EC2 instances maximum (see `ebOptions` in the Python code above).
- the instance profile and service role are the ones that are used by default (see `ebOptions` in the Python code above) therefore you can leave it like this or remove `instance_profile`  `service-role`.
- the Elastic Load Balancer (ELB) is of type application, as necessary for this type of deployment (see `ebOptions` in the Python code above).
- a very small EC2 instance type `t2.nano` will be used (see `ebOptions` in the Python code above).
- the name of your team will be used as the name of the environment (see command below).

The final hostname that Elastic Beanstalk is creating will be `team<YOUR-TEAM-NUMBER>.eu-south-2.elasticbeanstalk.com` that host name needs to be unique. We suggest you to use team and two digits of your team number for this lab session.

The output of the command is extremely long, scroll to the right inside the box below or see the output in your terminal.

```bash
_$ cd .houskeeping/elasticbeanstalk
_$ python ../scripts/ebcreate.py ../../aws.env team<YOUR-TEAM-NUMBER>
eb create team<YOUR-TEAM-NUMBER> --min-instances 1 --max-instances 3 --instance_profile aws-elasticbeanstalk-ec2-role --service-role aws-elasticbeanstalk-service-role --elb-type application --instance-types t2.nano --cname team<YOUR-TEAM-NUMBER> --envvars "DJANGO_DEBUG=True,DJANGO_ALLOWED_HOSTS=0.0.0.0:127.0.0.1:localhost:team<YOUR-TEAM-NUMBER>.eu-south-2.elasticbeanstalk.com,DJANGO_SECRET_KEY=-lm+)b44uap8!0-^1w9&2zokys(47)8u698=dy0mb&6@4ee-hh,DJANGO_LOGLEVEL=info,CCBDA_SIGNUP_TABLE=ccbda-signup-table,DB_NAME=ccbdadb,DB_USER=ccbdauser,DB_PASSWORD=ccbdapassword,DB_PORT=5432,DATABASE=postgresql,AWS_REGION=eu-south-2,AWS_ACCESS_KEY_ID=ASI......ORM,AWS_SECRET_ACCESS_KEY=SwJu.....9XpmR
```

There is just one final thing to do before we issue the command above. Create a file named inside the `elasticbeanstalk` folder. Make sure you change `<aws-registry-id>` by the actual ID. This file informs AWS Elastic Beanstalk from which repository it needs to pull the Docker immage to install on each AWS EC2 instance.

```json
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "<aws-registry-id>.dkr.ecr.eu-south-2.amazonaws.com/django-webapp-docker-repo:v1.0.1"
  },
  "Ports": [
    {
      "ContainerPort": 8000
    }
  ]
}
```

Before proceeding, please make sure that the `aws-elasticbeanstalk-ec2-role` role includes the following permissions, otherwise you'll find errors while deploying the elasticbeanstalk and docker container.

- AmazonEC2ContainerRegistryReadOnly
- AWSElasticBeanstalkMulticontainerDocker
- AWSElasticBeanstalkWebTier
- AWSElasticBeanstalkWorkerTier

In Unix, you can use the back quotes to execute the text produced by the script above. If you are using windows copy and paste in the command line the output of the Python script. In Windows, you'll need to copy and paste the output text of the script.

```bash
_$ cd .houskeeping/elasticbeanstalk
_$ `python ../scripts/ebcreate.py ../../aws.env team<YOUR-TEAM-NUMBER>`
Creating application version archive "app-251105_190630392746".
Uploading django-webapp-eb/app-251105_190630392746.zip to S3. This may take a while.
Upload Complete.
Environment details for: team<YOUR-TEAM-NUMBER>
  Application name: django-webapp-eb
  Region: eu-south-2
  Deployed Version: app-251105_190630392746
  Environment ID: e-ffciczykmy
  Platform: arn:aws:elasticbeanstalk:eu-south-2::platform/Docker running on 64bit Amazon Linux 2023/4.7.4
  Tier: WebServer-Standard-1.0
  CNAME: team<YOUR-TEAM-NUMBER>.eu-south-2.elasticbeanstalk.com
  Updated: 2025-11-05 18:06:33.102000+00:00
Printing Status:
2026-03-19 14:50:27    INFO    createEnvironment is starting.
2026-03-19 14:50:28    INFO    Using elasticbeanstalk-eu-south-2-<aws-registry-id> as Amazon S3 storage bucket for environment data.
2026-03-19 14:50:49    INFO    Created security group named: sg-0b7beef319967146f
2026-03-19 14:51:05    INFO    Created target group named: arn:aws:elasticloadbalancing:eu-south-2:<aws-registry-id>:targetgroup/awseb-AWSEB-BZUZMCTWTRWQ/9862edfd7688018f
......
2026-03-19 14:54:30    INFO    Application available at team<YOUR-TEAM-NUMBER>.eu-south-2.elasticbeanstalk.com.
2026-03-19 14:54:31    INFO    Successfully launched environment: team<YOUR-TEAM-NUMBER>
```
If you have followed all the steps above you shall have now a web application deployed and accesible. It will take a few minutes until you are able to read `Successfully launched environment`.

You can use the `eb` command to query and interact with the Elastic Beanstalk environment.

```bash
_$ eb use team<YOUR-TEAM-NUMBER>
_$ eb printenv
 Environment Variables:
     AWS_ACCESS_KEY_ID = *****
     AWS_REGION = eu-south-2
     AWS_DEFAULT_REGION= eu-south-2
     AWS_SECRET_ACCESS_KEY = *****
     CCBDA_SIGNUP_TABLE = ccbda-signup-table
     DATABASE = postgresql
     DB_NAME = ccbdadb
     DB_PASSWORD = ccbdapassword
     DB_PORT = 5432
     DB_USER = ccbdauser
     DJANGO_ALLOWED_HOSTS = 0.0.0.0:127.0.0.1:localhost:team<YOUR-TEAM-NUMBER>.eu-south-2.elasticbeanstalk.com
     DJANGO_DEBUG = True
     DJANGO_LOGLEVEL = info
     DJANGO_SECRET_KEY = -lm+)b44uap8!0-^1w9&2zokys(47)8u698=dy0mb&6@4ee-hh
```

To visit the web application using your browser type:

```bash
_$ eb open
```

Probably you'll see that the application is not yet working correctly. You can check the AWS Elasticbeanstalk console and see that the web application environment is not healthy.

<img alt="Lab06-unhealthy.png" src="images/Lab05-unhealthy.png" width="50%"/>

Connect to the running EC2 instance by using `eb ssh`. You shall then be connected to the EC2 instance using the user **ec2-user** as shown in the prompt  `[ec2-user@ip-172-31-9-174 ~]$`. To issue docker commands you need to connect as **root** and that is what `sudo bash` does, and you'll see it reflected in the prompt `[root@ip-172-31-9-174 ec2-user]`. 

The command `docker ps` shows the Docker containers currently working in that AWS EC2 instance. We want to verify that the container can connect to the PostGreSQL database engine and we type `docker exec -t <CONTAINER-NAME> python manage.py dbshell` which shall respond with a database prompt `ccbdadb=>`. For the moment it takes a few minutes, when it shall be almost immediate, and returns an error: *Is the server running on that host and accepting TCP/IP connections?*

```bash
_$ cd .housekeeping/elasticbeanstalk
_$ eb ssh
INFO: Running ssh -i /Users/angeltoribio/.ssh/aws-eb -o IdentitiesOnly yes ec2-user@44.193.0.196
  _____ _           _   _      ____                       _        _ _
 | ____| | __   ___| |_(_) ___| __ )  ___  __ _ _ __  ___| |_ __ _| | | __
 |  _| | |/ _ \/ __| __| |/ __|  _ \ / _ \/ _\ | '_ \/ __| __/ _\ | | |/ /
 | |___| | (_| \__ \ |_| | (__| |_) |  __/ (_| | | | \__ \ || (_| | |   <
 |_____|_|\__,_|___/\__|_|\___|____/ \___|\__,_|_| |_|___/\__\__,_|_|_|\_\

 Amazon Linux 2023 AMI

 This EC2 instance is managed by AWS Elastic Beanstalk. Changes made via SSH
 WILL BE LOST if the instance is replaced by auto-scaling. For more information
 on customizing your Elastic Beanstalk environment, see our documentation here:
 http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/customize-containers-ec2.html

   ,     #_
   ~\_  ####_        Amazon Linux 2023
  ~~  \_#####\
  ~~     \###|
  ~~       \#/ ___   https://aws.amazon.com/linux/amazon-linux-2023
   ~~       V~' '->
    ~~~         /
      ~~._.   _/
         _/ _/
       _/m/'
Last login: Sun Mar 30 10:10:33 2025 from 91.134.180.105
[ec2-user@ip-172-31-9-174 ~]$ sudo bash
[root@ip-172-31-9-174 ec2-user]# docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS          PORTS      NAMES
3a8f275f4f77   2a4a23d3dfbb   "gunicorn --bind 0.0…"   25 minutes ago   Up 25 minutes   8000/tcp   blissful_wu
[root@ip-172-31-9-174 ec2-user]# docker exec -t blissful_wu python manage.py dbshell
psql: error: connection to server at "database-lab2.<YOUR-DB-INSTANCE-ID>.eu-south-2.rds.amazonaws.com" (172.31.69.44), port 5432 failed: Connection timed out
        Is the server running on that host and accepting TCP/IP connections?
CommandError: "psql -U ccbdauser -h database-lab2.<YOUR-DB-INSTANCE-ID>.eu-south-2.rds.amazonaws.com -p 5432 ccbdadb" returned non-zero exit status 2.
```

A connectivity problem seems to be happening. Both AWS RDS and AWS Elasticbeanstalk use class B private IP address inside the only VPC that we have. If you check again the AWS RDS security group, it only allows traffic inside its security group. We have then two options:

- include the Elasticbeanstalk environment into the same AWS RDS instance security group
- add a new rule, as we did before to grant access to the laptop. This time the rule shall allow traffic from the 172.16.0.0/12 CIDR.

The second option is easier to apply. Once it's applied, the connection between the AWS EC2 instance and the AWS RDS engine will be possible and the web application will work correctly.

```bash
[root@ip-172-31-9-174 ec2-user]# docker exec -t blissful_wu python manage.py dbshell
psql (15.12 (Debian 15.12-0+deb12u2), server 17.2)
WARNING: psql major version 15, server major version 17.
         Some psql features might not work.
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

ccbdadb=> 
```

Go to the AWS S3 console and see that it there is a new bucket named `elasticbeanstalk-eu-south-2-<aws-account-id>`. Go to the `django-webapp-eb` folder and download the lastest zip file. Uncompress the zip file.

> :question: **Question 5**. What have you found on the zip file? Why do you think it is like that?.

> :question: **Question 6**. Open the AWS EC2 console and check how many instances are running and how many AWS ELB instances. Share your thoughts.

> :question: **Question 7**. Terminate one of the AWS EC2 instances using the AWS EC2 console. Is the web app responding now?  Why?

> :question: **Question 8**. Wait three minutes. What happens? Is the web app responding now?  Why? What do you expect to happen?

Finish the execution of the AWS Elastic Beanstalk environment.

```bash
_$ cd .housekeeping/elasticbeanstalk
_$ eb terminate
The environment "team<YOUR-TEAM-NUMBER>" and all associated instances will be terminated.
To confirm, type the environment name: team<YOUR-TEAM-NUMBER>
2026-03-24 18:23:23    INFO    terminateEnvironment is starting.
2026-03-24 18:23:23    INFO    Validating environment's EC2 instances have termination protection disabled before performing termination.
2026-03-24 18:23:23    INFO    Finished validating environment's EC2 instances for termination protection.
....
2026-03-24 18:25:43    INFO    Deleted security group named: awseb-e-gcmgtmhupr-stack-AWSEBSecurityGroup-gjEZoswAShaF
2026-03-24 18:25:43    INFO    Deleted security group named: sg-0ea7bdd8c119da953
2026-03-24 18:25:45    INFO    Deleting SNS topic for environment team<YOUR-TEAM-NUMBER>.
2026-03-24 18:25:46    INFO    terminateEnvironment completed successfully.
```



## How to submit this assignment:

> :question: **Question 9**: Draw a diagram of the current deployment of the web app using a tool such as [Draw.io](https://www.drawio.com/blog/aws-diagrams)

> :question: **Question 10**: Assess the current version of the web application against each of the twelve factor application.

> :question: **Question 11**: How long have you been working on this session? What have been the main
difficulties that you have faced and how have you solved them? Add your answers to `README.md`.

> :question: **Question 12**: Using the AWS Billing and Cost Management Service, access the "Cost Explorer" and capture the cost of last week Using the "Dimension" "Service" where you can see how much did you spend to complete the session in total and per service.

Make sure that you have updated your local GitHub repository (using the git commands add, commit, and push) with all the files generated during this session.

Before the deadline, all team members shall push their responses to their private https://github.com/CCBDA-UPC/2025_1-5-xx repository.

Add all the web application files to your repository and comment what you think is relevant in your session's *README.md*.


