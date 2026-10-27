

\# FactoryFlow Architecture



\## System Overview



FactoryFlow is a local-first FMCG manufacturing and supply-chain simulation deployed on Kubernetes using Docker Desktop.



\## Architecture Diagram



```mermaid

flowchart TD

&#x20;   Client\["Client / HTTP Request"]

&#x20;   Ingress\["NGINX Ingress Controller"]

&#x20;   Service\["Kubernetes API Service<br/>Port 8000"]

&#x20;   API\["FactoryFlow Flask API<br/>Gunicorn"]

&#x20;   DBService\["PostgreSQL Kubernetes Service<br/>Port 5432"]

&#x20;   DB\["PostgreSQL Database"]

&#x20;   PVC\["PersistentVolumeClaim"]



&#x20;   Client --> Ingress

&#x20;   Ingress --> Service

&#x20;   Service --> API

&#x20;   API --> DBService

&#x20;   DBService --> DB

&#x20;   DB --- PVC



&#x20;   Config\["ConfigMap"]

&#x20;   Secret\["Kubernetes Secret"]

&#x20;   HPA\["Horizontal Pod Autoscaler"]



&#x20;   Config -.-> API

&#x20;   Secret -.-> API

&#x20;   HPA -.-> API

```



\## Component Responsibilities



| Component | Responsibility |

|---|---|

| Client | Sends HTTP requests to the application |

| NGINX Ingress Controller | Routes incoming HTTP requests using the configured hostname |

| Kubernetes API Service | Routes traffic to available API pods |

| Flask API | Handles health, product, and inventory requests |

| PostgreSQL Service | Provides internal network access to PostgreSQL |

| PostgreSQL | Stores application and inventory data |

| PersistentVolumeClaim | Requests persistent storage for database data |

| ConfigMap | Supplies non-sensitive application configuration |

| Kubernetes Secret | Supplies sensitive configuration such as database credentials |

| Horizontal Pod Autoscaler | Adjusts API replica count based on observed CPU utilization |



\## Local Access



The configured Ingress hostname is `factoryflow.local`.



For local development, the Ingress controller is accessed using a Kubernetes port-forward:



```powershell

kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80

```



The API can then be tested with:



```powershell

curl.exe -i http://factoryflow.local:8080/health

```



The port-forward must remain active while testing this route.



\## Deployment Management



Kubernetes resources are organized through `k8s/kustomization.yaml` and can be applied from the project root using:



```powershell

kubectl apply -k .\\k8s

```



\## Scope and Limitations



\- The current deployment runs locally on Docker Desktop Kubernetes.

\- The architecture does not represent a public cloud deployment.

\- The HPA is configured for CPU-based scaling, with a minimum of one and a maximum of three API replicas.

\- Database credentials must be managed securely and must not be committed as plaintext secrets.

\- The diagram represents the intended request and dependency flow; it does not imply that every component has been independently load-tested or production-certified.



