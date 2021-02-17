# BigBang Template

This folder contains a template that you can replicate in your own Git repo to get started with Big Bang configuration.

The main benefits of this template include:

- Isolation of the Big Bang product and your custom configuration
  - Allows you to easily consume upstream Big Bang changes since you never change the product
  - Big Bang product tags are explicitly referenced in your configuration, giving you control over upgrades
- [GitOps](https://www.weave.works/technologies/gitops/) for your deployments configrations
  - Single source of truth for the configurations deployed
  - Historical tracking of changes made
  - Allows tighter control of what is deployed to production (via merge requests)
  - Enables use of CI/CD pipelines to test prior to deployment
  - Avoids problem of `helm upgrade` using `values.yaml` that are not controlled
  - Allows you to limit access to production Kubernetes cluster since all changes are made via Git
- Shared configurations across deployments
  - Common settings across deployments (e.g. dev, staging, prod) can be configured in one place
  - Secrets (e.g. pull credentials) can be shared across deployments.  NOTE:  SOPS supports multiple keys for encrypting the same secret so that each environment can use a different SOPS key.

### Prerequisites

To deploy Big Bang, the following items are required:

- Kuberntes cluster
- A git repo for your configuration
- [Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [GPG](https://gnupg.org/index.html)
- [SOPS](https://github.com/mozilla/sops)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Iron Bank Personal Access Token](https://registry1.dso.mil) - Under your `User Profile`, copy the `CLI secret`.
- [Repo1 Personal Access Token](https://repo1.dso.mil/-/profile/personal_access_tokens) - You will need `api` and `write_repository` permissions.

In addition, the following items are recommended to assist with troubleshooting:
- [Helm](https://helm.sh/docs/intro/install/)
- [Kustomize](https://kubectl.docs.kubernetes.io/installation/kustomize/)
- [K9S](https://github.com/derailed/k9s)
## Quick Start

The `quickstart` folder contains a simplistic Big Bang deployment to help you deploy your first Big Bang.

### One-time Setup

1. For this quickstart, we will work off of a branch in the template repo.  For production, it is recommended that you create your own Git repo for storing configuration.

   ```bash
   git checkout -b ${USER}-quickstart
   ```

2. To make sure your pull secrets are not comprimized when uploaded to Git, you must generate your own encryption key:

   ```bash
   # Import Big Bang's development key for decrypting existing secrets:
   curl https://repo1.dso.mil/platform-one/big-bang/bigbang/-/raw/master/hack/bigbang-dev.asc | gpg --import

   # Generate a GPG master key
   # The key fingerprint will be stored in the $fp variable
   fp=`gpg --quick-generate-key bigbang-sops rsa4096 encr | sed -e 's/ *//;2q;d;'`
   gpg --quick-add-key ${fp} rsa4096 encr

   # Rekey your secret
   # This ensures your secrets are only decryptable by your key
   sed -i "s/pgp: 41BFF8BAF2586039F6293D835A2E820C25FE527C/pgp: ${fp}/" ../.sops.yaml
   sops updatekeys secrets.enc.yaml -y
   sops updatekeys ingress-cert.enc.yaml -y
   ```

3. Add pull secrets for Iron Bank and Repo1

   ``` bash
   # Add pull secrets to secrets.enc.yaml
   # Put your Iron Bank user/PAT where it states "replace-with-your-iron-bank-user" and "replace-with-your-iron-bank-personal-access-token"
   # Similarly, put your repo1 user/PAT in place
   sops secrets.enc.yaml

   # Save secrets into Git
   # Configuration changes must be stored in Git to take affect
   # Note that your secrets are encrypted
   git add secrets.enc.yaml ../.sops.yaml
   git commit -m "test(quickstart): updated encryption keys"
   git push
   ```

4. Reference your Git repository and branch by editing the `GitRepository` resource in `bigbang.yaml`:

   ```yaml
   apiVersion: source.toolkit.fluxcd.io/v1beta1
   kind: GitRepository
   metadata:
     name: environment-repo
     namespace: bigbang
   spec:
     interval: 1m
     url: https://repo1.dsop.io/platform-one/big-bang/customers/template.git
     ref:
        branch: <YOUR USER>-quickstart
   ```

### Deployment

1. Deploy private key for Big Bang to decrypt secrets

   ```bash
   # The private key is not stored in Git, so we must deploy it manually
   kubectl create namespace bigbang
   gpg --export-secret-key --armor ${fp} | kubectl create secret generic sops-gpg -n bigbang --from-file=bigbangkey=/dev/stdin
   ```

1. Deploy flux to handle syncing

   ```bash
   # Flux is used to sync Git with the the cluster configuration
   kubectl create namespace flux-system
   curl https://repo1.dso.mil/platform-one/big-bang/umbrella/-/raw/master/scripts/deploy/flux.yaml | kubectl apply -f -

   # Wait for flux to complete
   kubectl get deploy -o name -n flux-system | xargs -n1 -t kubectl rollout status -n flux-system
   ```

1. Deploy Big Bang

   ```bash
   # The quickstart configuration will deploy istio, gatekeeper, twistlock, and kiali
   kubectl apply -f bigbang.yaml

   # Watch deployment
   # NOTE: The Kustomization resource may fail at first with an error about the istio-system namespace.  This is normal since the Helm Release for istio will create that namespace and it has not run yet.  This should resolve itself within a few minutes
   watch kubectl get gitrepositories,kustomizations,hr,po -A

   # Test deployment by opening a browser to "kiali.bigbang.dev" to get to the Kiali application deployed by Istio.
   # Note that the owner of "bigbang.dev" has setup the domain to point to 127.0.0.1 for this type of testing.
   ```

You now have successfully deployed the quickstart Big Bang.  Your next step is to customize the configuration.  To show you how this is done, let's enable Twistlock.

1. In `configmap.yaml`, enable Twistlock

   ```yaml
   twistlock:
     enabled: true
   ```

1. Push changes to Git

   ```bash
   git add configmap.yaml
   git commit -m "test(quickstart): enabled twistlock"
   git push
   ```

1. Big Bang will automatically pick up your change and make the necessary changes.

   ```bash
   # Watch deployment
   watch kubectl get gitrepositories,kustomizations,hr,po -A

   # Test deployment by opening a browser to "twistlock.bigbang.dev" to get to the Twistlock application
   ```
## Environments

To support multiple deployments to similar environments, a more complex template has been provided in the `dev`, `prod`, and `base` folders.  This template can be expanded to more environments by replicating one of the existing folders.

Each environment consists of a Kubernetes manifest (e.g. `bigbang.yaml`), a `kustomization.yaml`, and additional files used to deploy resources.  All of the environments share the `base` folder configuration, which also has a `kustomization.yaml`.

## Configuration

The configuration steps below reference the `dev` environment only.  The same steps should be take to setup additional environments (e.g. `prod`).

### Big Bang Version

To minimize the risk of an unexpected deployment of a BigBang release, the BigBang release version should be explicitly stored in the configuration files and updated during planned upgrades.

The shared default BigBang release can be modified by updating the following in `base/kustomization.yaml`:

- Reference for the Big Bang kustomize base:

  ```yaml
  bases:
  - https://repo1.dsop.io/platform-one/big-bang/umbrella.git/base/?ref=v1.0.6
  ```

- Reference for the Big Bang helm release:

   ```yaml
   apiVersion: source.toolkit.fluxcd.io/v1beta1
   kind: GitRepository
   metadata:
      name: bigbang
   spec:
      ref:
         $patch: replace
         semver: "1.0.6"
   ```

If you want to test a different Big Bang release in a specific environment, the above sections can be placed in the `kustomization.yaml` of the environment's folder to override the base settings.

It is recommended that you track Big Bang releases using the version.  However, you can use `tag` or `branch` in place of `semver` if needed.  The kustomize base uses [Go-Getter](https://github.com/hashicorp/go-getter)'s syntax for the reference.  The helm release (GitRepository) resource uses the [GitRepository CRD](https://toolkit.fluxcd.io/components/source/gitrepositories/#specification)'s syntax.

### Environment

For each environment, the following are the minimum required steps to fully configure Big Bang.  For additional configuration options, refer to the [Big Bang](https://repo1.dsop.io/platform-one/big-bang/umbrella) and [Big Bang Package](https://repo1.dsop.io/platform-one/big-bang/apps) documentation.

1. In `bigbang.yaml`
   - Update the `GitRepository` resource with your deployment's Git repository and branch.

      ```yaml
      spec:
        url: https://repo1.dsop.io/platform-one/big-bang/customers/template.git
        ref:
          branch: main
      ```

      - [Optional] if your git url is a private git repository you will need to create a `Secret` with the credentials to allow flux to clone your git repo down. More information on that can be found [here](https://toolkit.fluxcd.io/components/source/gitrepositories/#https-authentication)

   - Update the `Kustomization` resource with the path to your environment-specific [Kustomize](https://kustomize.io/) configuration.

      ```yaml
      spec:
        path: ./dev
      ```

2. In `dev/configmap.yaml`
   - Update the `hostname` variable to the domain of your deployment.

      ```yaml
      hostname: bigbang.dev
      ```

   - [Optional] Add any additional environment-specific Big Bang or package overrides.
      > NOTE: The `dev` template includes several overrides to minimize resource usage and increase polling time in a development environment.  They are provided for convenience and are NOT required.

3. [Optional] In `base/configmap.yaml`
   - Add any additional shared Big Bang or package overrides.
4. [Optional] If you need a new ConfigMap for configuration, add a new file to the appropriate folder and reference it in `kustomization.yaml`.

   ```yaml
   resources:
   - mycustomconfigmap.yaml
   ```

### Secrets

Prequisites:

- [Secrets Operations (SOPS)](https://github.com/mozilla/sops)
- [GNU Privacy Guard (GPG)](https://gnupg.org/index.html) to decode existing secret.

1. Big Bang uses [SOPS](https://github.com/mozilla/sops) to store encrypted secrets in Git.  In order for Big Bang to decrypt and deploy the serets, your private key must be stored securly and access configuration must be put in place.  Refer to the [Big Bang](https://repo1.dsop.io/platform-one/big-bang/umbrella) documentation for details on how to do this.
1. Import the [Big Bang development private key](https://repo1.dsop.io/platform-one/big-bang/umbrella/-/blob/master/hack/bigbang-dev.asc) using `gpg --import bigbang-dev.asc`
   > This key is only intended to be used to demonstrate the use of SOPS.  It is NOT a secure key and should NOT be used in production in any manner.
1. `.sops.yaml` holds the key fingerpints used for SOPS.  When you setup your encryption keys in step 1, you should have updated this file for the key management you are using.  If not, [setup .sops.yaml](https://github.com/mozilla/sops#210using-sopsyaml-conf-to-select-kmspgp-for-new-files) now.
   > The `.sops.yaml` can be setup to have different keys for `dev`, `prod` and other environments.  In this case it is important to have a `path_regex` setup for `base` that holds all keys for all environments so that secrets there can be shared.  There is an excellent tutorial on how to do this [here](https://dev.to/stack-labs/manage-your-secrets-in-git-with-sops-common-operations-118g).

1. Re-encrypt `secrets.enc.yaml` with your SOPS keys.  This will decrypt the file with the Big Bang development private key and re-encrypt with your keys.

   ```bash
   sops updatekeys base/secrets.enc.yaml -y
   sops updatekeys dev/secrets.enc.yaml -y
   ```

1. Decrypt and update your [Iron Bank](registry1.dsop.io) pull credentials in `base/secrets.enc.yaml`

   ```bash
   sops base/secrets.enc.yaml
   ```

   > If you get an error decrypting, run `GPG_TTY=$(tty) && export GPG_TTY` and try to open the file again.

   ```yaml
   stringData:
      values.yaml: |-
         registryCredentials:
        - registry: registry1.dsop.io
          username: replace-with-your-iron-bank-user
          password: replace-with-your-iron-bank-personal-access-token
        - registry: registry1.dso.mil
          username: replace-with-your-iron-bank-user
          password: replace-with-your-iron-bank-personal-access-token
        - registry: registry.dso.mil
          username: replace-with-your-repo1-user
          password: replace-with-your-repo1-personal-access-token
        - registry: registry.dsop.io
          username: replace-with-your-repo1-user
          password: replace-with-your-repo1-personal-access-token
   ```

   Saving the file automatically re-encrypts it for all of the keys.

1. [Optional] In either `base/secrets.enc.yaml` or `dev/secrets.enc.yaml`
   - Add any additional secret overrides for Big Bang or packages.
   - For example, certificates or authentication server details
1. [Optional] If you need a new Secret for configuration, create and edit a new file using `sops`.  Then, reference it in `kustomization.yaml`.

   ```yaml
   resources:
   - mycustomsecret.enc.yaml
   ```

## Deploy

Big Bang follows a [GitOps](https://www.weave.works/blog/what-is-gitops-really) approach to deployment.  All configuration changes will be pulled and reconciled with what is stored in the Git repository.  The only exception to this is the initial manifests (e.g. `bigbang.yaml`) which points to the Git repository and path to start from.

1. Commit and push all changes made during configuration to Git
1. Double check you are pointing to the correct Kubernetes cluster

   ```bash
   kubectl config current-context
   ```

1. Deploy the Big Bang manifest to the cluster

   ```bash
   kubectl apply -f bigbang.yaml
   ```

1. Watch the deployment for problems

   ```bash
   # Verify 'bigbang' namespace is created
   kubectl get namespaces

   # Verify Pull from Git was successful
   kubectl get gitrepositories -A

   # Verify Big Bang config maps (x2) and secrets (x2) are deployed
   kubectl get -n bigbang secrets,configmaps,kustomizations

   # Verify Big Bang is successfully deploying pods
   watch kubectl get po,hr,kustomizations -A
   ```

   For troubleshooting, refer to the [Big Bang](https://repo1.dsop.io/platform-one/big-bang/umbrella) documentation.

## Updates

It is likely that you will want to make changes to the `dev` environment first and then propagate to other environments.  You can add changes to the `dev` folder without affecting other environments.  And, you can override settings in the `base` folder within the `dev` configuration using [Kustomize patching](https://kubectl.docs.kubernetes.io/references/kustomize/patches/).

After making your configuration changes for `dev`, make sure to modify the appropriate Git reference for the branch, tag, or semver you are testing.  Upon pushing the changes to Git, Big Bang will automatically reconcile the configuration.
   > It may take Big Bang up to 10 minutes to recognize your changes and start to deploy them.  This is based on the interval set for polling.  You can force Big Bang to recheck by running the [sync.sh](https://repo1.dsop.io/platform-one/big-bang/umbrella/-/blob/master/hack/sync.sh) script.

Once you have tested in one environment, you can repeat the above steps for each additional environment you want to test.  When you are ready to deploy to production, you can modify settings in the `base` directory and remove overrides from the specific environments.
