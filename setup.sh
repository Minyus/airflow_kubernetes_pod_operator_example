#!/bin/bash

airflow_chart_values="airflow_chart_values.yml"
airflow_chart_version="7.4.1"
airflow_ns="airflow"
airflow_tasks_ns="airflow-tasks"

docker_server="" 
docker_username=""
docker_password=""
docker_email=""

#############################################

set -eu

[[ ! -f "$airflow_chart_values" ]] && echo "$airflow_chart_values"" cannot be found." && exit 1

kubectl create ns "$airflow_ns" 
helm repo add stable https://kubernetes-charts.storage.googleapis.com/ 
helm repo update 
helm install "airflow" "stable/airflow" \
    --version "$airflow_chart_version" \
    --namespace "$airflow_ns" \
    --values "$airflow_chart_values"

for ns in $airflow_tasks_ns
do
kubectl create ns "$ns" 
kubectl create role "airflow-tasks" -n "$ns" \
    --verb=create,get,list \
    --resource=pods,pods/log,pods/exec 
kubectl create rolebinding "system-airflow-tasks" -n "$ns" \
    --role="airflow-tasks" \
    --serviceaccount="$airflow_ns":"airflow" 
kubectl create sa "airflow-tasks" -n "$ns" 
kubectl create rolebinding "airflow-tasks" -n "$ns" \
    --role="airflow-tasks" \
    --serviceaccount="$ns":"airflow-tasks"

if [[ -n "$docker_server" ]]; then
    kubectl create secret docker-registry "task-image-pull-secret" -n "$ns" \
        --docker-server="$docker_server" \
        --docker-username="$docker_username" \
        --docker-password="$docker_password" \
        --docker-email="$docker_email"
    patch_yaml=$(cat \
<<HEREDOC
imagePullSecrets:
    - name: task-image-pull-secret
HEREDOC
        )
    kubectl patch sa "airflow-tasks" -n "$ns" \
        -p "$patch_yaml"
fi

done
