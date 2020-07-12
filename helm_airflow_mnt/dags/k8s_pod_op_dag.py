from datetime import datetime, timedelta

from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator

kubernetes_args = dict(
    in_cluster=True,
    namespace="airflow",
    service_account_name="airflow",
    image_pull_secrets=None,
)

default_args = dict(
    owner="airflow",
    depends_on_past=False,
    start_date=datetime(2020, 7, 10),
    email=["airflow@airflow.com"],
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
    name="k8s_pod_op_001",
    xcom_push=False,
    image="gcr.io/gcp-runtimes/ubuntu_18_0_4",
    cmds=["echo"],
    **kubernetes_args
)
