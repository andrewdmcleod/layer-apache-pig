import jujuresources

from charmhelpers.core import unitdata
from jujubigdata import utils
from path import Path
from subprocess import check_output


def install_java():
    """Install java just like we do for Hadoop Base.

    This is the same method used to install java in HadoopBase:
    https://github.com/juju-solutions/jujubigdata/blob/master/jujubigdata/handlers.py#L134

    This allows us to run Pig in local mode (which requires Java) without
    any Hadoop. If Hadoop comes along later, we'll already have java installed
    in a way that is compatible with the plugin.

    NOTE: this will go away if/when we support the java interface.
    """
    env = utils.read_etc_env()
    java_installer = Path(jujuresources.resource_path('java-installer'))
    java_installer.chmod(0o755)
    output = check_output([java_installer], env=env).decode('utf8')
    lines = output.strip().splitlines()
    if len(lines) != 2:
        raise ValueError('Unexpected output from java-installer: %s' % output)
    java_home, java_version = lines
    if '_' in java_version:
        java_major, java_release = java_version.split("_")
    else:
        java_major, java_release = java_version, ''
    unitdata.kv().set('java.home', java_home)
    unitdata.kv().set('java.version', java_major)
    unitdata.kv().set('java.version.release', java_release)


class Pig(object):
    def __init__(self, dist_config):
        self.dist_config = dist_config
        self.resources = {
            'java-installer': 'java-installer',
            'pig': 'pig-noarch',
        }
        self.verify_resources = utils.verify_resources(*self.resources.values())

    def install(self, force=False):
        """Add dirs from dist.yaml and install Pig and java."""
        self.dist_config.add_dirs()
        jujuresources.install(self.resources['pig'],
                              destination=self.dist_config.path('pig'),
                              skip_top_level=True)
        install_java()

    def initial_config(self):
        """Do one-time Pig configuration.

        Copy the default configuration files to the pig_conf dir from dist.yaml
        and adjust system environment.
        """
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
            env['PIG_CONF_DIR'] = self.dist_config.path('pig_conf')
            env['PIG_HOME'] = self.dist_config.path('pig')
            env['JAVA_HOME'] = Path(unitdata.kv().get('java.home'))

    def configure_local(self):
        """In local mode, configure Pig with PIG_HOME as the classpath."""
        with utils.environment_edit_in_place('/etc/environment') as env:
            env['PIG_CLASSPATH'] = env['PIG_HOME']

    def configure_yarn(self):
        """In mapred mode, configure Pig with HADDOP_CONF as the classpath."""
        with utils.environment_edit_in_place('/etc/environment') as env:
            env['PIG_CLASSPATH'] = env['HADOOP_CONF_DIR']
