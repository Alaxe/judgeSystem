#!/usr/bin/env python3
import os
import subprocess

subprocess.call(['git', 'submodule', 'init'])
subprocess.call(['git', 'submodule', 'update'])

subprocess.call(['make', '-C', 'isolate'])
subprocess.call(['cp', 'isolate/isolate', 'judge/isolate'])

subprocess.call(['mkdir', '-p', 'judge/solutions', 'judge/graders'])
subprocess.call(['mkdir', '-p', 'static', 'media'])

subprocess.call(['pip3', 'install', '-r', 'requirements.txt', '--upgrade'])

subprocess.call(['./manage.py', 'makemigrations'])
subprocess.call(['./manage.py', 'migrate'])
subprocess.call(['./manage.py', 'collectstatic', '--noinput'])
