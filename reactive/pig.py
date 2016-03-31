from charms.reactive import when, when_none, when_not
from charms.reactive import is_state, set_state, remove_state
from charmhelpers.core import hookenv
from charms.layer.apache_pig import Pig
from charms.layer.hadoop_client import get_dist_config


@when_not('pig.installed')
def install_pig():
    pig = Pig(get_dist_config())
    if pig.verify_resources():
        hookenv.status_set('maintenance', 'installing pig')
        hookenv.log('Installing Apache Pig')
        pig.install()
        pig.initial_config()
        set_state('pig.installed')
        hookenv.status_set('waiting', 'waiting to configure pig')
        hookenv.log('Apache Pig is installed and ready to be configured')


@when('pig.installed')
@when_none('pig.configured.local', 'pig.configured.yarn')
def configure_pig():
    pig = Pig(get_dist_config())
    hadoop_ready = is_state('hadoop.ready')
    if hadoop_ready:
        hookenv.status_set('maintenance', 'configuring pig (mapreduce)')
        hookenv.log('YARN is ready, configuring Apache Pig in MapReduce mode')
        pig.configure_yarn()
        remove_state('pig.configured.local')
        set_state('pig.configured.yarn')
        hookenv.status_set('active', 'ready (mapreduce)')
        hookenv.log('Apache Pig is ready in MapReduce mode')
    else:
        hookenv.status_set('maintenance', 'configuring pig (local)')
        hookenv.log('YARN is not ready, configuring Pig in local mode')
        pig.configure_local()
        remove_state('pig.configured.yarn')
        set_state('pig.configured.local')
        hookenv.status_set('active', 'ready (local)')
        hookenv.log('Apache Pig is ready in local mode')


@when('pig.configured.yarn')
@when_not('hadoop.ready')
def reconfigure_local():
    configure_pig()


@when('pig.configured.local')
@when('hadoop.ready')
def reconfigure_yarn(hadoop):
    configure_pig()
