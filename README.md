# 2026_1-3-13
## Team Members
- Alexandra Olivares
- Pol Plana

## Task 1: Expand Your AWS Cloud Knowledge
### ❓ Question 1 [Module 8 – Databases]: Include screenshots of key steps and briefly explain what you learned or observed.
>I learned how to provision a managed database in AWS using RDS, configure networking with subnet groups, and securely connect the database to an EC2-hosted application.
>
>First screenshot: Shows the database creation process, where I selected the Standard create method and chose MySQL as the database engine.
>
>![createDB](img/creardb-mod8.png)
>
>Second screenshot: Displays the DB subnet group configuration, where I defined multiple subnets across different availability zones to ensure high availability and proper network setup.
>
>![createSubG](img/creardb-subGroup.png)

>Third screenshot: Illustrates the creation of an Aurora RDS instance, showcasing the options for selecting the instance type and configuring the database settings.
![aurora](img/AuroraRDSLaunch.png)
>
>Final screenshot: Shows the web interface of the PHP application successfully connected to the RDS database. I was able to view, edit, and add records, confirming that the integration between EC2 and RDS was working correctly.
>
>![muestraDB](img/accesodb-mod8.png)
>
### ❓ Question 2 [Module 9 – Cloud Architecture]: Include screenshots of key steps and briefly explain what you learned or observed.

We consider this module the easiest one of the course, but this doesn't mean it is not as important as the others. In this module, we learned about the pillars of the AWS Well-Architecture Framework, which are essential for designing and operating operational excellent, reliable, secure, performance efficient, cost-effective, and sustainable systems in the cloud. The module consisted on watching a video explaining each pillar in detail, along with best practices and contexts, which helped us understand how to apply these principles when architecting solutions on AWS.

In the image below, we can see the pillars, that include Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, and Sustainability.

![pillars](img/Module9SlideIntro.png)

### ❓ Question 3 [Module 10 – Auto Scaling and Monitoring]: Include screenshots of key steps and briefly explain what you learned or observed.
This is the last module of the course, and I found it very interesting because it focuses on monitoring and auto-scaling, which are crucial for maintaining application performance and reliability in the cloud. It is very intersting how with a small effort, you can set up automatic scaling to handle varying loads, ensuring that your application remains responsive without manual intervention. We used CloudWatch to monitor our application's performance and set up alarms to trigger scaling actions. Then with EC2 Auto Scaling, we configured policies to automatically adjust the number of instances based on demand.

In the image below, you can see a video explaining the load balancing principles, concepts, and use cases.

![Module10Video](img/Module10Video.png)


## Task 2: Extract Images from a Website
### ❓ Question 4: Reflect on the tasks above. What did you find interesting or challenging? Share your thoughts.
>
> Es interesante cómo se puede obtener información de distintas páginas, seleccionando exactamente lo que se desea para analizarlo posteriormente de forma adecuada.
>

## Task 3: Obtain Insights About an Image Using AWS Rekognition
### ❓ Question 5: Share your thoughts about the Rekognition demo. What did you observe? Was anything surprising or particularly useful?

### ❓ Question 6: What differences or similarities did you find between the JSON output and the console demo? Which one provides more usable information, and why?


## Task 4: Get Insights From Website Images Using AWS Rekognition
### ❓ Question 7: What is the goal of your image analysis application? (E.g., detecting objects, filtering inappropriate content, facial recognition, etc.)

### ❓ Question 8: What is the mechanism that you have created to prevent sending the same image to AWS Rekognition more than once?


## Submit Your Assignment
### ❓ Question 9: How much time did you spend on this session?

### ❓ Question 10: What challenges did you encounter, and how did you overcome them?


