# fdroidserver, for publishing an F-Droid repository: `fdroid update` reads
# APKs and writes a signed index. Tirzono/k8s fdroid/ runs it as a CronJob,
# with its script (publish.py) in a ConfigMap, so what is here is only what
# that script calls and imports.
#
# Debian's package rather than pip's, because `fdroid update` shells out to
# apksigner to sign the index, and apksigner needs a JDK: the package depends
# on both. F-Droid's own images are its full build server, several GB for an
# SDK and Gradle this never runs.
#
# boto3 uploads the repository to Garage; click and requests are what
# publish.py is written with.
#
# Renovate bumps this pin, and the tag published from it is read back out of
# this line (see .github/workflows/build.yml). The fdroidserver it gets is
# whatever that Debian release carries, which is 2.4 for trixie.
FROM debian:13.7-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        fdroidserver \
        python3-boto3 \
        python3-click \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 1000 --create-home fdroid

USER fdroid
WORKDIR /home/fdroid
