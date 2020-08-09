from datetime import datetime, timedelta

from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator

from airflow.kubernetes.volume import Volume
import yaml

pod_yaml = """
apiVersion: v1
kind: Pod
metadata:
  name: pod
  namespace: airflow
spec:
  serviceAccountName: airflow
  imagePullSecrets: 
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
          echo "Keeping the temporary data for 1 day for backup." 
          && ls -lah /tmp 
          && sleep 86400
      volumeMounts:
        - name: tmp-dir
          mountPath: /tmp
  containers:
    - name: no-op
      image: gcr.io/gcp-runtimes/ubuntu_16_0_4:0dfb79fb3719cc17532768e27fd3f9648da4b9a5
"""

# pod_template_file could not be used due to the issue: https://github.com/apache/airflow/issues/10037

d = yaml.safe_load(pod_yaml)

metadata = d["metadata"]
spec = d["spec"]

volumes = []
for vd in spec["volumes"]:
    name = vd.pop("name")
    v = Volume(name=name, configs=vd)
    volumes.append(v)

kubernetes_args = dict(
    in_cluster=True,
    name=metadata["name"],
    namespace=metadata["namespace"],
    service_account_name=spec["serviceAccountName"],
    image_pull_secrets=spec["imagePullSecrets"],
    volumes=volumes,
    init_containers=spec["initContainers"],
)

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
    image="gcr.io/gcp-runtimes/ubuntu_16_0_4:0dfb79fb3719cc17532768e27fd3f9648da4b9a5",  # no-op
    **kubernetes_args,
)
