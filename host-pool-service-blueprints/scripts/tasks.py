import itertools
import os.path
import StringIO

import fabric.api
import fabric.context_managers

import yaml

import cloudify


HOST_POOL_PACKAGE_LINK = 'https://codeload.github.com/cloudify-cosmo/cloudify-host-pool-service/zip/master'

_DPKG = 1
_WHICH = 2

_updated = False


def create(directory):
    _ensure_dependencies_installed()
    fabric.api.run(
        ' && '.join(['mkdir {0}'.format(directory),
                     'cd {0}'.format(directory),
                     'virtualenv .',
                     '. bin/activate',
                     'pip install {0}'.format(HOST_POOL_PACKAGE_LINK),
                     'pip install gunicorn']))


def configure(directory, environment=None):
    env = environment or {}
    config_filename = env.get('HOST_POOL_CONFIG', 'host-pool.yaml')
    pool_config = cloudify.ctx.get_resource(
        'resources/{0}'.format(config_filename))
    keys, key_dirs = _get_key_dirs_and_paths(pool_config)
    with fabric.context_managers.cd(directory):
        f = StringIO.StringIO(pool_config)
        f.name = config_filename
        fabric.api.put(f, config_filename)
        if key_dirs:
            fabric.api.run('mkdir -p {0}'.format(' '.join(key_dirs)))
        for key in keys:
            _sftp_resource_copy('resources/{0}'.format(key), key)


def _get_key_dirs_and_paths(pool_config):
    pool = yaml.load(pool_config).get('pool', {})
    keys = set()
    key_dirs = set()
    for entry in itertools.chain([pool.get('default', {})],
                                 pool.get('hosts', [])):
        if 'auth' in entry and entry['auth'].get('keyfile') is not None:
            keys.add(entry['auth']['keyfile'])
    for key in keys:
        d = os.path.dirname(key)
        if d == '':
            continue
        if d[0] == '/':
            raise Exception(
                '\'{0}\': absolute paths are not supported!'.format(key))
        key_dirs.add(d)
    return keys, key_dirs


def _ensure_dependencies_installed():
    if not _is_installed('python-dev', _DPKG):
        _install_with_apt_get('python-dev')
    if not _is_installed('pip', _WHICH):
        _install_with_apt_get('python-pip')
        fabric.api.sudo('pip install --upgrade pip')
    if not _is_installed('virtualenv', _WHICH):
        fabric.api.sudo('pip install virtualenv')


def _is_installed(what, check_method):
    if check_method == _DPKG:
        result = fabric.api.run(
            'dpkg-query --status {0} 1>/dev/null 2>&1'.format(what),
            quiet=True)
    elif check_method == _WHICH:
        result = fabric.api.run(
            'which {0} 1>/dev/null 2>&1'.format(what),
            quiet=True)
    else:
        raise Exception('bad parameter')
    return result.succeeded


def _install_with_apt_get(what):
    global _updated
    if not _updated:
        fabric.api.sudo('apt-get update')
        _updated = True
    fabric.api.sudo('apt-get --yes install {0}'.format(what))


def _sftp_resource_copy(resource_path, remote_target_path):
    contents = cloudify.ctx.get_resource(resource_path)
    f = StringIO.StringIO(contents)
    f.name = resource_path
    fabric.api.put(f, remote_target_path)
