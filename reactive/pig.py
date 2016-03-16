from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state
from charmhelpers.core import hookenv
from charms.pig import Pig
from charms.layer.hadoop_client import get_dist_config


@when_not('pig.installed')
def install_pig():
    pig = Pig(get_dist_config())
    if pig.verify_resources():
        hookenv.status_set('maintenance', 'Installing Pig')
        pig.install()
        set_state('pig.installed')


@when('pig.installed')
@when_not('hadoop.ready')
def missing_hadoop():
    hookenv.status_set('blocked', 'Waiting for relation to Hadoop')


@when('pig.installed', 'hadoop.ready')
@when_not('pig.configured')
def configure_pig(*args):
    hookenv.status_set('maintenance', 'Setting up pig')
    pig = Pig(get_dist_config())
    pig.setup_pig()
    set_state('pig.configured')
    hookenv.status_set('active', 'Ready')


@when('pig.configured')
@when_not('hadoop.ready')
def stop_pig():
    remove_state('pig.configured')
    hookenv.status_set('blocked', 'Waiting for Hadoop connection')
