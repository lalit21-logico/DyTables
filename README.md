# DyTables(Walkover Assignment) _Final Project_
**A Web Application which helps the users to create a Dynamic Tables**
---

> ## Techstack
> + [Django](https://www.djangoproject.com) (**A high-level Python web framework**)
> + [MongoDB](https://www.mongodb.com) (**Database**)
> + [Jenkins](https://www.jenkins.io) (**an open source automation server**)
> + [AWS](https://aws.amazon.com) (**Cloud platform for deployment**)
> + [Python](https://www.python.org) (**Programming Language**)
> + [authO](https://auth0.com) (**Authorization Platform**)
> + [Bootstrap](https://getbootstrap.com) (**CSS Framework**)
> + [HTML/CSS](https://www.w3schools.com/html/) (**Core technologies for building webpages**)
> + [Balsamiq design of all pages](https://balsamiq.cloud/sali2n2/p358eks/r4B13) (**User interface design tool**)

## This is how the table looks like
_**Note: Here you can make a coloumn a primary key**_

| Number | String    | Boolean | Email          | Datetime   |
| ----   | :-------: | :----:  | :----:         |      ----: |
| 1      | Dytables  | True    | abc@yandex.com | 25/01/2022 |

## Setup

_**Note : However For running this project another python file is required which is secureCred.py**_

_**Note : Create the sucureCred.py file under the project directory which is DyTables/secureCred.py**_

## secureCred.py should contain the varialbles listed below

AUTH_SEC = "provide auth0 AuthUrl"

HOST_URL = 'MongoDB connection URL'

**Installation**

> ``` python
> pip install -r requirements.text
> ```

_**Note: Before running the project install all the required files**_

_**Note: Change debug False to True inside settings.py (for running in localhost)**_

## Use this command to run the project

**Run this following commands inside root directory**

> ``` python
> python manage.py makemigrations
> python manage.py migrate
> ```

> ```python 
> python manage.py runserver
>```

## Team Intro (2 Members)
**Lalit Patidar(Contribution)**: Backend,Deployment,Frontend,Bug Fixing

**Vivek Choudhary(Contribution)** : Research,Frontend,Backend,Debugging
### Our team comprises of 2 members so far we have reached this step for the final project submission. Although this was not easy for us to reach at the final level. We decided to make this project using python web framework Django as it is convinient and comfortable for us to make a project in Django. Its all are harwork and process which had led us to complete all the six week assignments and finally getting a chance for the project completion. We thank Walkover Web Solution for giving us a chance to make this project and showcase our skills.  

## User Stories

>As a User of Dytables Web Application

## Balsamiq design of all pages

**Landing Page**

![alt text](https://github.com/lalit21-logico/DyTables/blob/master/static/images/DyTables.png)

**auth0 (Login Page)**

![alt text](https://github.com/lalit21-logico/DyTables/blob/master/static/images/Login.png)

**Create New tables**

![alt text](https://github.com/lalit21-logico/DyTables/blob/master/static/images/Create%20new.png)

**My Tables**

![alt text](https://github.com/lalit21-logico/DyTables/blob/master/static/images/My%20Tables.png)

**After adding the Values in the table**

![alt text](https://github.com/lalit21-logico/DyTables/blob/master/static/images/Student.png)

**Audit History**

![alt_text](https://github.com/lalit21-logico/DyTables/blob/master/static/images/My%20Tables.png)
