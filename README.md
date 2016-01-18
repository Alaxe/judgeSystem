# judgeSystem
A python/django based system for testing c/c++ solutions to algoritmic problems

##What it does now:
* Basic Login/register funtionality
* Task/test editing
* Testing solutions
* A simple blog
* Searching by tags

##Required software:
* Python 3 (tested only with 3.5)
* Python modules: view requirements.txt
* g++ compiler
* postgreSQL
* rabbitmq

##How to install:
0. Clone the repository `git clone https://github.com/Alaxe/judgesystem.git`
1. Setup database - you have a few options
    * install postgreSQL `pacman -S postgresql` on Arch Linux
    * setup database and user
2. Install rabbitmq `pacman -S rabbitmq` on Arch Linux
3. Setup settings 
    * create variables in judgeSystem/sens.py
        * `EMAIL_HOST_USER` - used for account confirmation
        * `EMAIL_HOST_PASSWORD` - password for that account
        * `RECAPTCHA_PRIVATE_KEY` - the private key for recaptcha
    * judgeSystem/settings.py
        * `SITE_HOST` - used for some links
        * Email backend and server (default is gmail)
        * `TIME_ZONE` - default one is different from Easter Europe's
        * `RECAPTCHA_PUBLIC_KEY` - the public key for recaptcha
4. run `sudo python setup.py` (as root)

##How to run:
  * Web server: `python manage.py runserver` (you can a add `url:port` pair as a
    parameter)
  * Celery server (as root): `sudo -- sh -c  'export C_FORCE_ROOT="true"; celery
    -A judgeSystem worker`
