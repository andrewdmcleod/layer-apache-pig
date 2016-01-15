import jujuresources
from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state
from charmhelpers.core import hookenv
from jujubigdata import utils
from charmhelpers.fetch import apt_install
from subprocess import check_call
from charms.pig import Pig

DIST_KEYS = ['vendor', 'hadoop_version', 'groups', 'users', 'dirs']

def get_dist_config(keys):
    from jujubigdata.utils import DistConfig

    if not getattr(get_dist_config, 'value', None):
        get_dist_config.value = DistConfig(filename='dist.yaml', required_keys=keys)
    return get_dist_config.value


#@when('hadoop.installed')
@when_not('pig.installed')
def install_pig():
    pig = Pig(get_dist_config(DIST_KEYS))
    if pig.verify_resources():
        hookenv.status_set('maintenance', 'Installing Pig')
        pig.install()
        set_state('pig.installed')


@when('pig.installed')
@when_not('hadoop.related')
def missing_hadoop():
    hookenv.status_set('blocked', 'Waiting for relation to Hadoop')


@when('pig.installed', 'hadoop.ready')
@when_not('pig.configured')
def configure_pig(*args):
    hookenv.status_set('maintenance', 'Setting up pig')
    pig = Pig(get_dist_config(DIST_KEYS))
    pig.setup_pig()
    set_state('pig.configured')
    hookenv.status_set('active', 'Ready')


@when('pig.configured')
@when_not('hadoop.ready')
def stop_pig():
    remove_state('pig.configured')
    hookenv.status_set('blocked', 'Waiting for Hadoop connection')
