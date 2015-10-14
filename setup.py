#!/usr/bin/env python3
import os
import subprocess

subprocess.call(['git', 'submodule', 'init'])
subprocess.call(['git', 'submodule', 'update'])

subprocess.call(['make', '-C', 'isolate'])
subprocess.call(['cp', 'isolate/isolate', 'judge/isolate'])

subprocess.call(['pip', 'install', '-r', 'requirements.txt', '--upgrade'])
subprocess.call(['./manage.py', 'migrate'])
