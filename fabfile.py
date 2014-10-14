from fabric.api import *
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
    env.cd = lcd
    env.name = 'local'
    env.hosts = ['localhost']
    env.path = Path(__file__).ancestor(1) + "/"
    env.project = 'theeyes'
    env.virtualenv = 'virtualenv -p python3'
    env.environment = env.path + 'venv'
    env.python = 'python'
    env.pip = 'pip'
    env.manage = MANAGE.format(env.python)
    env.restart = ('echo "You must use manage.py runserver"',)


@task
def production():
    env.run = run
    env.cd = cd
    env.user = 'theeyes'
    env.name = 'production'
    env.hosts = ['theey.es']
    env.path = '/srv/theeyes/'
    env.project = 'theeyes'
    env.virtualenv = 'virtualenv -p python3'
    env.environment = env.path + 'venv'
    env.warn_only = True
    env.python = 'source {0}venv/bin/activate && python'.format(env.path)
    env.pip = 'source {0}venv/bin/activate && pip'.format(env.path)
    env.manage = MANAGE.format(env.python)
    env.restart = ('sudo /usr/sbin/service uwsgi stop',
                   'sudo /usr/sbin/service nginx stop',
                   'sudo /usr/sbin/service uwsgi start',
                   'sudo /usr/sbin/service nginx start',)


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
    if not 'localhost' in env.hosts:
        extra_opts = '--omit-dir-times'
        put('requirements', env.path)
        rsync_project(remote_dir=env.path,
                      local_dir=env.project,
                      delete=True,
                      extra_opts=extra_opts,
                      exclude=('{0}/static/'.format(env.project),
                               '{0}/media/'.format(env.project),
                               '{0}/logs/'.format(env.project),
                               '*.pyc',
                               '*.pyo'))

        rsync_project(remote_dir=env.path,
                      local_dir='brainstem',
                      delete=True,
                      extra_opts=extra_opts,
                      exclude=('brainstem/logs/',
                               '__pycache__',
                               '*.pyc',
                               '*.pyo'))

        rsync_project(remote_dir=env.path,
                      local_dir='webroot',
                      delete=True,
                      extra_opts=extra_opts,
                      exclude=('conductor/logs/',
                               '__pycache__',
                               '*.pyc',
                               '*.pyo'))


@task
def update_requirements():
    with prefix(ACTIVATE.format(env.environment)):
        env.run(UPDATE_REQS.format(env.pip, env.path, env.name))


@task
def collectstatic():
    with env.cd(env.path + env.project):
        with prefix(ACTIVATE.format(env.environment)):
            env.run(env.manage + COLLECT_STATIC.format(env.project, env.name))


@task
def syncdb():
    with env.cd(env.path + env.project):
        with prefix(ACTIVATE.format(env.environment)):
            env.run(env.manage + SYNCDB.format(env.project, env.name))


@task
def migrate():
    with env.cd(env.path + env.project):
        with prefix(ACTIVATE.format(env.environment)):
            env.run(env.manage + MIGRATE.format(env.project, env.name))


@task
def restart():
    with settings(warn_only=True):
        for cmd in env.restart:
            env.run(cmd)


@task
def restart_conductor():
    env.run('sudo service conductor stop')
    env.run('sudo service conductor start')


@task
def deploy():
    upload()
    collectstatic()
    syncdb()
    migrate()
    restart()
