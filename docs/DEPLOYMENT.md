# CareBridge Deployment

## Local production stack

Copy `.env.example` to `.env`, replace all placeholder secrets, then run:

```bash
docker compose up --build -d
docker compose ps
```

The frontend is exposed on `http://localhost` by default. Nginx serves the React
SPA and proxies `/api/`, `/ws/`, and `/health/` to Daphne. PostgreSQL, Redis,
Celery worker, and Celery beat are private services in the Compose network.

Set `APP_PORT` to expose a different host port. Persistent named volumes hold
PostgreSQL, Redis, uploaded media, and collected static files.

## Required production settings

At minimum, set secure values for:

- `SECRET_KEY`, `ALLOWED_HOSTS`, and `CORS_ALLOWED_ORIGINS`
- `DB_NAME`, `DB_USER`, and `DB_PASSWORD`
- email, payment, map, and AI provider credentials used by your environment
- `SENTRY_DSN` if production error reporting is enabled

Keep `.env` out of source control. Rotate any credential that has previously
been committed or shared.

## Azure Container Apps

The Bicep template at `deployment/azure/main.bicep` provisions the Container
Apps environment, logging workspace, backend app, and frontend app. Provision
Azure Database for PostgreSQL, Azure Cache for Redis, and Azure Container
Registry separately, then deploy:

```bash
az deployment group create \
  --resource-group <resource-group> \
  --template-file deployment/azure/main.bicep \
  --parameters backendImage=<acr>/carebridge-backend:latest \
               frontendImage=<acr>/carebridge-frontend:latest \
               registryServer=<registry>.azurecr.io \
               registryUsername='<registry-user>' \
               registryPassword='<registry-password>' \
               secretKey='<secret>' \
               databaseUrl='<database-url>' \
               redisUrl='<redis-url>' \
               allowedHosts='.azurecontainerapps.io' \
               corsAllowedOrigins='https://<frontend-host>'
```

Use Azure Key Vault or secure pipeline inputs for secrets; do not commit a
filled parameter file.

## GitHub Actions

`ci.yml` checks Django, migrations, tests, the Vite production build, and both
container images. `deploy-azure.yml` uses Azure workload identity federation,
pushes immutable SHA-tagged images to ACR, and updates both Container Apps.

Configure repository variables `ACR_NAME`, `AZURE_RESOURCE_GROUP`,
`AZURE_BACKEND_APP`, and `AZURE_FRONTEND_APP`, plus the federated identity
secrets `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_SUBSCRIPTION_ID`.

## Operations

Use `/health/` for health probes. Back up PostgreSQL and uploaded media,
monitor error rate and request latency through the API Gateway audit dashboard,
and test database restoration before each major release.
