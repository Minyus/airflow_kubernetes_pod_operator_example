#!/bin/bash

kubectl create ns airflow

helm repo add stable https://kubernetes-charts.storage.googleapis.com/
helm repo update
helm install "airflow" stable/airflow --version "7.3.0" --namespace "airflow" --values helm_airflow_values.yml

kubectl create ns airflow-tasks
kubectl create role airflow-tasks -n airflow-tasks --verb=create,get,list --resource=pods,pods/log,pods/exec
kubectl create rolebinding system-airflow-tasks -n airflow-tasks --role=airflow-tasks --serviceaccount=airflow:airflow 
kubectl create sa airflow-tasks -n airflow-tasks
kubectl create rolebinding airflow-tasks -n airflow-tasks --role=airflow-tasks --serviceaccount=airflow-tasks:airflow-tasks
