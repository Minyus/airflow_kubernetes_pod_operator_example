from datetime import datetime, timedelta
import yaml
from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.kubernetes.volume import Volume


def get_kubernetes_args(pod_yaml: str):
    """
    function prepared as
    pod_template_file arg could not be used due to the issue:
    https://github.com/apache/airflow/issues/10037
    """

    d = yaml.safe_load(pod_yaml)

    metadata = d["metadata"]
    spec = d["spec"]
    container = spec["containers"][0]

    volumes = []
    for vd in spec.get("volumes", []):
        name = vd.pop("name")
        v = Volume(name=name, configs=vd)
        volumes.append(v)

    kubernetes_args = dict(
        in_cluster=True,
        name=metadata.get("name"),
        namespace=metadata.get("namespace"),
        service_account_name=spec.get("serviceAccountName", "default"),
        image_pull_secrets=spec.get("imagePullSecrets"),
        hostnetwork=spec.get("hostNetwork"),
        affinity=spec.get("affinity"),
        node_selectors=spec.get("nodeSelector"),
        tolerations=spec.get("tolerations"),
        priority_class_name=spec.get("priorityClassName"),
        volumes=volumes,
        init_containers=spec.get("initContainers"),
        image=container.get("image"),
        cmds=container.get("command"),
    )
    return kubernetes_args


pod_yaml = """
apiVersion: v1
kind: Pod
metadata:
  name: pod-001
  namespace: airflow-tasks
spec:
  serviceAccountName: airflow-tasks
  imagePullSecrets:
  hostNetwork:
  affinity:
  nodeSelector:
  tolerations:
  priorityClassName:
  restartPolicy: Never
  volumes:
    - name: tmp-dir
      emptyDir: {}
  initContainers:
    - name: container-1
      image: gcr.io/gcp-runtimes/ubuntu_16_0_4:0dfb79fb3719cc17532768e27fd3f9648da4b9a5
      command:
        - bash
        - -c
        - echo "foobar" > /tmp/input_data
      volumeMounts:
        - name: tmp-dir
          mountPath: /tmp
      env:
      resources:
        limits:
          memory: 1G
          cpu: 2
    - name: container-2
      image: gcr.io/google-containers/python:3.5.1-slim
      command:
        - python
        - -c
        - >
          data = open('/tmp/input_data').read(); 
          open('/tmp/output_data','w').write(data);
      volumeMounts:
        - name: tmp-dir
          mountPath: /tmp
      env:
      resources:
        limits:
          memory: 1G
          cpu: 2
    - name: container-3
      image: gcr.io/gcp-runtimes/ubuntu_16_0_4:0dfb79fb3719cc17532768e27fd3f9648da4b9a5
      command:
        - bash
        - -c
        - cp /tmp/output_data /tmp/output_data_copied
      volumeMounts:
        - name: tmp-dir
          mountPath: /tmp
      env:
      resources:
        limits:
          memory: 1G
          cpu: 2
    - name: container-4
      image: gcr.io/gcp-runtimes/ubuntu_16_0_4:0dfb79fb3719cc17532768e27fd3f9648da4b9a5
      command:
        - bash
        - -c
        - >
          echo "[Contents of the temporal directory]" 
          && ls -la /tmp 
      volumeMounts:
        - name: tmp-dir
          mountPath: /tmp
  containers:
    - name: no-op
      image: gcr.io/gcp-runtimes/ubuntu_16_0_4:0dfb79fb3719cc17532768e27fd3f9648da4b9a5
      command:
        - bash
        - -c
        - echo "Pod completed."
"""

# Reference: https://kubernetes.io/docs/concepts/workloads/pods/init-containers/

kubernetes_args = get_kubernetes_args(pod_yaml)

default_args = dict(
    owner="airflow",
    depends_on_past=False,
    start_date=datetime(2020, 7, 10),
    email=["example@example.com"],
    email_on_failure=False,
    email_on_retry=False,
    retries=1,
    retry_delay=timedelta(seconds=60),
)

dag = DAG(
    dag_id="k8s_pod_op_dag_001",
    default_args=default_args,
    schedule_interval=timedelta(seconds=60),
    catchup=False,
)

t1 = KubernetesPodOperator(
    dag=dag,
    task_id="k8s_pod_op_task_001",
    startup_timeout_seconds=120,
    do_xcom_push=False,  # xcom_push renamed to do_xcom_push in Airflow 1.10.11
    log_events_on_failure=True,
    **kubernetes_args
)
