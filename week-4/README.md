# Week 4, Docker Compose with PostgreSQL

## What this does
Runs the incident tracker and a PostgreSQL database as a two-service Compose stack, with data persisted in a named volume.

## Requirements
- Docker Compose (original stack) and k3s with kubectl
- A `.env` file in `week-4/` (copy `.env.example` and fill in real values)

## Run it
Compose is stopped now. Kubernetes (k3s) is how this app actually runs, from the manifests in this folder.
```
kubectl create secret generic db-credentials --from-env-file=.env
kubectl apply -f .
```

## Verify
```
kubectl get pods
kubectl port-forward --address 0.0.0.0 service/web 8080:8080
```
Then visit http://localhost:8080 in a browser.

## Stop it
```
docker compose down
```
Add `-v` only if you want to delete the database volume along with the containers.
