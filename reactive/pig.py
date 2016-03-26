from charms.reactive import when, when_not
from charms.reactive import is_state, set_state, remove_state
from charmhelpers.core import hookenv
from charms.layer.apache_pig import Pig
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
def report_status():
    hadoop_joined = is_state('hadoop.joined')
    hadoop_ready = is_state('hadoop.ready')
    if not hadoop_joined:
        hookenv.status_set('blocked', 'Waiting for relation to Hadoop Plugin')
    elif not hadoop_ready:
        hookenv.status_set('waiting', 'Waiting for Hadoop Plugin to become ready')


@when('pig.installed', 'hadoop.ready')
@when_not('pig.configured')
def configure_pig(*args):
    hookenv.status_set('maintenance', 'Setting up Apache Pig')
    pig = Pig(get_dist_config())
    pig.setup_pig()
    set_state('pig.configured')
    hookenv.status_set('active', 'Ready')


@when('pig.configured')
@when_not('hadoop.ready')
def stop_pig():
    remove_state('pig.configured')
    report_status()
