# 2026-1-16
## Team Members
- Daniel Antonia Galleguillos
- Pol Plana

## Task 1: Continue Learning About the AWS Cloud
### ❓ Question 1: Include screenshots of key steps and briefly explain what you learned or observed
In Lab 1: Introduction to AWS IAM, we practiced how to work with users, groups, and permissions in AWS. The goal was to understand how IAM controls access depending on the role of each user.

![lab4TaskOverview.png](lab4TaskOverview.png)

First, we explored the pre-created users (user-1, user-2, and user-3) and the groups (EC2-Admin, EC2-Support, and S3-Support). At the beginning, the users had no permissions. We learned that permissions can be given through groups, and each group has policies attached. We also discovered the difference between Managed Policies, which are created by AWS and easy to reuse, and Inline Policies, which are only for one group or user.

Next, we added the users to their groups. We placed user-1 in S3-Support with read-only access to S3, user-2 in EC2-Support with read-only access to EC2, and user-3 in EC2-Admin with more control, including starting and stopping instances. This showed us how permissions are inherited from groups.

![lab4confirmacionDetencionInstancia.png](lab4confirmacionDetencionInstancia.png)


![lab4InstanciaDetenida.png](lab4InstanciaDetenida.png)

Finally, we tested the accounts by logging in with the IAM sign-in URL. The results matched what we expected: user-1 could only see S3, user-2 could only view EC2, and with user-3 we actually stopped the instance (we have the screenshots).

![lab4Completado.png](lab4Completado.png)

But more than the grade, what really mattered was the experience. Now we know and understand better how permissions work in AWS.


### ❓ Question 2: Include screenshots of key steps and briefly explain what you learned or observed.
In this task, we continued our learning journey with AWS by completing courses 5 from the AWS Academy Cloud Foundations series. This course focuses on Networking and Content Delivery. We learned about the fundamental concepts of networking in the cloud, including Virtual Private Clouds (VPCs), subnets, route tables, and internet gateways. The course also covered how to set up and configure these components to create a secure and efficient network architecture in AWS.

We observed how VPCs allow us to isolate our cloud resources and control their communication with each other and the internet. We also learned about the importance of security groups and network access control lists (ACLs) in protecting our resources from unauthorized access. Some of this concepts were a bit complex, but we took our time to understand them and reviewed the material as needed. Understanding the different components of a VPC and how they interact with each other has been the most difficult part of the task, but we managed to grasp the concepts through the course material and additional research.

In the screenshots below, you can see some of the key steps we took during the course, including the course overview when starting the laboratory environment, VPC configuration in AWS, and an example of launching an EC2 instance within our own VPC.
![lab5enunciat.png](lab5enunciat.png)
![lab5vpcConfig.png](lab5vpcConfig.png)
![lab5ec2Result.png](lab5ec2Result.png)
## Task 3: Write a Python Program with the random Library
### ❓ Question 3: Include screenshots of key steps and briefly explain what you learned or observed.
We learned the key basics of Python programming, including how to set up a Python development environment using PyCharm, write a simple Python program that utilizes the `random` library to generate random numbers, and run the program within the IDE. In our case, Python is not our first programming language, we needed to refresh its syntax and conventions, which was a good exercise to strengthen our adaptability. This exercise helped us understand the syntax and structure of Python code, as well as how to use libraries to enhance functionality.

In the screenshots below, you can see the configured PyCharm interface with the Python program that generates a random number between 1 and 20. It represents the most key step as it can be seen how we have coded the program and executed it to test the output.
![pycharmPythonProgram.png](pycharmPythonProgram.png)

## Submit Your Assignment
### ❓ Question 4: How much time did you spend on this session?
To complete the tasks in this session, we spent approximately 4 hours. This time was divided between learning about AWS Cloud services (the AWS courses 5 and 6 took approximately 2 hours in total), setting up the Python development environment, writing the Python program, and answering the questions in this assignment.

### ❓ Question 5: What challenges did you encounter, and how did you overcome them?
During the laboratory session, we encountered a few challenges, but we managed to overcome them successfully.

The first challenge was understanding some of the more complex concepts in the AWS courses, particularly in course 5, which covered networking and VPC concepts. To overcome this, we took our time to review the material, and checked the concepts in external sources to conceive a clearer understanding.

The second challenge was recalling Python syntax and conventions, as it is not our first programming language. We overcame this by referring to Python documentation in this course and examples online to refresh our memory, and succeed in this session's task. 

Overall, we worked well and got along as a team, supporting each other through the challenges and ensuring that we completed the tasks successfully.
