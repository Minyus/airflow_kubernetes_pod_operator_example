# Airflow KubernetesPodOperator Example

An example set up to use 
[Airflow's KubernetesPodOperator](https://airflow.apache.org/docs/stable/_api/airflow/contrib/operators/kubernetes_pod_operator/index.html#airflow.contrib.operators.kubernetes_pod_operator.KubernetesPodOperator._set_resources) in a laptop (macOS or Windows) or an on-premise machine (Linux) running a single-node Kubernetes cluster for development or testing.

1. Clone this repository and cd into it. 

```bash
$ git clone https://github.com/Minyus/airflow_kubernetes_pod_operator_example.git
$ cd airflow_kubernetes_pod_operator_example
```

2. If you have not installed kubectl, [install kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/). If Homebrew is available, you can run:

```bash
$ brew install kubectl
```

3. 

  - Set up a single-node Kubernetes cluster:

    1. [install Docker Desktop](https://docs.docker.com/desktop/#download-and-install)
    2. [install kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) (Kubernetes IN Docker)
    3. run:

    ```bash
    $ kind create cluster --config kind_config.yml
    ```

  - Alternatively, if you already have a single-node Kubernetes cluster and want to use it, copy the contents of `helm_airflow_mnt` directory to `/opt/airflow/efs` directory in the machine running the cluster.


4. If you have not installed helm, [install helm](https://helm.sh/docs/intro/install/) by running: 

```bash
$ curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
```

5. If you have not added "stable" helm repository, run:

```bash
$ helm repo add stable https://kubernetes-charts.storage.googleapis.com/
```

6. Create "airflow" namespace in the Kubernetes cluster by running:

```bash
$ kubectl create ns airflow
```

7. Install airflow helm chart by running:

```bash
$ helm repo update
$ helm install "airflow" stable/airflow --version "7.2.0" --namespace "airflow" --values helm_airflow_values.yml
```

8. Wait for a minute or so until the status of the pods become `Running`.

```bash
$ kubectl get all -n airflow
```

9. Set up port-forwarding by running either:

  - One-liner

    ```bash
    $ kubectl port-forward --namespace airflow $(kubectl get pods --namespace airflow -l "component=web,app=airflow" -o jsonpath="{.items[0].metadata.name}") 8080:8080
    ```

  - Using a variable

    ```bash
    $ POD_NAME=$(kubectl get pods --namespace airflow -l "component=web,app=airflow" -o jsonpath="{.items[0].metadata.name}")
    $ kubectl port-forward --namespace airflow $POD_NAME 8080:8080
    ```
  
  - Using `!!` (repeat previous command)

    ```bash
    $ kubectl get pods --namespace airflow -l "component=web,app=airflow" -o jsonpath="{.items[0].metadata.name}"
    $ kubectl port-forward --namespace airflow $(!!) 8080:8080
    ```

10. Open a web browser and access http://localhost:8080/ to open the Airflow GUI.

11. DAGs defined in `helm_airflow_mnt/dags` directory will appear in the Airflow GUI. Turn on the DAG. The logs will be saved in `helm_airflow_mnt/logs` directory.

## To use your Docker image

The example DAG code (`helm_airflow_mnt/dags/k8s_pod_op_dag.py`) pulls an image which does not require authentication.

```python
...
image="gcr.io/gcp-runtimes/ubuntu_18_0_4",
...
```

If your image requires authentication, you need to set the name of your secret created in your Kubernetes cluster, for example:

```python
...
image_pull_secrets="my-image-pull-secret",
...
image="docker.io/pytorch/pytorch:1.5.1-cuda10.1-cudnn7-runtime",
...
```

You can create a secret in your Kubernetes cluster using kubectl, for example:

```bash
$ kubectl create secret docker-registry \
    my-image-pull-secret \
    -n airflow \
    --docker-server=https://index.docker.io/v1/ \
    --docker-username=my-username \
    --docker-password=my-password \
    --docker-email=my-name@example.com
```

## Reference

- https://airflow.apache.org/docs/stable/_api/airflow/contrib/operators/kubernetes_pod_operator/index.html#airflow.contrib.operators.kubernetes_pod_operator.KubernetesPodOperator._set_resources

- https://github.com/helm/charts/tree/master/stable/airflow#option-2a----single-pvc-for-dags--logs

- https://cloud.google.com/composer/docs/how-to/using/using-kubernetes-pod-operator

- https://kubernetes.io/blog/2018/06/28/airflow-on-kubernetes-part-1-a-different-kind-of-operator/#using-the-kubernetes-operator

- https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/
