# Google's Analytics MCP server (googleanalytics/google-analytics-mcp), served
# over streamable HTTP by server.py. Upstream publishes a PyPI package with a
# stdio transport and no image; this is that package, and the few dozen lines
# that put it on a port.
#
# NOTHING SECRET IS IN HERE, and nothing should ever be. The image holds the
# packages in requirements.txt and server.py, both copied by name -- never the
# directory -- so a file left lying beside them cannot be swept in. How the
# server proves who it is to Google arrives at run time, from wherever it runs
# (Tirzono/k8s: analytics-mcp/). The build checks this before it pushes; see
# .github/workflows/build.yml.
#
# Renovate bumps this pin and holds it on 3.13, which requirements.txt is
# locked for. The published tag is the analytics-mcp version and this Python
# version together; see the README.
FROM python:3.13.16-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Every package pinned and every file hashed, so what is installed is exactly
# what was reviewed, and a file changed on PyPI under the same version fails
# the build. --no-deps because the lock already lists everything; wheels only,
# so no package's setup code runs here.
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --no-deps --require-hashes --only-binary=:all: \
        --requirement /app/requirements.txt

COPY server.py /app/server.py

# Numeric, so a pod's runAsNonRoot can be checked against the image itself.
USER 1000:1000
EXPOSE 8000
CMD ["python", "/app/server.py"]
