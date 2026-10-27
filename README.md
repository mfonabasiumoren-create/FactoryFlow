\# FactoryFlow — FMCG Manufacturing \& Supply Chain Platform



\## Project Overview



FactoryFlow is a local-first, cloud-native portfolio project that simulates the manufacturing and supply-chain operations of a fictional fast-moving consumer goods (FMCG) company.



The project demonstrates how application development, database persistence, containerization, Kubernetes orchestration, and operational practices can work together to support a simulated FMCG environment.



\*\*Repository:\*\* https://github.com/mfonabasiumoren-create/FactoryFlow



\## Architecture



FactoryFlow currently uses the following components:



\- \*\*Application:\*\* Python Flask REST API served with Gunicorn.

\- \*\*Database:\*\* PostgreSQL for persistent application data.

\- \*\*Containerization:\*\* Docker and Docker Compose.

\- \*\*Orchestration:\*\* Kubernetes using Docker Desktop.

\- \*\*Configuration management:\*\* Kubernetes ConfigMaps and Secrets.

\- \*\*Storage:\*\* Kubernetes PersistentVolumeClaim for PostgreSQL data.

\- \*\*Networking:\*\* Kubernetes Services and NGINX Ingress.

\- \*\*Autoscaling:\*\* Horizontal Pod Autoscaler (HPA).

\- \*\*Deployment management:\*\* Kustomize.

\- \*\*Version control:\*\* Git and GitHub.



\### Request flow



A client sends an HTTP request to the FactoryFlow API through the configured Ingress route. NGINX Ingress forwards the request to the Kubernetes API Service, which directs traffic to an API pod. The API communicates with PostgreSQL through its internal Kubernetes Service.



\## Implemented Features



\### Application and database

\- Flask REST API with Gunicorn.

\- PostgreSQL database integration.

\- Product retrieval endpoint.

\- Inventory retrieval endpoint.

\- Health endpoint that checks application health and database connectivity.

\- Seed data for products, raw materials, warehouse, and inventory records.



\### Containerization and security

\- Dockerized API application.

\- Non-root container execution.

\- Read-only root filesystem.

\- Linux capabilities dropped.

\- Privilege escalation disabled.

\- Temporary writable storage configured for `/tmp`.



\### Kubernetes and operations

\- Dedicated `factoryflow` namespace.

\- API and PostgreSQL Deployments.

\- Internal ClusterIP Services.

\- PostgreSQL persistent storage configuration.

\- ConfigMap and Secret-based configuration.

\- Application health probes and resource requests/limits.

\- Horizontal Pod Autoscaler configured for CPU-based scaling.

\- NGINX Ingress routing.

\- Kustomize configuration for managing Kubernetes manifests.



\## API Endpoints



| Method | Endpoint | Purpose |

|---|---|---|

| GET | `/health` | Checks API health and database connectivity |

| GET | `/products` | Retrieves product records |

| GET | `/inventory` | Retrieves inventory records |



\### Verified results



During local Kubernetes testing, the following endpoints returned HTTP 200:



\- `/health` — reported a healthy API and connected database.

\- `/products` — returned three seeded product records.

\- `/inventory` — returned three inventory records associated with the Lagos Distribution Warehouse.



These results were verified against the local Kubernetes deployment.



\## Project Structure



```text

FactoryFlow/

├── app/

│   └── database/

│       ├── init.sql

│       └── seed.sql

├── k8s/

│   ├── api-deployment.yaml

│   ├── api-service.yaml

│   ├── ingress.yaml

│   ├── kustomization.yaml

│   ├── namespace.yaml

│   ├── postgres-config.yaml

│   ├── postgres-deployment.yaml

│   ├── postgres-service.yaml

│   └── postgres-storage.yaml

├── .github/

│   └── workflows/

├── .gitignore

├── Dockerfile

├── docker-compose.yml

└── README.md

```



\*Note: This is a high-level project structure. Some application files and workflow files are omitted from the listing.\*



\## Prerequisites



To run or manage the project locally, you will need:



\- Git

\- Python and pip

\- Docker Desktop

\- Docker Compose

\- Kubernetes enabled in Docker Desktop

\- `kubectl`

\- A Windows PowerShell terminal or an equivalent shell



\## Deploying to Kubernetes



Run these commands from the project root.



\### 1. Check cluster access



```powershell

kubectl cluster-info

kubectl get nodes

```



\### 2. Apply the Kubernetes resources



```powershell

kubectl apply -k .\\k8s

```



This command uses the Kustomize configuration to apply the listed Kubernetes manifests.



\*\*Prerequisite:\*\* Ensure the `factoryflow-db-secret` Kubernetes Secret has been created in the `factoryflow` namespace before starting the database-dependent application. Supply credentials securely; do not commit real secrets to Git.



\### 3. Check deployment status



```powershell

kubectl get deployments,pods -n factoryflow

kubectl get services -n factoryflow

kubectl get hpa -n factoryflow

kubectl get ingress -n factoryflow

```



\### 4. Access the API locally



Start a port-forward in one PowerShell window:



```powershell

kubectl port-forward -n factoryflow service/factoryflow-api 8000:8000

```



Keep that window open. In a second PowerShell window, test the endpoints:



```powershell

curl.exe -i http://localhost:8000/health

curl.exe -i http://localhost:8000/products

curl.exe -i http://localhost:8000/inventory

```



The health endpoint should return HTTP 200 and indicate whether the database is connected.



\### 5. Access through NGINX Ingress



The local Ingress hostname is `factoryflow.local`.



The Windows hosts file should map this hostname to `127.0.0.1`. With the NGINX Ingress controller running, establish the tested local port-forward:



```powershell

kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80

```



Then test the route:



```powershell

curl.exe -i http://factoryflow.local:8080/health

```



Keep the Ingress port-forward running while testing. This is a local development setup, not a public cloud deployment.



\## Useful Troubleshooting Commands



\### Inspect pods



```powershell

kubectl get pods -n factoryflow

```



\### Inspect API logs



```powershell

kubectl logs deployment/factoryflow-api -n factoryflow

```



\### Inspect PostgreSQL logs



```powershell

kubectl logs deployment/factoryflow-postgres -n factoryflow

```



\### Describe a pod



```powershell

kubectl describe pod <pod-name> -n factoryflow

```



Replace `<pod-name>` with the actual pod name.



\### Reapply configuration



```powershell

kubectl apply -k .\\k8s

```



\## Planned Improvements



The following are potential future enhancements and should not be considered completed features until implemented and verified:



\- Automated API and database integration tests in CI.

\- Expanded GitHub Actions build, test, and deployment workflows.

\- Prometheus and Grafana monitoring.

\- Structured application logging and operational dashboards.

\- Database backup and recovery procedures.

\- Production-grade secret management.

\- More complete manufacturing, batch tracking, warehouse movement, and order-fulfilment workflows.

\- Deployment to a cloud Kubernetes environment.



\## Development Principles



\- Local-first development without requiring a paid cloud subscription.

\- Reproducible environments and automated quality checks.

\- Secure configuration and least-privilege access.

\- Infrastructure defined through version-controlled manifests.

\- Incremental implementation and verification.

\- Documentation that distinguishes tested capabilities from future plans.



\## Disclaimer



FactoryFlow is an educational simulation created for software engineering and DevOps portfolio development. It is not affiliated with, endorsed by, or a representation of the proprietary systems of any real FMCG company.



