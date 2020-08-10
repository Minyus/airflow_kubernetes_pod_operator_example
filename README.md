# Airflow KubernetesPodOperator Example

An example set up to use 
[Airflow's KubernetesPodOperator](https://airflow.apache.org/docs/stable/_api/airflow/contrib/operators/kubernetes_pod_operator/index.html#airflow.contrib.operators.kubernetes_pod_operator.KubernetesPodOperator._set_resources) in a laptop (macOS or Windows) or an on-premise machine (Linux) running a single-node Kubernetes cluster for development or testing.

### 1. Clone this repository and cd into it. 

```bash
$ git clone https://github.com/Minyus/airflow_kubernetes_pod_operator_example.git
$ cd airflow_kubernetes_pod_operator_example
```

### 2. Install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) if you haven't. Homebrew can be used if available.

```bash
$ brew install kubectl
```

### 3. Install [helm](https://helm.sh/docs/intro/install/) if you haven't. 

```bash
$ curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
```

### 4. Add "stable" helm repository if you haven't.

```bash
$ helm repo add stable https://kubernetes-charts.storage.googleapis.com/
```

### 5. Set up a Kubernetes cluster.

  - [Option 1: create a new cluster using `kind`] (recommended for initial prototyping)

    1. Install [Docker Desktop](https://docs.docker.com/desktop/#download-and-install) if you haven't
    2. Install [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) (Kubernetes IN Docker) if you haven't
    3. Create a cluster by running:

    ```bash
    $ kind create cluster --config kind_config.yml
    ```

  - [Option 2: use a cluster already created] (recommended *after* finishing initial prototyping)
    
    1. copy the contents of `helm_airflow_mnt` directory to `/opt/airflow/efs` directory in the machine running the cluster. 
    2. If your Kubernetes cluster consists of multiple nodes, configure in `helm_airflow_values.yml` as follows.
      - [Option A] run Airflow pods in a specific node using `nodeSelector` or `affinity`; or
      - [Option B] set up a Persistent Volume with `ReadWriteMany` support instead of `hostPath`

### 6. Create "airflow" namespace in the Kubernetes cluster, install stable/airflow Helm chart, and wait for a minute or so until the status of the pods become `Running`.

```bash
$ kubectl create ns airflow 
  helm repo update 
  helm install "airflow" stable/airflow --version "7.3.0" --namespace "airflow" --values helm_airflow_values.yml 
  kubectl get po -n airflow --watch
```

To stop watching by `--watch` option, hit `Ctrl + C`.

### 7. Set up pulling a Docker image

- The example DAG code (`helm_airflow_mnt/dags/k8s_pod_op_dag.py`) pulls images which do not require authentication.

  Proceed to step 9 if you want to try KubernetesPodOperator without using your Docker image (recommended if this is your first time to try the Airflow Helm Chart).

- To use another Docker image, modify the image defined in the DAG code.

### 8. If your image requires authentication to pull from the registry, you need to set up the secret.

#### 8.1. Create a secret in your Kubernetes cluster using kubectl, for example:

  ```bash
  $ kubectl create secret docker-registry \
      my-image-pull-secret \
      -n airflow \
      --docker-server=https://index.docker.io/v1/ \
      --docker-username=my-username \
      --docker-password=my-password \
      --docker-email=my-name@example.com
  ```

  #### 8.2. Configure to enable the pod to use the secret to pull images as follows:
  
  - [Option I] Service Account specified in the DAG code as `serviceAccountName`: 

    ```bash
    $ kubectl patch sa airflow -n airflow -p '{\"imagePullSecrets\": [{\"name\": \"my-image-pull-secret\"}]}'
    ```

  - [Option II] Pod in the DAG code:

    ```yaml
    ...
    imagePullSecrets: "my-image-pull-secret"
    ...
    ```

### 9. Access the Airflow Web UI using a web browser:

  - If you chose [Option 1: create a new cluster using `kind`]:
  
    Access http://localhost:8080/
  
    DAGs defined in `helm_airflow_mnt/dags` directory will appear in the Airflow GUI. 
    The logs will be saved in `helm_airflow_mnt/logs` directory.
  
  - If you chose [Option 2: use a cluster already created]:
  
    Access http://$IP_ADDRESS_OF_A_NODE:30080/

    You can check the IP address of a node by running:

    ```
    $ kubectl get nodes -n airflow -o jsonpath="{.items[0].status.addresses[0].address}"
    ```

## Reference

- https://airflow.apache.org/docs/stable/_api/airflow/contrib/operators/kubernetes_pod_operator/index.html#airflow.contrib.operators.kubernetes_pod_operator.KubernetesPodOperator._set_resources

- https://github.com/helm/charts/tree/master/stable/airflow#option-2a----single-pvc-for-dags--logs

- https://cloud.google.com/composer/docs/how-to/using/using-kubernetes-pod-operator

- https://kubernetes.io/blog/2018/06/28/airflow-on-kubernetes-part-1-a-different-kind-of-operator/#using-the-kubernetes-operator

- https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/

- https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/#add-imagepullsecrets-to-a-service-account

- https://kubernetes.io/docs/concepts/workloads/pods/init-containers/
