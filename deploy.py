import glob
import os
import platform
import re
import subprocess
import sys


def step(message):
    print('[*] %s' % message)


def error_exit(message):
    print('[-] Error: %s' % message)
    sys.exit(-1)


step('Checking Python version')

if sys.version_info[:2] < (3, 5):
    error_exit('Python 3.5+ required')


step('Checking Java installation')

try:
    subprocess.check_call(['java', '-version'])
except Exception:
    error_exit('Java not installed')

if 'JAVA_HOME' not in os.environ:
    error_exit("'JAVA_HOME' not set")


step('Cloning projects')

subprocess.check_call(['git', 'clone', 'https://github.com/gousaiyang/topic-model-analysis.git'])
subprocess.check_call(['git', 'clone', 'https://github.com/gousaiyang/Twitter-LDA.git'])


step('Installing required modules')

os.chdir('topic-model-analysis')
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
os.chdir('..')


step('Building Twitter-LDA')

os.chdir('Twitter-LDA')
sep = ';' if platform.system() == 'Windows' else ':'
classpath = sep.join(glob.glob('lib/**/*.jar', recursive=True) + ['bin'])

os.mkdir('bin')

for f in glob.glob('src/**/*.java', recursive=True):
    subprocess.check_call(['javac', '-cp', classpath, '-d', 'bin', f])

os.chdir('..')


step('Setting configuration')

os.chdir('topic-model-analysis')

with open('.env.example', 'r') as env_file:
    env_content = env_file.read()

env_content = re.sub(r'TWLDA_BASE_DIR=', r'TWLDA_BASE_DIR=../Twitter-LDA', env_content)

with open('.env', 'w') as env_file:
    env_file.write(env_content)

print('[+] Deployment done.')
