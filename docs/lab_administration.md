# Lab Cluster Administration

This page is for those that are installing or managing an OpenShift cluster for this lab.

## OpenShift Cluster Preparation

1. These labs currently only support an x86_64/amd64 OpenShift cluster.
1. Install the WebSphere Liberty Operator:
    1. Add the [IBM operator catalog](https://www.ibm.com/docs/en/cloud-paks/1.0?topic=clusters-adding-operator-catalog)
    1. [Install the operator with oc in AllNamespaces](https://www.ibm.com/docs/en/was-liberty/base?topic=operator-installing-red-hat-openshift-cli)
1. If you would like to support the labs that require `cluster-admin` permissions such as [Health of the cluster](lab_basics_openshift_health.md), etc.:
    1. If you are just running the lab yourself, you can just use any user with `cluster-admin` authority (e.g. `kubeadmin`)
    1. If you would like to create a set of administrator users, review the [cluster-admin group configuration steps](#cluster-admin-group-configuration-steps).
1. If instead of `cluster-admin` users, you want normal users, review the [normal users configuration steps](#normal-users-configuration-steps).
1. If you would like to create a namespace for each user to use which has quotas, review the [namespaces with quotas configuration steps](#namespaces-with-quotas-configuration-steps).
1. The cluster is now ready for students to use [the lab](index.md).

---

## Cluster-admin group configuration steps

1. Log in as a user with `cluster-admin` access into the OpenShift web console
1. Go to `User Management` } `Groups`
1. Click `Create Group`
1. Set `name: admingroup`
1. Remove the `users` section as we will add users later:

          users:
            - user1
            - user2

1. Click `Create`
1. Click `RoleBindings`
1. Click `Create binding`
1. Select `ClusterRoleBinding`
1. Set Name to `admingroupclusteradminbinding`
1. Set Role name to `cluster-admin`
1. Click `Create`
1. Create one or more admin users:
    1. Generate a random password:

            cat /dev/random | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 22 | head -n 1

    1. Create/update a user password file. Replace `$PASSWORD` with the output from the previous step and update `adminuser1` with the user name you'd like. For all but the first user, remove the `-c` flag.

            htpasswd -c -B -b adminusers.htpasswd adminuser1 $PASSWORD

    1. Remember this user name and password combination somewhere.

1. In the OpenShift web console, go to Administration } Cluster Settings } Configuration } OAuth
1. Identity providers } Add } HTPasswd
1. Name: `Administrators`
1. Browser } adminusers.htpasswd file created above
1. Click `Add`
1. Click `View authentication conditions for reconfiguration status.`
1. Wait until "All is well"
1. Go to `User Management` } `Groups`
1. Click `admingroup`
1. Actions } Add Users
1. Add all the users created above and click `Save`

## Normal users configuration steps

1. Create one or more normal users:
    1. Generate a random password:

            cat /dev/random | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 22 | head -n 1

    1. Create/update a user password file. Replace `$PASSWORD` with the output from the previous step and update `normaluser1` with the user name you'd like. For all but the first user, remove the `-c` flag.

            htpasswd -c -B -b normalusers.htpasswd normaluser1 $PASSWORD

    1. Remember this user name and password combination somewhere.

1. In the OpenShift web console, go to Administration } Cluster Settings } Configuration } OAuth
1. Identity providers } Add } HTPasswd
1. Name: `Normal Users`
1. Browser } normalusers.htpasswd file created above
1. Click `Add`
1. Click `View authentication conditions for reconfiguration status.`
1. Wait until "All is well"

## Namespaces with quotas configuration steps

First, figure out your worker node capacity; for example:

```
$ for i in $(seq 0 2); do echo "worker${i}"; oc describe node worker${i}.example.com | grep -A 6 Capacity:; done
worker0
Capacity:
  cpu:                8
  ephemeral-storage:  261608428Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             16015788Ki
  pods:               250
worker1
Capacity:
  cpu:                8
  ephemeral-storage:  261608428Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             16015780Ki
  pods:               250
worker2
Capacity:
  cpu:                8
  ephemeral-storage:  261608428Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             16015788Ki
  pods:               250
```

Next, figure out baseline worker node resource usage; for example:

```
$ for i in $(seq 0 2); do oc describe node worker${i}.example.com | grep -A 5 "Allocated resources:"; done
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests      Limits
  --------           --------      ------
  cpu                504m (6%)     0 (0%)
  memory             2400Mi (16%)  0 (0%)
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests      Limits
  --------           --------      ------
  cpu                417m (5%)     0 (0%)
  memory             2286Mi (15%)  0 (0%)
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests      Limits
  --------           --------      ------
  cpu                748m (9%)     400m (5%)
  memory             1718Mi (11%)  512Mi (3%)
```

Subtract the baseline usage from the capacity and subtract some buffer space and that leaves you with an approximate amount of room on your worker nodes.

Each student is expected to need no more than 1 CPUs and 2GB RAM.

Based on this capacity planning, create up to the maximum number of users as described in the other sections.

Finally, create the quotas:

1. Create a namespace for a user; for example, replace `adminuser1-namespace` with the namespace name:

        oc create namespace adminuser1-namespace

1. Create a [ResourceQuota](https://kubernetes.io/docs/concepts/policy/resource-quotas/) on the namespace; for example, replace `adminuser1-resourcequota` with a user-specific name, replace `adminuser1-namespace` with the namespace name, and replace the `limits.cpu` and `limits.memory` if needed:

        printf '{"apiVersion":"v1","kind":"ResourceQuota","metadata":{"name":"%s","namespace":"%s"},"spec":{"hard":{"requests.cpu":"10m","requests.memory":"10Ki","limits.cpu":"1001m","limits.memory":"2Gi"}}}' adminuser1-resourcequota adminuser1-namespace | oc create -f -

1. Create a [LimitRange](https://kubernetes.io/docs/concepts/policy/limit-range/) to control the quota for each pod that doesn't have specified limits; for example, replace `adminuser1-limitrange` with a user-specific name, replace `adminuser1-namespace` with the namespace name, and replace the limits in `default` if needed:

        printf '{"apiVersion":"v1","kind":"LimitRange","metadata":{"name":"%s","namespace":"%s"},"spec":{"limits":[{"defaultRequest":{"cpu":"1m","memory":"1Ki"},"default":{"cpu":"500m","memory":"1Gi"},"type":"Container"}]}}' adminuser1-limitrange adminuser1-namespace | oc create -f -

### Automating quota creation

```
USERS=30
for USER in $(seq 1 $USERS); do oc create namespace adminuser${USER}-namespace && printf '{"apiVersion":"v1","kind":"ResourceQuota","metadata":{"name":"%s","namespace":"%s"},"spec":{"hard":{"requests.cpu":"10m","requests.memory":"10Ki","limits.cpu":"1001m","limits.memory":"2Gi"}}}' adminuser${USER}-resourcequota adminuser${USER}-namespace | oc create -f - && printf '{"apiVersion":"v1","kind":"LimitRange","metadata":{"name":"%s","namespace":"%s"},"spec":{"limits":[{"defaultRequest":{"cpu":"1m","memory":"1Ki"},"default":{"cpu":"500m","memory":"1Gi"},"type":"Container"}]}}' adminuser${USER}-limitrange adminuser${USER}-namespace | oc create -f -; done
```

### Automating destroying namespaces

```
USERS=30
for USER in $(seq 1 $USERS); do oc delete namespace adminuser${USER}-namespace; done
```

## Updating an htpasswd file

1. In the OpenShift web console, go to Administration } Cluster Settings } Configuration } OAuth
1. Click on the `YAML` tab
1. Find the section with the target htpasswd name (e.g. `Administrators`, `Normal Users`, etc.); for example:

            - htpasswd:
                fileData:
                  name: htpasswd-zxf8q
              mappingMethod: claim
              name: Administrators
              type: HTPasswd

1. In the output above, under `fileData`, take the `name` field value.
1. Replace `$NAME` both times in:
   
        oc get secret $NAME -ojsonpath={.data.htpasswd} -n openshift-config | base64 --decode > $NAME.htpasswd

1. Add more users as describe in previous sections
1. Update the htpasswd file, replacing `$NAME` as above:

        oc create secret generic $NAME --from-file=htpasswd=$NAME.htpasswd --dry-run=client -o yaml -n openshift-config | oc replace -f -

1. If users should be in a group (e.g. `Administrators`), add any new users to that group as per previous instructions.
1. If users need a namespace with a quota, create a namesapce as per previous instructions.

---

## Clean up

To start a lab from scratch, clean up a namespace as follows.

### Clean up current namespace

```
oc delete wltrace libertytrace1
oc delete wldump libertydump1
oc delete webspherelibertyapplication --all
oc delete deployment libertydiag
oc delete serviceaccount privilegedserviceaccount
```

### Clean up a specific namespace

Replace `$NAMESPACE` with the target namespace. Some of these commands will return errors if such resources no longer exist, and that is expected.

```
oc delete wltrace libertytrace1 --namespace $NAMESPACE
oc delete wldump libertydump1 --namespace $NAMESPACE
oc delete webspherelibertyapplication --all --namespace $NAMESPACE
oc delete deployment libertydiag --namespace $NAMESPACE
oc delete serviceaccount privilegedserviceaccount --namespace $NAMESPACE
```

### Automating cleaning up namespaces

```
oc delete wltrace --all --all-namespaces
oc delete wldump --all --all-namespaces
oc delete webspherelibertyapplication --all --all-namespaces
USERS=30
for USER in $(seq 1 $USERS); do oc delete all --all --namespace adminuser${USER}-namespace; oc delete serviceaccount privilegedserviceaccount --namespace adminuser${USER}-namespace; done
```
