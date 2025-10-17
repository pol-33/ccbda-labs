# 2026_1-4-19
## Team Members
- Mariam Delgado
- Pol Plana

## Task 4.3: Test the web app locally
### ❓ Question 1: Create a screen capture of your DynamoDB table with the data of the new leads. Add your thoughts on the above tasks.

The screenshot below shows the DynamoDB table ccbda-signup-table populated with two leads (two items using email as the partition key), created by submitting the newsletter form in the local Django app (http://127.0.0.1:8000/).
![DynamoDB Table](./images/dynamoDBstatus.png)

As we had created the table in us-east-1, we configured AWS CLI default profile to us-east-1. Then, we set up the project .env (making sure we had the proper .gitignore configuration). We also created and activated a fresh Python 3.13 virtualenv, installed requirements, ran migrations and started the dev server. Finally, we submitted two test sign-ups and confirmed items appeared in DynamoDB.

We think that it is important to use the least-privilege policy for the IAM created user, lab4_user (FullAccess to DynamoDB and AWS Simple Notification Service, as this are the only things to be used in this lab session). It was also important to check that we never commit .env (verified it’s gitignored). We say how if a certain policy is not activated, an AccessDenied errors occur, ensuring a proper permissions management.


## Task 4.4: Use AWS Simple Notification Service in your web app
### ❓ Question 2: Has everything gone alright? Share your thoughts on the task developed above.


## Task 4.5: Configure Docker
### ❓ Question 3: Has everything gone alright? Share your thoughts on the task developed above.


## Task 4.6: Deploy the target web app
### ❓ Question 4: Share your thoughts on the task developed above.


## Task 4.7: Analisys of the twelve-factor app methodology
### ❓ Question 5: For the above lab session, explain, one by one, how each factor is taken into consideration, or what would you change or add to comply with each factor


## Submit Your Assignment
### ❓ Question 6: How much time did you spend on this session?


### ❓ Question 7: What challenges did you encounter, and how did you overcome them?


