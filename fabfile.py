#
import os
from sys import platform
from fabric.api import *
from datetime import date


CONTAINER_NAME = 'echo'
RUN_STRING = ' '.join([
    'docker run',
    '-d',
    '--name ' + CONTAINER_NAME,
    '--restart always',
    '-t ' + CONTAINER_NAME
])


def _cmd(*args):
    return ' '.join(args)


def _get_pyenv_exec():
    """ get an abs path to pyenv, or just return sys """
    env_path = os.path.expanduser('~/.pyenv/bin/pyenv')
    if os.path.exists(env_path):
        return env_path

    return 'pyenv'  # global?


def _get_python_exec(exe='python'):
    """ figure out the python path """
    cmd = _cmd(_get_pyenv_exec(), 'root')
    path = local(cmd, capture=True)
    py = '{p}/versions/{cont}/bin/{exe}'.format(
        p=path, exe=exe, cont=CONTAINER_NAME
    )

    return py


@task
def tests(arg='local'):
    """ write the tests """
    with cd(os.getcwd()):
        if arg == 'local':
            local('env/bin/py.test test/')
        elif arg == 'docker':
            local('fab docker:test')



@task
def version_bump(part='patch'):
    # run('echo `git rev-parse --short HEAD`.%s > VERSION' % date.today())
    if part not in ('major', 'minor', 'patch'):
        print('Arg needs to be one of major, minor, patch')
        exit(-1)
        
    local('env/bin/bumpversion %s VERSION' % part)
    local('cat VERSION')


@task
def deps():
    """
    find out where pyenv is installed, and then install the deps
    """
    pip = _get_python_exec('pip')
    local(_cmd(pip, 'install --upgrade pip'))
    local(_cmd(pip, 'install --upgrade -r requirements.txt'))


@task
def install():
    """ """
    with settings(warn_only=True):
        if platform in ('linux', 'linux2'):
            local('apt-get install -y python-dev libyaml-dev')
        elif platform in ('darwin',):
            local('brew install libyaml pyenv')
        else:
            print('got %s for platform, wtfbbq?' % platform)
            exit(0)

    # Install pyenv and the virtual environment first
    with settings(warn_only=True):
        local('curl -L '
              'https://raw.githubusercontent.com/'
              'yyuu/pyenv-installer/master/bin/pyenv-installer | bash')
        pyenv = _get_pyenv_exec()
        local(_cmd(pyenv, 'install', '-s', '3.5.1'))
        local(_cmd(pyenv, 'virtualenv', '-f 3.5.1', CONTAINER_NAME))

    deps()


@task
def docker(arg):
    """ """
    def _build():
        """  """
        with cd(os.getcwd()):
            local('fab update')

        local('docker build -t %s:latest .' % CONTAINER_NAME)
        local('docker images')

        # stop and remove any running containers
        with settings(warn_only=True):
            local('docker stop ' + CONTAINER_NAME)
            local('docker rm ' + CONTAINER_NAME)

            # create a new container with the updated image
            # local('docker create --name {0} -i -t {0}:latest'.format(CONTAINER_NAME)

    def _start():
        _build()
        with settings(warn_only=True):
            local('docker stop ' + CONTAINER_NAME)
            local('docker rm -f ' + CONTAINER_NAME)

        local(RUN_STRING)

    def _run():
        local('docker run -it ' + CONTAINER_NAME)

    def _test():
        local('docker run -it %s:latest /usr/bin/py.test test/' % CONTAINER_NAME)

    def _clean():
        with settings(warn_only=True):
            local('docker images -q | xargs docker rmi -f ')
            local('docker rmi -f $(docker images --filter "dangling=true" -q --no-trunc)')
            local('docker images -a')

    ####################################

    if arg == 'build':
        _build()
    elif arg in ('test', 'tests'):
        _test()
    elif arg == 'start':
        _start()
    elif arg == 'run':
        _run()
    elif arg == 'clean':
        _clean()
    else:
        print('u wot m8')
        exit(0)


@task
def update(arg=None):
    """ """
    def _local():
        with cd(os.getcwd()):
            local('git reset --hard')
            local('chmod 0600 deploy/deploy_key')
            local("ssh-agent bash -c 'ssh-add deploy/deploy_key; git pull'")
            local('fab version_bump')

    if arg in ('local', '', None):
        _local()
    else:
        print('u wot m8')
        exit(0)
