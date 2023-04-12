# Lab: InstantOn

This lab covers how to run a Liberty InstantOn container and investigate issues with InstantOn.

## Theory

Liberty [InstantOn](https://developer.ibm.com/blogs/liberty-instanton-serverless-for-java-without-compromise/) is a capability of Liberty (along with technology in IBM Semeru Java and Linux) to dramatically reduce Liberty start-up time by up to 10-20 **times**. In the example you'll see below, startup time goes from 30-60 seconds to less than 1 second. The technology is currently in beta.

InstantOn is useful for serverless applications (where Liberty is spawned to handle a single unit of work and then destroyed) but it's also useful for traditional, long-running application scenarios. For example, Kubernetes deployments can be configured to auto-scale based on workload, both down to 0 pods during periods of inactivity (e.g. at night when there may be no users) as well as increasing the number of pods during unexpected spikes of activity. In both of these cases, when a new pod is created, startup time and various caches may affect the requests during the period when new pods are being created and initialized. With InstantOn, start up time can be nearly instantaneous and thus solve those issues with cold starts.

The way InstantOn generally works in a cloud environment is that the application developer builds the application container, starts the container, and then takes a checkpoint, most often after applications have finished starting, and this checkpoint is saved into a container image. This checkpoint represents all of the memory and state of Liberty in its ready-to-serve state. Then, when a pod is started based off of this image, Liberty works with IBM Semeru Java and Linux to restore this checkpoint and prepare it for serving requests.

The most common issue with InstantOn is that a security misconfiguration causes the checkpoint restore to fail. In this case, Liberty falls back to a normal, slow start-up. Therefore, you'll go through two labs. First, we'll show InstantOn in action with everything succeeding, and then we'll show InstantOn failing the checkpoint restore and how to review the logs for what went wrong.

InstantOn in OpenShift has two different ways of running: fully privileged mode (i.e. essentially "root" mode) and non-fully privileged but increased privilege mode. For obvious reasons, it's generally more recommended to run in the latter mode because giving a container root privileges means that security risks are higher. However, running in this lower privileges mode [requires](https://blog.openj9.org/2022/10/05/deploying-on-kubernetes-and-openshift-with-openj9-criu-support/) either a Linux kernel that supports the `clone3` system call with the `set_tid` argument, or `runc` version 1.1.3 or higher. Such environments are not yet often available, so this first version of these labs will run in fully privileged mode.

## Labs

1. [Lab: InstantOn successfully working in privileged mode](#lab-instanton-successfully-working-in-privileged-mode)
1. [Lab: InstantOn failing](#lab-instanton-failing)

-----

## Lab: InstantOn successfully working in privileged mode

### Step 1: Create a ServiceAccount

We will run the pod under the authority of a ServiceAccount to which we will associate elevated privileges.

<details markdown="1" open>
<summary>Using the command line</summary>

1. If you haven't already, [download the `oc` executable and log into your OpenShift console through the command line](openshift_login_commandline.md)
1. Create the service account:

        oc create serviceaccount privilegedserviceaccount

1. Associate the service account with the `privileged` security context constraint (SCC):

        oc adm policy add-scc-to-user privileged -z privilegedserviceaccount

</details>

### Step 2: Install example application

1. [Uninstall](lab_liberty_uninstall_app.md) any previously installed sample application.
1. Re-install the sample application using [a basic Kubernetes Deployment](lab_liberty_install_app.md#install-using-a-basic-kubernetes-deployment).

### Step 3: Test InstantOn

First you will see how long it took to start a non-InstantOn application. Then you will delete that and install an InstantOn application for comparison.

<details markdown="1" open>
<summary>Using the command line</summary>

1. List the pods; for example:

        oc get pods
   Example output:

        NAME                          READY   STATUS    RESTARTS   AGE
        libertydiag-b98748954-mgj64   1/1     Running   0          97s

1. Execute a remote search in the pod for the `CWWKZ0001I: Application libertydiag started` message by replacing `$POD` with a pod name from the previous command:

        oc exec $POD -- grep CWWKZ0001I /logs/messages.log
   For example:

        $ oc exec libertydiag-59d59c5dbc-sghwt -- grep CWWKZ0001I /logs/messages.log
        [12/12/22, 20:00:55:275 UTC] 0000002e com.ibm.ws.app.manager.AppMessageHelper   A         CWWKZ0001I: Application libertydiag started in 39.409 seconds.

1. Notice that the application took many dozens of seconds to start. In the above example, it took about 40 seconds.
1. Next, we'll delete this deployment and create an InstantOn deployment.
1. Delete the current deployment.

        oc delete deployment libertydiag

1. Wait about 5 seconds for the deployment to finish deleting. Confirm it's not in the resulting list of all deployments:

        oc get deployments
   Example output:

        No resources found in user1-namespace namespace.

1. Create a `libertydiaginstanton.yaml` file with the following contents:

        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: libertydiag
        spec:
          replicas: 1
          selector:
            matchLabels:
              name: libertydiag
          template:
            metadata:
              labels:
                name: libertydiag
            spec:
              serviceAccountName: privilegedserviceaccount
              containers:
                - name: libertydiag
                  image: quay.io/ibm/libertydiag:instanton
                  imagePullPolicy: Always
                  securityContext:
                    privileged: true

1. Run the YAML file:

        oc apply -f libertydiaginstanton.yaml

1. Run the following command which will wait until the deployment is ready:

        oc wait deployment libertydiag --for condition=available --timeout=5m

1. List the pods for the example application deployment; for example:

        oc get pods
   Example output:

        NAME                          READY   STATUS    RESTARTS   AGE
        libertydiag-59d59c5dbc-dbz8m  1/1     Running   0          97s

1. Execute a remote search in the pod for the `CWWKZ0001I: Application libertydiag started` message by replacing `$POD` with a pod name from the previous command:

        oc exec $POD -- grep CWWKZ0001I /logs/messages.log
   For example:

        $ oc exec libertydiag-59d59c5dbc-dbz8m -- grep CWWKZ0001I /logs/messages.log
        [12/12/22, 20:13:26:761 UTC] 0000002e com.ibm.ws.app.manager.AppMessageHelper   A           CWWKZ0001I: Application libertydiag started in 0.684 seconds.

1. This time, notice that the application started in much less time. In the above example, about half a second.

</details>

### Step 4: Clean-up

Clean-up the resources.

<details markdown="1" open>
<summary>Using the command line</summary>

1. Delete the deployment:

        oc delete deployment libertydiag

1. Delete the ServiceAccount:

        oc delete serviceaccount privilegedserviceaccount

</details>

### Summary

In summary, this lab demonstrated how to run a Liberty InstantOn image in privileged mode. It showed that Liberty startup time compared to a normal deployment was more than a magnitude faster.

-----

## Lab: InstantOn failing

This lab will demonstrate how to investigate why InstantOn failed to work. We will deliberately skip steps to mark the deployment as privileged and observe InstantOn errors.

This lab will take approximately 15 minutes.

### Step 1: Install example application

#### Install using a basic Kubernetes deployment

<details markdown="1" open>
<summary>Using the command line</summary>

1. Install the InstantOn application but without the proper privileges:

        oc create deployment libertydiag --image=quay.io/ibm/libertydiag:instanton

1. Wait two minutes for the application to initialize (the namespace may have limited CPU, so startup can take a while)
1. List the pods for the example application deployment; for example:

        oc get pods
   Example output:

        NAME                           READY   STATUS    RESTARTS   AGE
        libertydiag-596cc64bdd-rdj62   1/1     Running   0          97s

1. Print the logs of the pod by replacing `$POD` with a pod name from the previous command:

        oc logs $POD
   For example:

        oc logs libertydiag-596cc64bdd-rdj62

1. Scroll to the top of the output and observe various errors. In particular, the `CWWKE0957I` message confirms that InstantOn failed to load and that Liberty will load without InstantOn.

        /opt/ol/wlp/bin/server: line 1458: /opt/ol/wlp/output/defaultServer/workarea/checkpoint/restoreTime: Permission denied
        /opt/ol/wlp/bin/server: line 1474: /opt/ol/wlp/output/defaultServer/workarea/checkpoint/.env.properties: Permission denied
        /opt/ol/wlp/bin/server: line 1413: /usr/sbin/criu: Operation not permitted
        CWWKE0957I: Restoring the checkpoint server process failed. Check the /logs/checkpoint/restore.log log to determine why the checkpoint process was not restored. Launching the server without using the checkpoint image.

</details>

### Step 2: Clean-up

Clean-up the resources.

<details markdown="1" open>
<summary>Using the command line</summary>

1. Delete the deployment:

        oc delete deployment libertydiag

1. Delete the ServiceAccount:

        oc delete serviceaccount privilegedserviceaccount

</details>

### Summary

In summary, this lab demonstrated what to look for if InstantOn fails to load. Most commonly, this means that privileges are missing.
