# judgeSystem
A python/django based system for testing c/c++ solutions to algoritmic problems

##What it does now:
* Basic Login/register funtionality
* Task/test editing
* Testing solutions
* A simple blog
* Searching by tags

##Required software:
* A linux distribution (tested on Arch and Ubuntu)
* Python 3 (tested only with 3.5)
* Python modules: view requirements.txt
* g++ compiler
* A database (postgresql recommended)
* rabbitmq
* [isolate sandbox][isolate]

##How to install:
1. Clone the repository `git clone https://github.com/Alaxe/judgesystem.git`
2. (Optional) install [virtualenv][virtualenv] ([guide][virtualenv_guide])
3. Setup settings `judgeSystem/settings.py`
    * `EMAIL_<setting_name>` - Used for account confirmation, default server is
        [gmail]
    * `RECAPTCHA_PRIVATE_KEY` and `RECAPTCHA_PUBLIC_KEY` - self explanatory,
      You can get them from [their website][recaptcha]
    * `SITE_HOST` the domain / ip of the server; used for some links
    * `ALLOWED_HOSTS`
    * `SECRET_KEY` 
    * `TIME_ZONE` 

4. Setup database 
    * install it ([guide][postgres_guide] for postgres)
    * Fill in `DATABASE` in `judgeSystem/settings.py`
    * Generate any missing migrations `python manage.py createmigrations`
    * Create the database schema with `python manage.py migrate`
5. Other dependencies
    * Python modules `sudo pip install -r requirements.txt --upgrade`
    * Static files `python manage.py collectstatic`
    * (optinal) create a super user `python manage.py createsuperuser`
4. Install rabbitmq
    * `sudo apt-get install rabbitmq`
    * Start the service `sudo systemctl start rabbitmq-server` and enable it
      `sudo systemctl enable rabbitmq-server` (i.e. make it start on boot)
      **Note:** This assumes that you have systemd. While that's the case with
      newer distros, you may have to use an your disto's init system
5. Install isolate
    * Clone the [repository][isolate] `git clone https://github.com/ioi/isolate`
    * Install `make install` (Has to be run from the repository's directory)
6. (optional) Install a proper web server (you can use the development server,
   which comes with django, but it's not suitable for production) Here's a 
   [guide][nginx_uwsgi_guide] for nginx with uwsgi, a bit out of date though
    * When configuring uwsgi instead of `module` use `wsgi-file` and the full
      path to `judgesystem/judgeSystem/wsgi.py`
    * Most distros have systemd services so instead of `sudo service ...`
      use `sudo systemctl (start|restart|stop|enable) (nginx|uwsgi)`
7. (optional) Install celery as a service (systemd)
   * Add to `judge-celery.service` the full path to the repository
   * Copy the file to create the service `sudo cp judge-celery.service
       /etc/systemd/system/` and reload the services with `sudo systemctl
       daemon-reload`
  * Control it with `sudo systemctl (start|stop|restart) judge-celery` and make
      it auto-start with `sudo systemctl enable judge-celery`

##How to run:
  * Web server
      * If you installed a nginx it should be running as a service
      * For the development servere`python manage.py runserver` (you can add a `url:port` pair as a
        parameter)
  * Celery 
      * If you installed the service it should be running
      * Otherwise `sudo ./run_celery`

[isolate]: https://github.com/ioi/isolate
[virtualenv]: https://virtualenv.pypa.io/en/stable/
[virtualenv_guide]: https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-uwsgi-and-nginx-on-ubuntu-14-04#install-and-configure-virtualenv-and-virtualenvwrapper
[postgres_guide]: https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04#create-a-database-and-database-user

[gmail]: http://mail.google.com/
[recaptcha]: https://www.google.com/recaptcha

[nginx_uwsgi_guide]: https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-uwsgi-and-nginx-on-ubuntu-14-04#setting-up-the-uwsgi-application-server
