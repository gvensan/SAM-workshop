# Quickstart - Docker

One page to get all three workshop services running with Docker. Works identically on macOS, Windows (Docker Desktop / WSL 2), and Linux. Run everything from the workshop root (`SAM-workshop/`).

## Before you start

- Docker Desktop (macOS/Windows) or the Docker daemon (Linux) is running: `docker info`
- Credentials file created at the workshop root: `cp env.example .env`, then edit in your **Foursquare Legacy API Client ID and Client Secret** (optional: `ANTHROPIC_API_KEY` for AI recommendations) - see [One-Time Setup](../README.md#one-time-setup-credentials-file-env)
- SAM Desktop is installed with `SAM_PLATFORM_ALLOW_PRIVATE_MCP=true` set ([Step 1.2](../README.md#12-allow-local-mcp-servers))

## Start the services

```bash
# 1. Places MCP server (port 3010) - reads Foursquare credentials from .env
docker build -t places-mcp-server external/places-mcp-server/
docker run -d --name places-mcp -p 3010:3010 \
  --env-file .env \
  --restart unless-stopped places-mcp-server

# 2. Weather Advisor agent (port 10010) - key optional; picks up ANTHROPIC_API_KEY from .env if set
docker build -t weather-advisor-agent external/weather-advisor-agent/
docker run -d --name weather-advisor -p 10010:10010 \
  --env-file .env \
  --restart unless-stopped weather-advisor-agent

# 3. Amadeus mock (port 8090) - no key needed; --build guards against stale images
docker compose -f external/amadeus-mock/docker-compose.yml up -d --build
```

## Verify

```bash
curl -sS http://localhost:3010/health  && echo ""   # places-mcp
curl -sS http://localhost:10010/health && echo ""   # weather-advisor
curl -sS http://localhost:8090/health  && echo ""   # amadeus-mock
```

All three should return a small JSON status. Containers carry `--restart unless-stopped`, so they come back after a reboot until you remove them (`docker rm -f <name>`).

## Continue

Services are up - the rest of the workshop is identical for every runtime. Continue in the README at [Workshop - Hands-on, Step 1](../README.md#step-1-install--configure-sam-desktop). Deeper per-service verification lives in [Step 2](../README.md#step-2-verify-mcp-server-places) and [Step 3](../README.md#step-3-verify-external-a2a-agent-weather-advisor); if anything misbehaves, see [Troubleshooting](../README.md#troubleshooting).

## Tear down / start fresh

```bash
# Stop and remove the three containers (frees ports 3010/10010/8090)
docker rm -f places-mcp weather-advisor
docker compose -f external/amadeus-mock/docker-compose.yml down

# Optional deeper clean - remove the images too (forces a full rebuild next time)
docker rmi places-mcp-server weather-advisor-agent amadeus-mock

# Confirm the ports are free (no output = clean)
lsof -i :3010 -i :10010 -i :8090
# Windows (PowerShell): netstat -ano | findstr ":3010 :10010 :8090"
```

> Teardown discards container logs and the mock's in-memory OAuth tokens. If you are mid-debugging, save `docker logs <name>` output first.

To reset the SAM Desktop side (agents, connectors, toolset), see [Reset: Run the Workshop Again](../README.md#reset-run-the-workshop-again).
