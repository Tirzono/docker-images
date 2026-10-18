"""Google's analytics-mcp, served over streamable HTTP.

Upstream ships the server as a stdio process and nothing else: its entry point
wires `analytics_mcp.coordinator.app`, a low-level MCP `Server` holding every
tool, to stdin and stdout. This file wires the same object to the MCP SDK's
streamable-HTTP session manager instead and changes nothing about the tools,
so what a client sees is upstream's server, tool for tool.

Configuration is the environment, and none of it is a secret:

  MCP_ALLOWED_HOSTS               required; the Host header(s) a request may
                                  carry, comma-separated.
  GOOGLE_APPLICATION_CREDENTIALS  where google.auth.default() finds its
                                  credentials. Upstream reads it, not this.
"""

import contextlib
import os
import sys

import uvicorn
from analytics_mcp.coordinator import app
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette
from starlette.routing import Route

# No default. The server is reachable from wherever its port is, and an
# allowlist that quietly fell back to something would be one nobody chose.
allowed_hosts = [h.strip() for h in os.environ.get("MCP_ALLOWED_HOSTS", "").split(",") if h.strip()]
if not allowed_hosts:
    sys.exit("MCP_ALLOWED_HOSTS is not set: name the host(s) clients reach this server by")

session_manager = StreamableHTTPSessionManager(
    app=app,
    # Stateless: every tool here is one request and one answer -- a report, a
    # property's details -- and nothing is ever pushed to a client between
    # calls. Without a session map in memory, a restart or a rollout costs a
    # client nothing, where a stateful server would answer its next request
    # with a 404 for a session it has never seen.
    stateless=True,
    json_response=True,
    # A Host outside the allowlist is a misrouted request or a DNS-rebinding
    # attempt, and is refused with a 421. allowed_origins is empty on purpose,
    # which refuses any request that carries an Origin header at all -- that
    # is to say a browser -- with a 403. Neither is authentication; whatever
    # sits in front of this has to be.
    security_settings=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts,
        allowed_origins=[],
    ),
)


class MCPEndpoint:
    """The session manager as a plain ASGI app.

    Starlette treats a class instance as ASGI and a function as a
    request-response view, so this has to be the former. A Route rather than
    a Mount, because a Mount at /mcp answers /mcp itself with a redirect to
    /mcp/, and the endpoint every client is given is /mcp.
    """

    async def __call__(self, scope, receive, send):
        await session_manager.handle_request(scope, receive, send)


@contextlib.asynccontextmanager
async def lifespan(_):
    async with session_manager.run():
        yield


starlette_app = Starlette(
    routes=[Route("/mcp", endpoint=MCPEndpoint(), methods=["GET", "POST", "DELETE"])],
    lifespan=lifespan,
)

if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0", port=8000, proxy_headers=False)
