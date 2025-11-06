# 2026_1-5-15
## Team Members
- Álvaro Rodríguez
- Pol Plana

# Task 5.1: AWS Relational Database Service
## ❓ Question 1: Explain why you will not keep that access open on a production system. How can you do manual maintenance on the database using SQL commands, when necessary?

We should not keep public access open on a production database for several security reasons:

1. **Security Risk**: Opening the database to public internet access (0.0.0.0/0) exposes it to potential attacks, brute force attempts, and unauthorized access from anywhere in the world.

2. **Attack Surface**: Every publicly accessible service increases the attack surface of our infrastructure, making it vulnerable to SQL injection attacks, DDoS attacks, and other malicious activities.

**How to do manual maintenance when necessary:** 

To perform manual maintenance on the database while keeping it secure:

1. **Use VPN**: Set up a VPN connection to the AWS VPC and access the database through the private network.

2. **Use a Bastion Host**: Set up an EC2 instance in the same VPC as the RDS instance and SSH into it, then connect to the database from there.

3. **Temporary Access (not recommendable)**: Temporarily add your current IP address to the security group, perform maintenance, then immediately remove it.


## ❓ Question 2: Using the above configuration file, what steps will you follow to have the web application running in your local Docker use the AWS RDS database engine?

To run the web application in local Docker using the AWS RDS database engine, we followed these steps:

1. **Build the Docker image** with a version tag:
   ```bash
   docker build -t django-docker:v1.0.0 .
   ```

2. **Ensured the `aws.env` file is properly configured** with the AWS RDS connection details.

3. **Verified RDS security group** allows inbound traffic on port 5432 from our laptop's IP address.

4. **Initialize the database** (first time only) by running the container interactively:
   ```bash
   docker run --env-file aws.env -it django-docker:v1.0.0 /bin/bash
   ```
   Then inside the container, create the database and user:
   ```bash
   cat > init_db.sql << 'EOF'
    CREATE DATABASE ccbdadb;
    CREATE USER ccbdauser
        WITH ENCRYPTED PASSWORD 'ccbdapassword'
        createdb
        createrole
        bypassrls;
    ALTER USER ccbdauser SET TimeZone = utc;
    ALTER DATABASE ccbdadb OWNER TO ccbdauser;
    EOF
   ```
   
    ```bash
   psql --host=$DB_HOST --port=$DB_PORT --username=postgres < init_db.sql
    ```

   Where `init_db.sql` contains the SQL commands to create the database and user.

5. **Run Django migrations** to create the necessary tables in the RDS database:
   ```bash
   python manage.py migrate
   ```

6. **Started the Docker container** with the web application:
   ```bash
   docker run --env-file aws.env -p 8000:8000 django-docker:v1.0.0
   ```

7. **Access the web application** at `http://localhost:8000`


**Connecting to the Database with PyCharm:**

To properly connect in PyCharm:
- **Host**: Your RDS endpoint (e.g., `database-lab.xxxxxxx.us-east-1.rds.amazonaws.com`)
- **Port**: `5432`
- **Database**: `ccbdadb`
- **User**: `ccbdauser`
- **Password**: `ccbdapassword`

After connecting to `ccbdadb`, you'll see all Django tables under `public` → `Tables`. If you connect to the `postgres` database instead, you'll only see server-level objects like roles, but not the application tables.


## ❓ Question 3: Explain what does the code in the box above. How can you execute it inside the Docker container?

The code in the box above performs the following operations to initialize the PostgreSQL database on AWS RDS:

1. **CREATE DATABASE ccbdadb;** - Creates a new database named `ccbdadb` that will store all the Django application data.

2. **CREATE USER ccbdauser WITH ENCRYPTED PASSWORD 'ccbdapassword' createdb createrole bypassrls;** - Creates a new PostgreSQL user `ccbdauser` with:
   - An encrypted password `ccbdapassword`
   - `createdb` privilege: allows the user to create new databases
   - `createrole` privilege: allows the user to create new roles/users
   - `bypassrls` privilege: allows the user to bypass row-level security policies

3. **ALTER USER ccbdauser SET TimeZone = utc;** - Sets the default timezone for the user to UTC to ensure consistent timestamp handling across the application.

4. **ALTER DATABASE ccbdadb OWNER TO ccbdauser;** - Changes the ownership of the `ccbdadb` database to `ccbdauser`, giving this user full control over the database.

**How to execute it inside the Docker container:**

1. First, enter the Docker container interactively:
   ```bash
   docker run --env-file aws.env -it django-docker:v1.0.0 /bin/bash
   ```

2. Inside the container, create the SQL script file using `cat` with input redirection:
   ```bash
   cat > init_db.sql << 'EOF'
    CREATE DATABASE ccbdadb;
    CREATE USER ccbdauser
        WITH ENCRYPTED PASSWORD 'ccbdapassword'
        createdb
        createrole
        bypassrls;
    ALTER USER ccbdauser SET TimeZone = utc;
    ALTER DATABASE ccbdadb OWNER TO ccbdauser;
    EOF
   ```

3. Execute the SQL script using the `psql` command:
   ```bash
   psql --host=$DB_HOST --port=$DB_PORT --username=postgres < init_db.sql
   ```
   
   The environment variables `$DB_HOST`, `$DB_PORT`, and `$PGPASSWORD` are automatically loaded from the `aws.env` file, which is why `psql` can authenticate and connect to the AWS RDS instance.


## ❓ Question 4: What is the result of "select * FROM django_migrations;"

The result of `SELECT * FROM django_migrations;` shows all the migrations that Django has applied to the database. After running `python manage.py migrate`, the table contains records of all applied migrations.

To execute this query inside the Docker container:

```bash
docker run --env-file aws.env -it django-docker:v1.0.0 /bin/bash
psql --host=$DB_HOST --port=$DB_PORT --username=postgres -d ccbdadb -c "SELECT * FROM django_migrations;"
```

The  output includes migrations from Django's built-in app:

![q4-db-table-query.png](images/q4-db-table-query.png)

Each row in the `django_migrations` table contains:
- `id`: Auto-incrementing primary key
- `app`: The Django app name (e.g., 'auth', 'admin', 'contenttypes', 'sessions')
- `name`: The migration filename (e.g., '0001_initial')
- `applied`: Timestamp when the migration was applied

This table is Django's way of tracking which database schema changes have been applied, ensuring that migrations are only run once and in the correct order. It prevents duplicate migrations and helps maintain database schema consistency across different environments.


# Task 5.2: Task 5.2: Adding the Docker image to AWS ECR
## Some images of the process followed in Task 5.2 and Task 5.3:

Configurating the IAM permissions for the user:
![task5.2-permissions.png](images/task5.2-permissions.png)

Successfully launching the web app:
![task5.3-successful-launch.png](images/task5.3-successful-launch.png)

Accessing the deployed web app and trying the related functionalities:
![task5.3-trying-deployed-version.png](images/task5.3-trying-deployed-version.png)

Accessing the database from the Elastic Beanstalk instance:
![task5.3-correct-access-db.png](images/task5.3-correct-access-db.png)


# Task 5.3: Running Docker Container images on AWS Elastic Beanstalk
## ❓ Question 5. What have you found on the zip file? Why do you think it is like that?.

The zip file contains the **source code of the Django web application**, all the Python files, configuration files, static files, and templates from our project directory.

**Why is it like this?**

Elastic Beanstalk needs to store a snapshot of each application version for version control and rollback purposes. When we run `eb create`, the EB CLI automatically:

1. Packages the current working directory into a zip file
2. Uploads it to an S3 bucket (`elasticbeanstalk-us-east-1-770404291990`)
3. Tags it with a version identifier (e.g., `app-251106_014455933930.zip`)

This allows AWS to track what was deployed, when, and enables us to easily roll back to previous versions if needed.


## ❓ Question 6. Open the AWS EC2 console and check how many instances are running and how many AWS ELB instances. Share your thoughts.
Originally there were three AWS EC2 t3.small instances, but we had to change it in the command because there are no t2.nano instances in the eu-south-2 region.
There is 1 ELB (Elastic Load Balancer) in this environment, but it is distributed across 3 availability zones (eu-south-2a, eu-south-2b, eu-south-2c) to ensure redundancy and high availability.
The number of EC2 instances behind the ELB can scale between the minimum and maximum you configured (--min-instances 1 --max-instances 3) depending on traffic and load.
Additionally, the ELB is internet-facing, which allows external users to access the Django application through its DNS name (awseb--AWSEB-wwvROLDqtk9r-1623737173.eu-south-2.elb.amazonaws.com). This setup, combined with multiple availability zones, ensures that the application remains reachable and responsive, even during deployments or if individual instances fail.


After checking the AWS EC2 console, we found:

**EC2 Instances:**
- **1 EC2 instance running**
  - Instance ID: `i-061dc74cf99353d4e`
  - Instance Type: `t3.small`
  - Name: `team2026-1-5-15`

**Elastic Load Balancers:**
- **1 Application Load Balancer (ALB)**
  - Type: `application`
  - State: `active`
  - Distributed across 6 availability zones in us-east-1

**Thoughts:**

1. **Single Instance Running**: Currently, only 1 EC2 instance is running, even though we configured Elastic Beanstalk with `--min-instances 1 --max-instances 3`. This is the expected behaviour, since the application is not under heavy load, so auto-scaling hasn't triggered additional instances.

2. **Load Balancer Present**: Despite having only 1 EC2 instance, Elastic Beanstalk still created an Application Load Balancer. This is important to ensure:
   - **High availability**: If the instance fails, the load balancer can route traffic to new instances
   - **Auto-scaling**: When demand increases, new instances can be added behind the same load balancer
   - **Health checks**: The load balancer monitors the instance health and can trigger replacements if needed

3. **Multi-AZ Deployment**: The load balancer is configured across 6 availability zones, providing redundancy even though the EC2 instance is in only one zone. This ensures the load balancer itself is highly available.

4. **Cost vs. Reliability Trade-off**: Having a load balancer for a single instance adds cost but provides the infrastructure for automatic scaling and high availability, which is essential for production environments.

![q6-instances.png](images/q6-instances.png)


## ❓ Question 7. Terminate one of the AWS EC2 instances using the AWS EC2 console. Is the web app responding now? Why?
We terminated the only instance that was running. After that, the website stopped allowing navigation between views, and submitting the form returned an error indicating that something had gone wrong. Shortly afterward, a 504 Gateway Timeout occurred, making the interface completely unavailable.

We terminated the running EC2 instance (`i-061dc74cf99353d4e`) using the AWS EC2 console.

What we saw was that the web application stopped responding immediately after terminating the instance.

When we terminated the running EC2 instance (i-061dc74cf99353d4e) through the AWS EC2 console, the web application 
immediately stopped responding because our Elastic Beanstalk environment was configured with only a single instance. 

This meant that by terminating it, we effectively removed the only server capable of running and serving our Django 
application at that moment. Although a load balancer was present, it could not route any traffic because there were no 
healthy backend instances available. As soon as the instance was terminated, the load balancer’s health checks began to 
fail, marking the target as unhealthy. Until Elastic Beanstalk launched a replacement instance and it passed its health 
checks, the application remained unavailable, resulting in a temporary service outage.


## ❓ Question 8. Wait three minutes. What happens? Is the web app responding now? Why? What do you expect to happen?

After about three minutes, the web application started responding again because Elastic Beanstalk automatically replaced 
the terminated EC2 instance. 

When we removed the only running instance, the Auto Scaling Group (ASG) detected that the number of running instances had dropped below the configured minimum 
(--min-instances 1) and launched a new instance to restore the environment. Once this new instance finished initializing, 
passed its health checks, and was registered by the load balancer, the application became available again. This 
self-healing behavior is expected and the desired one: we want Elastic Beanstalk to maintain the desired number of instances 
automatically. However, since our setup only had one instance, there was a short period of downtime during the replacement. 
In a production environment with multiple instances across availability zones, such failures would not cause any visible 
outage in most of the cases.

Once the new instance became fully available and was running, reloading the page restored normal functionality, and the website worked as expected again.

# How to submit this assignment:
## ❓ Question 9: Draw a diagram of the current deployment of the web app using a tool such as Draw.io

## ❓ Question 10: Assess the current version of the web application against each of the twelve factor application.
1. Codebase: We maintain the codebase in Git, allowing us to create branches to facilitate development. Additionally, we generate a build for what would be the production version and push the Docker image to the AWS repository.
2. Dependencies: All dependencies are declared in the requirements.txt file. This allows us to keep track of versions and maintain a clear list of all required packages.
3. Config: We use the settings.py file to configure aspects such as the Python version. Additionally, the aws.env file allows us to manage environment variables for production, keeping them separate from those used in development. 
4. Backing Services: The app relies on external services such as PostgreSQL and AWS S3. Currently, these services are tightly coupled in the configuration (environment variables in aws.env), but they could be easily replaced by changing these variables. This factor is partially satisfied. 
5. Build, Release, Run: This factor is met: we build the Docker image, upload it to AWS, and deploy instances. The ebcreate.py script automates the deployment, but the separation between build and release is not strict, as everything is done in a single step. 
6. Processes: The app runs in stateless processes using Gunicorn, but there are minimal local state dependencies (for example, local logs before being sent to CloudWatch). This could be improved to be fully stateless. 
7. Port Binding: The app runs as a self-contained service, listening on the specified port, while Elastic Beanstalk handles HTTP routing. 
8. Concurrency: Gunicorn handles multiple workers, but automatic scaling depends on Elastic Beanstalk. There is no explicit handling of background tasks outside the web processes. 
9. Disposability: Containers can start and stop quickly, but the reliance on AWS Elastic Beanstalk means they are not fully independent or easily replaceable without some configuration time. 
10. Dev/Prod Parity: The same Docker image built locally is deployed in production, ensuring consistency between environments. 
11. Logs: Logs are collected using eb logs, but there is no continuous streaming or full integration with a centralized logging system like CloudWatch Logs. 
12. Admin Processes: Administrative tasks (DB migrations, Django management commands) are executed manually via SSH or scripts rather than automatically.

## ❓ Question 11: How long have you been working on this session? What have been the main difficulties that you have faced and how have you solved them? Add your answers to README.md.
This session took us approximately nine hours, including the various tasks and writing the assignment. This was mainly due to issues specifying the correct host in different sections or adding a library to the requirements.txt file.