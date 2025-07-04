# DevOps Project

This repository contains a complete DevOps setup for deploying a Python Flask application using modern DevOps practices.

## Features

- **GitLab CI/CD**: Automated pipeline for testing, building, and deploying Docker images.
- **Kaniko**: Secure, in-cluster Docker image builds without requiring Docker daemon.
- **Kubernetes**: Separate staging & production environments with namespaces.
- **PostgreSQL & SQLite**: Uses SQLite locally, PostgreSQL in staging/production.
- **ArgoCD**: GitOps-driven continuous delivery to Kubernetes.
- **Ingress**: Exposes services using NGINX ingress controller.
- **Monitoring**: Grafana for cluster observability.

## Structure

- `ci-cd/` - CI/CD scripts and Dockerfile
- `k8s/` - Kubernetes manifests for staging, production, ArgoCD, ingress, and database
- `app/` - Flask application source code
- `.gitlab-ci.yml` - GitLab pipeline configuration

## Manual Sync

ArgoCD is configured in **manual sync mode** for safer deployment controls.
