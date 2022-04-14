# Reproducing indirect bugs

For each reproduced bug, you will see a test result json file as shown in the last column of `bug_reproduction_stats.tsv` (e.g., `sieve_test_results/cassandra-operator-scaledown-scaleup-cassandra-operator-indirect-1.yaml.json`).
This json file contains the errors detected by Sieve (see the `detected_errors` field).
The errors can be common errors (like timeout) and inconsistencies detected by the differential oracles.
We present the expected errors caused by each bug below to help you evaluate whether the bug is correctly reproduced.
Sieve might detect many different errors for the same bug,
we only present one or two representative errors here.

### [cassandra-operator](https://github.com/instaclustr/cassandra-operator)

#### indirect-1: [instaclustr-cassandra-operator-400](https://github.com/instaclustr/cassandra-operator/issues/400)
The `sieve_test_results/cassandra-operator-scaledown-scaleup-cassandra-operator-indirect-1.yaml.json` is supposed to contain the following error in its `detected_errors` field:
```
Error from the workload: error: hard timeout: cassandra-test-cluster-dc1-rack1-1 does not become Terminated within 600 seconds
```

#### indirect-2: [instaclustr-cassandra-operator-410](https://github.com/instaclustr/cassandra-operator/issues/410)
The `sieve_test_results/cassandra-operator-scaledown-scaleup-brittle-cassandra-operator-indirect-2.yaml.json` is supposed to contain the following error in its `detected_errors` field:
```
End state inconsistency - object field has a different value: pod/default/cassandra-test-cluster-dc1-rack1-1["status"]["containerStatuses"][0]["ready"] is True after reference run, but False after testing run
End state inconsistency - object field has a different value: statefulset/default/cassandra-test-cluster-dc1-rack1["status"]["readyReplicas"] is 2 after reference run, but 1 after testing run
```

### [mongodb-operator](https://github.com/percona/percona-server-mongodb-operator)

#### indirect-1: [percona-server-mongodb-operator-434](https://jira.percona.com/browse/K8SPSMDB-434)
The `sieve_test_results/mongodb-operator-disable-enable-shard-mongodb-operator-indirect-1.yaml.json` is supposed to contain the following error in its `detected_errors` field:
```
Exception from controller: Observed a panic: "invalid memory address or nil pointer dereference" (runtime error: invalid memory address or nil pointer dereference)
```

#### indirect-2: [percona-server-mongodb-operator-590](https://jira.percona.com/browse/K8SPSMDB-590)
The `sieve_test_results/mongodb-operator-recreate-mongodb-operator-indirect-2.yaml.json` is supposed to contain the following error in its `detected_errors` field:
```
State-update summaries inconsistency: secret/default/mongodb-cluster-ssl ADDED inconsistency: 2 event(s) seen during reference run, but 
3 seen during testing run                                                                                                               
State-update summaries inconsistency: secret/default/mongodb-cluster-ssl DELETED inconsistency: 1 event(s) seen during reference run, bu
t 2 seen during testing run                                                                                                             
State-update summaries inconsistency: secret/default/mongodb-cluster-ssl-internal ADDED inconsistency: 2 event(s) seen during reference 
run, but 3 seen during testing run                                                                                                      
State-update summaries inconsistency: secret/default/mongodb-cluster-ssl-internal DELETED inconsistency: 1 event(s) seen during referenc
e run, but 2 seen during testing run
```

#### indirect-3: [percona-server-mongodb-operator-591](https://jira.percona.com/browse/K8SPSMDB-591)
The `sieve_test_results/mongodb-operator-disable-enable-shard-brittle-mongodb-operator-indirect-3.yaml.json` is supposed to contain the following error in its `detected_errors` field:
```
End state inconsistency - object field has a different value: perconaservermongodb/default/mongodb-cluster["status"]["state"] is ready after learning run, but error after testing run
End state inconsistency - fewer object fields than reference: perconaservermongodb/default/mongodb-cluster["status"]["replsets"]["rs0"]["added_as_shard"] is True after learning run, but not seen after testing run
```

### [yugabyte-operator](https://github.com/yugabyte/yugabyte-operator)

#### indirect-1: [yugabyte-operator-33](https://github.com/yugabyte/yugabyte-operator/issues/33)
The `sieve_test_results/yugabyte-operator-disable-enable-tuiport-yugabyte-operator-indirect-1.yaml.json` is supposed to contain the following error in its `detected_errors` field:
```
Error from the workload: error: cmd 'kubectl patch YBCluster example-ybcluster --type merge -p='{"spec":{"tserver":{"tserverUIPort": 0}}}'' return non-zero code 1
Error from the workload: error: hard timeout: yb-tserver-ui does not become non-exist within 600 seconds
```

#### indirect-2: [yugabyte-operator-43](https://github.com/yugabyte/yugabyte-operator/issues/43)
The `sieve_test_results/yugabyte-operator-disable-enable-tls-yugabyte-operator-indirect-2.yaml.json` is supposed to contain the following error in its `detected_errors` field:
```
End state inconsistency - object field has a different value: pod/default/yb-master-2["status"]["containerStatuses"][0]["state"]["running"] is {'StartedAt': '2022-02-04T08:50:21Z'} after reference run, but None after testing run
```

### [zookeeper-operator](https://github.com/pravega/zookeeper-operator)

#### indirect-1: [zookeeper-operator-410](https://github.com/pravega/zookeeper-operator/issues/410)
The `sieve_test_results/zookeeper-operator-recreate-zookeeper-operator-indirect-1.yaml.json` is supposed to contain the following error in its `detected_errors` field:
```
State-update summaries inconsistency: configmap/default/zookeeper-cluster-configmap ADDED inconsistency: 2 event(s) seen during referenc
e run, but 3 seen during testing run                                                                                                    
State-update summaries inconsistency: configmap/default/zookeeper-cluster-configmap DELETED inconsistency: 1 event(s) seen during refere
nce run, but 2 seen during testing run
```