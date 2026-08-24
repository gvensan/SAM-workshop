# Quickstart - Local Python (No Containers)

One page to get all three workshop services running as plain Python processes - no Docker or Podman needed. Open **three terminals**, each starting from the workshop root (`SAM-workshop/`); every service occupies its terminal while running (Ctrl+C stops it, and there is no auto-restart).

## Before you start

- **Python 3.11 or 3.12** (`python3 --version`). **Not 3.13** - the mock pins an older pydantic with no 3.13 wheels; if you only have 3.13, install 3.12 and substitute `python3.12` below
- You have your **Foursquare Legacy API Client ID and Client Secret** ([signup notes](../README.md#api-keys-required))
- SAM Desktop is installed with `SAM_PLATFORM_ALLOW_PRIVATE_MCP=true` set ([Step 1.2](../README.md#12-allow-local-mcp-servers))
- Debian/Ubuntu may need `sudo apt install python3-venv` first

## Start the services - macOS / Linux

```bash
# Terminal 1 - Places MCP server (port 3010) - insert your Foursquare credentials
cd external/places-mcp-server
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
FOURSQUARE_CLIENT_ID="YOUR_CLIENT_ID" FOURSQUARE_CLIENT_SECRET="YOUR_CLIENT_SECRET" \
  .venv/bin/python server.py
```

```bash
# Terminal 2 - Weather Advisor agent (port 10010) - no key needed
cd external/weather-advisor-agent
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python agent.py
# Optional AI recommendations: ANTHROPIC_API_KEY="sk-ant-..." .venv/bin/python agent.py
```

```bash
# Terminal 3 - Amadeus mock (port 8090) - no key needed
cd external/amadeus-mock
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8090
```

## Start the services - Windows (PowerShell)

```powershell
# Terminal 1 - Places MCP server (port 3010) - insert your Foursquare credentials
cd external\places-mcp-server
py -3.12 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
$env:FOURSQUARE_CLIENT_ID = "YOUR_CLIENT_ID"
$env:FOURSQUARE_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
.venv\Scripts\python server.py
```

```powershell
# Terminal 2 - Weather Advisor agent (port 10010) - no key needed
cd external\weather-advisor-agent
py -3.12 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python agent.py
# Optional AI recommendations: set a real key first: $env:ANTHROPIC_API_KEY = "sk-ant-..."
```

```powershell
# Terminal 3 - Amadeus mock (port 8090) - no key needed
cd external\amadeus-mock
py -3.12 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8090
```

> No `py` launcher? Use `python -m venv .venv` after confirming `python --version` reports 3.11 or 3.12. On Windows, call `curl.exe` (not bare `curl`) in PowerShell.

## Verify

```bash
curl -s http://localhost:3010/health   # places-mcp
curl -s http://localhost:10010/health  # weather-advisor
curl -s http://localhost:8090/health   # amadeus-mock
```

All three should return a small JSON status. After a crash, reboot, or closed terminal, rerun the start command in that service's terminal (the venvs persist; skip the `venv`/`pip` lines on reruns).

## Continue

Services are up - the rest of the workshop is identical for every runtime. Continue in the README at [Workshop - Hands-on, Step 1](../README.md#step-1-install--configure-sam-desktop). Deeper per-service verification lives in [Step 2](../README.md#step-2-verify-mcp-server-places) and [Step 3](../README.md#step-3-verify-external-a2a-agent-weather-advisor); if anything misbehaves, see [Troubleshooting](../README.md#troubleshooting).

## Tear down / start fresh

Press **Ctrl+C** in each of the three terminals to stop the services. That alone frees the ports; to force a clean `pip install` on the next run, also delete the venvs:

```bash
# macOS / Linux
rm -rf external/places-mcp-server/.venv external/weather-advisor-agent/.venv external/amadeus-mock/.venv
```

```powershell
# Windows (PowerShell)
Remove-Item -Recurse -Force external\places-mcp-server\.venv, external\weather-advisor-agent\.venv, external\amadeus-mock\.venv
```

Keeping the venvs is fine if you only want to restart the processes - the mock's in-memory OAuth tokens are gone either way (the static token `workshop` still works).

To reset the SAM Desktop side (agents, connectors, toolset), see [Reset: Run the Workshop Again](../README.md#reset-run-the-workshop-again).
