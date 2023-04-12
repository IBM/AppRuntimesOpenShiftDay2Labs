# Frequently Asked Questions (FAQ)

## What causes the error 'dial tcp: lookup api.... on ...: no such host - verify you have provided the correct host and port and that the server is currently running.'

Internal test clusters may not publish their API endpoints to DNS. Replace the host name in the login command with the IP address of the API endpoint provided by your cluster administrator; for example, replace the following

```
oc login --token=... --server=https://api...
```

With:

```
oc login --token=... --server=https://10.20.30...
```

## What causes the error 'The server uses a certificate signed by unknown authority. You may need to use the --certificate-authority flag to provide the path to a certificate file for the certificate authority, or --insecure-skip-tls-verify to bypass the certificate check and use insecure connections.'?

Internal test clusters may have self-signed certificates. Add `--insecure-skip-tls-verify` to the login command; for example:

```
oc login --insecure-skip-tls-verify --token=... --server=...
```

## What causes the 'x509: “kube-apiserver-lb-signer” certificate is not trusted' error?

This is a [known issue on macOS](https://bugzilla.redhat.com/show_bug.cgi?id=2097830) so upgrade your `oc` client:

1. [macOS on Intel](https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/openshift-client-mac.tar.gz)
    * On macOS, you may need to remove the download quarantine before extracting the file. Open `Terminal`, change directory to where you downloaded the file and run:

            xattr -d com.apple.quarantine openshift*

1. [macOS on ARM/AArch](https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/openshift-client-mac-arm64.tar.gz)
    * On macOS, you may need to remove the download quarantine before extracting the file. Open `Terminal`, change directory to where you downloaded the file and run:

            xattr -d com.apple.quarantine openshift*

## What causes the error "cannot be opened because the developer cannot be verified"?

Executables you download from the internet such as `oc`, `containerdiag.sh`, etc. may fail to run on macOS with this error. To resolve it, open a `Terminal`, change directory to where the executable is and run the following command, replacing `$FILE` with the executable name:

```shell
xattr -d com.apple.quarantine $FILE
```

## What causes `unexpected EOF` during `oc cp`?

This is an undiagnosed, transient error. Please simply retry. If it happens often, we'll need to debug it.

## What causes `oc get route [...] .spec.host` to return a truncated URL?

This is an undiagnosed, transient error. Re-run. The URL should end with `/`.

## What causes `must specify one of -f and -k` and `error: unknown command "token prometheus-k8s"`?

The command `oc create token prometheus-k8s` is a new command in recent versions of `oc` so upgrade your `oc` client:

1. [macOS on Intel](https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/openshift-client-mac.tar.gz)
    * On macOS, you may need to remove the download quarantine before extracting the file. Open `Terminal`, change directory to where you downloaded the file and run:

            xattr -d com.apple.quarantine openshift*

1. [macOS on ARM/AArch](https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/openshift-client-mac-arm64.tar.gz)
    * On macOS, you may need to remove the download quarantine before extracting the file. Open `Terminal`, change directory to where you downloaded the file and run:

            xattr -d com.apple.quarantine openshift*
