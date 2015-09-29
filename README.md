# judgeSystem
A python/django based system for testing c/c++ solutions to algoritmic problems

What it does now:
  * Basic Login/register funtionality
  * Task/test editing
  * Grading solutions (no interactive checkers)
  * Submiting solutions
  * A simple blog
  * Searching by tags

What it is aiming to do:
  * Competitions

Required software:
  * Python 3.\*
  * Python moules: view requirements.txt
  * g++ compiler
  * Database
    * postgreSQL - default, a bit harder to install. Fully tested
    * SQLlite - easy to install, but does not support concurency - NOT TESTED MUCH
    * Others - shouldn't be hard to setup but you'll need to change a bit settings.py
  * message broker for celery
    * rabbitmq
    * django's default broker - a bit slower, but it should come installed

How to install:
  0. Clone the repository `git clone https://github.com/Alaxe/judgesystem.git`
  1. Setup database - you have a few options
    * For sqlite change the DATABASES from judgeSystem/settings.py
    * For postgresql create the database/user specified in DATABASES
    * For other databases visit [Django documentation](https://docs.djangoproject.com/en/1.8/ref/databases/)
  2. Setup message broker - again options
    * For rabbitmq - just install it
    * For django default broker (slower) uncoment the BROKER_URL line in judgeSystem/cellery.py
  3. Setup settings 
    * create variables in judgeSystem/sens.py
      * EMAIL - used for account confirmation
      * EMAIL_PASSWORD - password for that account
      * SITE_HOST - used for some links
    * judgeSystem/settings.py
      * Email backend and server
      * TIME_ZONE
  4. run setup.py What it does:
    * Installs the isolate submodule [Link](https://github.com/Alaxe/isolate)
    * Copies the sandbox to the correct folder
    * Installs required python modules
    * Creates the database

How to run:
  * Actual server : python manage.py runserver (you can add url parameters
  * Celery server : celery -A judgeSystem (you can mess with the parameters if you want) 
