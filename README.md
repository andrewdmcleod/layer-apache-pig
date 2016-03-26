## Overview

Apache Pig is a platform for creating MapReduce programs used with Hadoop.
It consists of a high-level language (Pig Latin) for expressing data analysis
programs, coupled with infrastructure for evaluating these programs. Learn more
at [pig.apache.org](http://pig.apache.org).

This charm supports running Pig in two execution modes:

 * Local Mode: Pig runs using your local host and file system. Specify local
   mode using the -x flag: `pig -x local`
 * Mapreduce Mode: Pig runs using a Hadoop cluster and HDFS. This is the default
   mode; you can, optionally, specify it using the -x flag:
   `pig` or `pig -x mapreduce`


## Usage

This charm leverages our pluggable Hadoop model with the `hadoop-plugin`
interface. This means that you will need to deploy a base Apache Hadoop cluster
to run Pig. The suggested deployment method is to use the
[apache-analytics-pig](https://jujucharms.com/apache-analytics-pig/)
bundle. This will deploy the Apache Hadoop platform with a single Apache Pig
unit that communicates with the cluster by relating to the
`apache-hadoop-plugin` subordinate charm:

    juju deploy apache-analytics-pig

Alternatively, you may manually deploy the recommended environment as follows:

    juju deploy apache-hadoop-namenode namenode
    juju deploy apache-hadoop-resourcemanager resourcemgr
    juju deploy apache-hadoop-slave slave
    juju deploy apache-hadoop-plugin plugin
    juju deploy apache-pig pig

    juju add-relation resourcemgr namenode
    juju add-relation namenode slave
    juju add-relation resourcemgr slave
    juju add-relation plugin namenode
    juju add-relation plugin resourcemgr
    juju add-relation pig plugin

### Local Mode

Once deployment is complete, run Pig in local mode on the Pig unit with the
following:

    juju ssh pig/0
    pig -x local

### MapReduce Mode

MapReduce mode is the default for Pig. To run in this mode, ssh to the Pig unit
and run pig as follows:

    juju ssh pig/0
    pig


## Testing the deployment

### Smoke test Local Mode

SSH to the Pig unit and run pig as follows:

    juju ssh pig/0
    pig -x local
    quit
    exit

### Smoke test MapReduce Mode

SSH to the Pig unit and test in MapReduce mode as follows:

    juju ssh pig/0
    hdfs dfs -mkdir -p /user/ubuntu
    hdfs dfs -copyFromLocal /etc/passwd /user/ubuntu/passwd
    echo "A = load '/user/ubuntu/passwd' using PigStorage(':');" > /tmp/test.pig
    echo "B = foreach A generate \$0 as id; store B into '/tmp/pig.out';" >> /tmp/test.pig
    pig -l /tmp/test.log /tmp/test.pig
    hdfs dfs -cat /tmp/pig.out/part-m-00000
    exit


## Contact Information

- <bigdata@lists.ubuntu.com>


## Help

- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju community](https://jujucharms.com/community)
