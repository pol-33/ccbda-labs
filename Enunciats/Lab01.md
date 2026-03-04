# Lab Session #1: Your Cloud Knowledge Toolbox

This session is designed to help you practice and solidify the foundational knowledge required for the rest of the course. By completing the tasks below, you’ll set yourself up for success in future labs.

> [!important]
> Please submit your Github user ID as soon as posible using [this Google form](https://forms.gle/9p1CCpdKPHEYSQud7). 
> You **must** use your UPC credentials to log into the Google form. 
> The Github user ID will be used to grant you access to a Github repository that you'll use to submit the results of this and the future laboratory sessions.

## Lab Tasks Overview

- [**Task 1.1: Review the foundations: Git, Markdown, Python**](#Task11)
- [**Task 1.2: Learning About the AWS Cloud**](#Task12)  
- [**Task 1.3: Install Python and Set Up Your Development Environment**](#Task13)  
- [**Task 1.4: Write a Python Program with the `random` Library**](#Task14)  
- [**Task 1.5: Using Git to submit your work**](#Task15)

<a id="Task11" />

## Task 1.1: Review the foundations: Git, Markdown, Python

One of the objectives of this initial lab session is to ensure that all participants are **aligned with a shared foundational understanding** of **Git**, **Markdown**, and **Python**. Establishing this common baseline will help support a smooth and effective learning experience throughout the course.

Please review the following hands-on guides to confirm your familiarity with the required tools and concepts. If any of the topics are unfamiliar, you are strongly encouraged to complete the exercises before continuing with the course.

### Hands-On Guides

- Hands-on 1: [Git and GitHub Quick Start](https://github.com/CCBDA-UPC/Cloud-Computing-QuickStart/blob/master/Git-Github-Quick-Start.md)  
- Hands-on 2: [Markdown Syntax](https://github.com/CCBDA-UPC/Cloud-Computing-QuickStart/blob/master/Quick-Start-Markdown.md)  
- Hands-on 3: [Python Quick Start](https://github.com/CCBDA-UPC/Cloud-Computing-QuickStart/blob/master/Python-Quick-Start.md)  
- Hands-on 4: [Python Development Environment Quick Start](https://github.com/CCBDA-UPC/Cloud-Computing-QuickStart/blob/master/Python-Development-Environment-Quick-Start.md)


<a id="Task12" />

## Task 1.2: Learning About the AWS Cloud

Students enrolled in the ["**Cloud Computing and Big Data Analytics**"](https://ccbda-upc.github.io/) course have access to the [**AWS Academy**](https://aws.amazon.com/training/awsacademy/), which includes the [**AWS Academy Cloud Foundations**](https://awsacademy.instructure.com/courses/134981) course that is designed for learners seeking a **broad understanding of cloud computing concepts**, independent of specific technical roles. It offers a comprehensive overview of:

- Cloud concepts  
- Core AWS services  
- Security and compliance  
- Cloud architecture  
- Pricing models and support options  

The course also helps prepare students for the [**AWS Certified Cloud Practitioner**](https://aws.amazon.com/certification/certified-cloud-practitioner/) exam.


### Learning materials

To begin building a solid foundation, complete the following modules and submit the corresponding knowledge checks:

- **Module 1** – Cloud Concepts Overview  
- **Module 2** – Cloud Economics and Billing
- **Module 3** - AWS Global Infrastructure Overview
- **Module 4 – AWS Cloud Security**
  > :question: **Question 1:** Include screenshots of key steps and briefly explain what you learned or observed
  
  > :test_tube: **Laboratory 1:** *Introduction to AWS IAM*  
  
  
> [!Important]
> Each student must **individually** complete the AWS Academy knowledge checks as part of the course requirements.
> 
> Complete only the modules and laboratories specified below.

<a id="Task13" />

## Task 1.3: Install Python and Set Up Your Development Environment

Install [PyCharm](https://www.jetbrains.com/pycharm/) – a popular Python IDE. It supports debugging, version control, virtual environments, and more. 

> [!tip]
> PyCharm Professional is **free for students** – [download the application here](https://www.jetbrains.com/shop/download/PC/2025200). To confirm and accept your All Products Pack license invitation, please click on   [https://account.jetbrains.com/a/0558yrx4](https://account.jetbrains.com/a/0558yrx4). The invitation link requires the use of a `@estudiantat.upc.edu` email account.

1. Create a new PyCharm project named `Lab1`.
2. Configure a [Python virtual environment](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html) inside the folder `venv`.
3. Activate the virtual environment and install any necessary packages using `pip`.

<a id="Task14" />

## Task 1.4: Write a Python Program with the `random` Library

Create a Python script named `Lab1.guessnumber.py` that does the following:

- Generates a random number between 1 and 20.
- Prompts the user to guess the number.
- Tells the user whether their guess is too high or too low.
- Ends the game when the correct number is guessed.

> [!Tip]
> Use this session to gain **debugging Practice in PyCharm**.
> Get comfortable using the built-in debugger. Create a run configuration, set breakpoints, and inspect variable values. Your future lab sessions will take advantage on this skill.


![](./images/Lab01-PyCharmEditConfig.jpg)   
![](./images/Lab01-PyCharmDebugConfig.png)

> :question: **Question 3:** Include screenshots of key steps and briefly explain what you learned or observed.

<a id="Task15" />

## Task 1.5: Using Git to submit your work

Use your assigned **private GitHub repository**: `https://github.com/CCBDA-UPC/2026_1-1-xx` (Replace `xx` with your actual group identifier.)

```bash
echo "# 2026-1-xx" >> README.md
git init
git add README.md Lab1.guessnumber.py
git commit -m "First commit"
git remote add origin https://github.com/CCBDA-UPC/2026_1-1-xx.git
git push -u origin master
```

> [!Note]
> You are encouraged to initially use Git from the command line. Once familiar, feel free to manage Git through PyCharm.


## How to submit Your Assignment

> :question: **Question 4:** How much time did you spend on this session?  
  
> :question: **Question 5:** What challenges did you encounter, and how did you overcome them?

Push your updated repository to GitHub https://github.com/CCBDA-UPC/2026_1-1-xx **before the deadline**, including:

- `README.md` with all your responses and documentation
- Your Python script (`Lab1.guessnumber.py`)
- Any screenshots or files required by the tasks