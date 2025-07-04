# DevOps Project

This repository contains a complete DevOps setup for deploying a Python Flask application using modern DevOps practices.

## Features
- **GitLab CI/CD** builds & deploys via Kaniko
- **Kubernetes** with staging & production namespaces
- **ArgoCD** for GitOps deployments
- **SQLite (dev)** & **PostgreSQL (prod/stage)**
- **Grafana/Prometheus** monitoring

## Structure
- `ci-cd/` - CI/CD scripts and Dockerfile
- `k8s/` - Kubernetes manifests for staging, production, ArgoCD, ingress, and database
- `app/` - Flask application source code
- `.gitlab-ci.yml` - GitLab pipeline configuration

## Manual Sync

ArgoCD is configured in **manual sync mode** for safer deployment controls.
