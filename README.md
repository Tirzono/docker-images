# docker-images

Container images built here and published to GHCR. One directory per image;
each is a `Dockerfile` and nothing else.

## What is in here

| Image | What it is |
| --- | --- |
| [`actions-runner`](actions-runner/) | The official GitHub Actions runner, plus two libraries jobs commonly need |
| [`actions-runner-android`](actions-runner-android/) | The official runner, plus an Android SDK directory the Gradle plugin can fill |

### `actions-runner`

`ghcr.io/actions/actions-runner` is deliberately minimal: the runner, and
little else. A workflow cannot make up the difference at run time either,
because the runner is an unprivileged user with no `sudo` — so `apt-get
install` fails in a step, and anything a job needs from the system has to be in
the image.

Two libraries, both for things that are ordinary in a Python or Django
project's CI:

- **`libatomic1`** — Node links it from 25 onwards. Anything that downloads its
  own Node at run time defaults to the newest release and fails to start
  without it. nodeenv does, which means every pre-commit hook with
  `language: node`.
- **`gettext`** — `msgfmt`, `msguniq`, `msgattrib`. Django shells out to them
  for `makemessages` and `compilemessages`, so a workflow that checks
  translation catalogs needs them on `PATH`.

What is *not* changed is the rest of the image: the runner binary, the
entrypoint at `/home/runner/run.sh`, and the `runner` user. The
[`gha-runner-scale-set`][arc] chart starts `run.sh` and hands it a just-in-time
registration config, so an image that changes that contract does not register
at all. It is also why the fuller third-party runner images are no use with
that chart — they register themselves from environment variables, which is the
older, pre-scale-set model.

### `actions-runner-android`

For Android builds, which have needed `ubuntu-latest` only because it ships an
SDK. What the Android Gradle Plugin needs from the machine is less than that:
`ANDROID_HOME` pointing at a directory it can write to, with the SDK licences
already accepted there. Given those, it downloads the platform and build-tools
the project names by itself, so a `compileSdk` bump is a change to the app and
not to this image.

So the SDK here is empty apart from `licenses/`, and `/opt/android-sdk` belongs
to `runner`. There is no JDK either: the workflow brings its own with
`actions/setup-java`, as it does on `ubuntu-latest`. The price is a platform
and build-tools download at the start of each job, since every runner pod
starts from the image.

It carries `libatomic1` as `actions-runner` does, and `unzip`; not `gettext`,
which an Android build has no use for.

## How a build works

Every push builds. Only the default branch publishes, because a deployment
pinning an immutable tag should never have one move under it.

The tag is the base image's, read out of the `FROM` line rather than written
down a second time: `actions-runner:2.337.0` is "the official 2.337.0, with
this repository's additions". That gives the chain one version to follow —
Renovate bumps the `FROM` pin here, merging publishes the matching tag, and
whatever pins the image downstream sees a new tag to move to.

That first step runs unattended: a minor or patch bump to a base image or an
action is merged by Renovate once the build is green, so an upstream release
turns into a published tag on its own. A major is left open for someone to
look at.

Between the build and the push, the image is checked for the things it exists
to provide — for `actions-runner`, that `msgfmt` runs and `libatomic.so.1` is
present; for `actions-runner-android`, that `ANDROID_HOME` is set, writable and
has the SDK licence accepted — and for the two parts
of the chart's contract that are easy to break silently: `/home/runner/run.sh`
is executable, and the default user is `runner`.

Builds run on GitHub-hosted runners. An image build needs a Docker daemon,
which a scale-set runner pod does not have unless it is given a privileged
sidecar — so this is one workflow that stays where it is.

## Adding an image

1. `mkdir <name>/` with a `Dockerfile` in it, pinned to a tagged base image.
2. Add `<name>` to the `image:` matrix in
   [`.github/workflows/build.yml`](.github/workflows/build.yml).
3. Pin the published tag wherever it is consumed rather than following
   `latest` — a GitOps reconciler compares git against what is deployed, so a
   tag that keeps its name never rolls out at all.

A first build publishes a package that is private by default, whatever the
repository's visibility. Make it public once in the package's settings, or
every consumer needs a pull secret for it.

[arc]: https://github.com/actions/actions-runner-controller
