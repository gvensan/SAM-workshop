# Quickstart - Podman

One page to get all three workshop services running with Podman. Works on macOS, Windows, and Linux. Run everything from the workshop root (`SAM-workshop/`).

## Before you start

- **macOS/Windows:** start the Podman VM first: `podman machine start` (then confirm with `podman ps`)
- You have your **Foursquare Legacy API Client ID and Client Secret** ([signup notes](../README.md#api-keys-required))
- SAM Desktop is installed with `SAM_PLATFORM_ALLOW_PRIVATE_MCP=true` set ([Step 1.2](../README.md#12-allow-local-mcp-servers))

## Start the services

```bash
# 1. Places MCP server (port 3010) - insert your Foursquare credentials
podman build -t places-mcp-server external/places-mcp-server/
podman run -d --name places-mcp -p 3010:3010 \
  -e FOURSQUARE_CLIENT_ID="YOUR_CLIENT_ID" \
  -e FOURSQUARE_CLIENT_SECRET="YOUR_CLIENT_SECRET" \
  places-mcp-server

# 2. Weather Advisor agent (port 10010) - no key needed
podman build -t weather-advisor-agent external/weather-advisor-agent/
podman run -d --name weather-advisor -p 10010:10010 weather-advisor-agent
# Optional AI recommendations: add  -e ANTHROPIC_API_KEY="sk-ant-..."  to the run command

# 3. Amadeus mock (port 8090) - no key needed
podman build -t amadeus-mock external/amadeus-mock/
podman run -d --name amadeus-mock -p 8090:8090 amadeus-mock
# Or, with the compose provider (Podman 4+):
# podman compose -f external/amadeus-mock/docker-compose.yml up -d --build
```

## Verify

```bash
curl -s http://localhost:3010/health   # places-mcp
curl -s http://localhost:10010/health  # weather-advisor
curl -s http://localhost:8090/health   # amadeus-mock
```

All three should return a small JSON status.

> Unlike the Docker path, these commands omit `--restart unless-stopped`: rootless Podman containers do not auto-start after a reboot without extra systemd setup. After a restart, rerun the `podman run` commands (`podman rm -f <name>` first if the names are taken).

## Continue

Services are up - the rest of the workshop is identical for every runtime. Continue in the README at [Workshop - Hands-on, Step 1](../README.md#step-1-install--configure-sam-desktop). Deeper per-service verification lives in [Step 2](../README.md#step-2-verify-mcp-server-places) and [Step 3](../README.md#step-3-verify-external-a2a-agent-weather-advisor); if anything misbehaves, see [Troubleshooting](../README.md#troubleshooting).

## Tear down / start fresh

```bash
# Stop and remove the three containers (frees ports 3010/10010/8090)
podman rm -f places-mcp weather-advisor amadeus-mock
# If you started the mock via the compose provider instead:
# podman compose -f external/amadeus-mock/docker-compose.yml down

# Optional deeper clean - remove the images too (forces a full rebuild next time)
podman rmi places-mcp-server weather-advisor-agent amadeus-mock

# Optional (macOS/Windows): stop the Podman VM
podman machine stop
```

> Teardown discards container logs and the mock's in-memory OAuth tokens. If you are mid-debugging, save `podman logs <name>` output first.

To reset the SAM Desktop side (agents, connectors, toolset), see [Reset: Run the Workshop Again](../README.md#reset-run-the-workshop-again).
