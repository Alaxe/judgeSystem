# judgeSystem
A python/django based system for testing c/c++ solutions to algoritmic problems

##What it does now:
* Basic Login/register funtionality
* Task/test editing
* Testing  solutions
* A simple blog
* Searching by tags

##Required software:
* Python 3.\*
* Python modules: view requirements.txt
* g++ compiler
* postgreSQL
* rabbitmq

##How to install:
0. Clone the repository `git clone https://github.com/Alaxe/judgesystem.git`
1. Setup database - you have a few options
    * install postgreSQL `pacman -S postgresql` on Arch Linux
    * setup database and user
    ```
    sudo su postgres
    createuser admin -P
    cretadb judgeSystemDB -U admin
    ```
2. Install rabbitmq `pacman -S rabbitmq` on Arch Linux
3. Setup settings 
    * create variables in judgeSystem/sens.py
        * EMAIL - used for account confirmation
        * EMAIL_PASSWORD - password for that account
    * judgeSystem/settings.py
        * SITE_HOST - used for some links
        * Email backend and server
        * TIME_ZONE
4. run setup.py

How to run:
  * Actual server : python manage.py runserver (you can add url parameters)
  * Celery server : celery -A judgeSystem (you can mess with the parameters if you want) 
