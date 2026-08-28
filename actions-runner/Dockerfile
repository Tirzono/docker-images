# The official GitHub Actions runner image, plus two libraries that jobs
# commonly need and it does not carry.
#
# That image ships the runner and little else, and a workflow cannot make up
# the difference at run time: it runs as an unprivileged user with no sudo, so
# `apt-get install` fails in a step however small the package is. Anything a
# job needs from the system has to be in the image.
#
# Everything else is left alone on purpose. The runner binary, the entrypoint
# at /home/runner/run.sh and the `runner` user all come from upstream, because
# the gha-runner-scale-set chart starts run.sh and hands it a just-in-time
# registration config. An image that changes that contract does not register at
# all, whatever else it has installed -- which is also why the fuller
# third-party runner images are no use with that chart: they register
# themselves from environment variables, which is the older model.
#
# Renovate bumps this pin, and the tag published from it is read back out of
# this line. See .github/workflows/build.yml.
FROM ghcr.io/actions/actions-runner:2.337.0

USER root

# libatomic1  Node links it from 25 onwards. Anything that downloads its own
#             Node at run time defaults to the newest release and so fails to
#             start without it -- nodeenv does, which means every pre-commit
#             hook with `language: node`.
# gettext     msgfmt, msguniq and msgattrib. Django shells out to them for
#             makemessages and compilemessages, so a workflow that checks
#             translation catalogs needs them on PATH.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libatomic1 \
        gettext \
    && rm -rf /var/lib/apt/lists/*

USER runner
