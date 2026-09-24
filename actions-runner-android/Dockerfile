# The official GitHub Actions runner image, plus an empty Android SDK that the
# Android Gradle Plugin can fill for itself.
#
# ubuntu-latest ships a full SDK, which is the only reason an Android build
# has had to run there. What a build actually needs from the machine is less
# than that: ANDROID_HOME pointing at a directory the build can write to, with
# the SDK licences already accepted in it. Given those, AGP downloads whatever
# platform and build-tools the project names the first time it needs them --
# which is what makes compileSdk a line in the app's build rather than a line
# here, and a bump to it not a rebuild of this image.
#
# Nothing is preinstalled for the same reason, and because installing it here
# would mean sdkmanager, which means a JDK in the image and a pinned
# cmdline-tools download to keep current. The cost is a platform and a
# build-tools download at the start of each job, since every runner pod
# starts empty.
#
# No JDK: the workflow brings its own with actions/setup-java, the same as it
# does on ubuntu-latest, so the Java a build uses is chosen by the repository.
#
# The runner contract is left alone, exactly as in actions-runner/: the
# binary, /home/runner/run.sh and the `runner` user come from upstream.
#
# Renovate bumps this pin, and the tag published from it is read back out of
# this line. See .github/workflows/build.yml.
FROM ghcr.io/actions/actions-runner:2.337.0

USER root

ENV ANDROID_HOME=/opt/android-sdk \
    ANDROID_SDK_ROOT=/opt/android-sdk

# libatomic1  As in actions-runner/: Node links it from 25 onwards, and
#             anything that downloads its own Node needs it.
# unzip       AGP unpacks SDK packages itself, but a job that fetches a tool
#             from Google by hand gets a zip.
#
# The licence files are what `sdkmanager --licenses` writes after "y": one
# file per licence, holding the hash of each version of its text that has
# been accepted. AGP refuses to download a package whose licence has no file
# here. The directory belongs to `runner` because AGP writes the packages it
# downloads next to them.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libatomic1 \
        unzip \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p "$ANDROID_HOME/licenses" \
    && printf '\n24333f8a63b6825ea9c5514f83c2829b004d1fee\nd56f5187479451eabf01fb78af6dfcb131a6481e\n8933bad161af4178b1185d1a37fbf41ea5269c55' \
        > "$ANDROID_HOME/licenses/android-sdk-license" \
    && printf '\n84831b9409646a918e30573bab4c9c91346d8abd' \
        > "$ANDROID_HOME/licenses/android-sdk-preview-license" \
    && chown -R runner:runner "$ANDROID_HOME"

USER runner
