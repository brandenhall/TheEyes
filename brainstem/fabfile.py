from fabric.api import task, env, lcd, put, prefix, run
from fabric.contrib.project import rsync_project
from fabric.operations import local as lrun
from unipath import Path

ACTIVATE = 'source {0}/bin/activate'
UPDATE_REQS = '{0} install -r {1}requirements/{2}.txt'
MANAGE = '{0} manage.py '
COLLECT_STATIC = 'collectstatic --noinput --settings {0}.settings.{1}'
SYNCDB = 'syncdb --settings {0}.settings.{1}'
MIGRATE = 'migrate --settings {0}.settings.{1}'


@task
def local():
    env.run = lrun
    env.sudo = lrun
    env.cd = lcd
    env.name = 'local'
    env.hosts = ['localhost']
    env.path = Path(__file__).ancestor(1) + "/"
    env.project = 'brainstem'
    env.virtualenv = 'virtualenv -p python3 --no-site-packages'
    env.environment = env.path + 'venv'
    env.python = 'python'
    env.pip = 'pip'
    env.manage = MANAGE.format(env.python)
    env.restart = 'echo "You must use manage.py runserver"'


@task
def bootstrap():
    upload()
    env.cd(env.path)
    env.run('rm -rf {0}'.format(env.environment))
    env.run('mkdir -p {0}'.format(env.environment))
    env.run('{0} {1} --no-site-packages'.format(
        env.virtualenv, env.environment))
    update_requirements()


@task
def upload():
    if 'localhost' not in env.hosts:
        extra_opts = '--omit-dir-times'
        put('requirements', env.path)
        rsync_project(remote_dir=env.path,
                      local_dir=env.project,
                      delete=True,
                      extra_opts=extra_opts,
                      exclude=('logs/',
                               '__pycache__',
                               '*.pyc',
                               '*.pyo'))


@task
def update_requirements():
    with prefix(ACTIVATE.format(env.environment)):
        env.run(UPDATE_REQS.format(env.pip, env.path, env.name))


@task
def restart():
    if 'localhost' not in env.hosts:
        run('sudo service conductor restart')


@task
def deploy():
    upload()
    restart()
