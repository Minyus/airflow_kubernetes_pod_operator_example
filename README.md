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

### 4. Set up a Kubernetes cluster.

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

### 5. Set up pulling a Docker image

- The example DAG code (`helm_airflow_mnt/dags/k8s_pod_op_dag.py`) pulls images which do not require authentication.

  Proceed to the next step if you want to try KubernetesPodOperator without using your Docker image (recommended if this is your first time to try the Airflow Helm Chart).

- To use another Docker image, modify the image defined in the DAG code. If your image requires authentication to pull from the registry, open `setup.sh` and specify the credentials, for example:

  ```bash
  docker_server="https://index.docker.io/v1/"
  docker_username="example-username"
  docker_password="example-password"
  docker_email="my-name@example.com"
  ```

### 6. Install stable/airflow Helm chart to "airflow" namespace, set up "airflow-tasks" namespace, and create secret to pull images.

```bash
$ bash setup.sh
```

### 7. Wait for a minute or so until the status of all of the 6 Airflow pods become `Running`.

```bash
$ kubectl get po -n airflow
```

### 8. Access the Airflow Web UI using a web browser:

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
