import jujuresources
from jujubigdata import utils


class Pig(object):
    def __init__(self, dist_config):
        self.dist_config = dist_config
        self.resources = {
            'pig': 'pig-noarch',
        }
        self.verify_resources = utils.verify_resources(*self.resources.values())

    def install(self, force=False):
        self.dist_config.add_users()
        self.dist_config.add_dirs()
        jujuresources.install(self.resources['pig'],
                              destination=self.dist_config.path('pig'),
                              skip_top_level=True)

    def setup_pig(self):
        '''
        copy the default configuration files to pig_conf property
        defined in dist.yaml
        '''
        default_conf = self.dist_config.path('pig') / 'conf'
        pig_conf = self.dist_config.path('pig_conf')
        pig_conf.rmtree_p()
        default_conf.copytree(pig_conf)
        # Now remove the conf included in the tarball and symlink our real conf
        default_conf.rmtree_p()
        pig_conf.symlink(default_conf)

        # Configure immutable bits
        pig_bin = self.dist_config.path('pig') / 'bin'
        with utils.environment_edit_in_place('/etc/environment') as env:
            if pig_bin not in env['PATH']:
                env['PATH'] = ':'.join([env['PATH'], pig_bin])
            env['PIG_CLASSPATH'] = env['HADOOP_CONF_DIR']
            env['PIG_CONF_DIR'] = self.dist_config.path('pig_conf')
            env['PIG_HOME'] = self.dist_config.path('pig')

    def cleanup(self):
        self.dist_config.remove_users()
        self.dist_config.remove_dirs()
