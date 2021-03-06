import glob
import os
import platform
import re
import shutil
import subprocess
import sys

PYTHON = sys.executable
IS_WINDOWS = platform.system() == 'Windows'


def step(message):
    print('[*] %s' % message)


def error_exit(message):
    print('[-] Error: %s' % message)
    sys.exit(-1)


step('Checking Python version')

if sys.version_info[:2] < (3, 5):
    error_exit('Python 3.5+ required')


step('Checking pip installation')
try:
    subprocess.check_call([PYTHON, '-m', 'pip', '-V'])
except Exception:
    error_exit('pip not installed')


step('Checking JDK installation')

try:
    subprocess.check_call(['javac', '-version'])
except Exception:
    error_exit('JDK not installed')

if 'JAVA_HOME' not in os.environ:
    error_exit("'JAVA_HOME' not set")


step('Cloning projects')

for d in ('topic-model-analysis', 'Twitter-LDA'):
    if os.path.exists(d):
        if input('%r already exists, do you want to remove it? (Y/N)' % d).strip().lower() == 'y':
            shutil.rmtree(d, ignore_errors=True)
        else:
            error_exit('User canceled deployment')

subprocess.check_call(['git', 'clone', 'https://github.com/gousaiyang/topic-model-analysis.git'])
subprocess.check_call(['git', 'clone', 'https://github.com/gousaiyang/Twitter-LDA.git'])


step('Installing required modules')

os.chdir('topic-model-analysis')

if IS_WINDOWS:
    subprocess.check_call([PYTHON, '-m', 'pip', 'install', '-r', 'requirements.txt'])
else:
    subprocess.check_call(['sudo', '-H', PYTHON, '-m', 'pip', 'install', '-r', 'requirements.txt'])

os.chdir('..')


step('Building Twitter-LDA')

os.chdir('Twitter-LDA')
sep = ';' if IS_WINDOWS else ':'
classpath = sep.join(glob.glob('lib/*.jar'))
os.mkdir('bin')
subprocess.check_call(['javac', '-sourcepath', 'src', '-cp', classpath, '-d', 'bin', 'src/TwitterLDA/TwitterLDAmain.java'])
os.chdir('..')


step('Setting configuration')

os.chdir('topic-model-analysis')

with open('.env.example', 'r') as env_file:
    env_content = env_file.read()

env_content = re.sub(r'TWLDA_BASE_DIR=', r'TWLDA_BASE_DIR=../Twitter-LDA', env_content)

with open('.env', 'w') as env_file:
    env_file.write(env_content)

print('[+] Deployment done.')
