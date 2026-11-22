# Android CI on GitHub-hosted runners: memory, disk and Jetifier

How to diagnose and fix Flutter Android builds that fail, stall or get killed on GitHub-hosted runners, without burning CI minutes on guesses.

## Know the machine first

| Runner | CPU | RAM | SSD |
| --- | --- | --- | --- |
| `ubuntu-latest`, **private** repo | 2 | 8 GB | 14 GB |
| `ubuntu-latest`, public repo | 4 | 16 GB | 14 GB |
| Larger runner (paid) | 4+ | 16 GB+ | 150 GB+ |

Source: [GitHub-hosted runners reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners). Check the repo's visibility (`gh repo view --json visibility`) before sizing anything.

Flutter's template `android/gradle.properties` ships `org.gradle.jvmargs=-Xmx8G -XX:MaxMetaspaceSize=4G ...`, sized for a developer machine. The Kotlin compile daemon inherits that `-Xmx` unless `kotlin.daemon.jvmargs` is set (measured: both daemons ran with `-Xmx8G`). On a private-repo runner that is two JVMs each allowed the whole machine.

## Read the failure signature before changing anything

| Log signature | Meaning | Fix |
| --- | --- | --- |
| `No space left on device` | Runner disk full (NDK download + unzip, caches, heap dumps) | Free disk step (below); drop `-XX:+HeapDumpOnOutOfMemoryError` in CI |
| `The runner has received a shutdown signal` + `Gradle task ... failed with exit code 143` | Runner VM ran out of memory (or disk) and was killed | Size Gradle for the runner (below), then find what uses the memory |
| No output for many minutes, then `The job has exceeded the maximum execution time` | Machine swapping or thrashing under memory pressure | Same as above; a longer timeout does not help |
| `Execution failed for JetifyTransform: .../io.flutter/<abi>_debug/... > Java heap space` | Jetifier rewriting Flutter's debug engine jars | Disable Jetifier if `checkJetifier` allows it (below) |
| `gradle cache is not found` on every run | No run ever finished, or matrix jobs share one cache key | Per-app cache key (below) |

Get the facts with `gh`, not by re-running:

```bash
gh run view <run-id> --json jobs --jq '.jobs[] | "\(.databaseId) \(.name): \(.conclusion) \(.startedAt) -> \(.completedAt)"'
gh api repos/<owner>/<repo>/actions/jobs/<job-id> --jq '.steps[] | "\(.name): \(.conclusion) \(.started_at) -> \(.completed_at)"'
gh api repos/<owner>/<repo>/check-runs/<job-id>/annotations --jq '.[] | "\(.annotation_level): \(.message)"'
gh api repos/<owner>/<repo>/actions/jobs/<job-id>/logs > job.log
```

Cancelled or killed jobs often return `BlobNotFound` for the log: open the job page instead and enable **Show timestamps** (gear icon) to see where output stopped.

## Jetifier is the usual root cause, and it can usually go

Jetifier rewrites every dependency for AndroidX, including Flutter's large `io.flutter:*_debug` engine jars, which needs a lot of heap. Most libraries are AndroidX-native now; Google says disabling Jetifier typically saves 5-10% of build time ([Build Analyzer](https://developer.android.com/build/build-analyzer), [AndroidX migration](https://developer.android.com/jetpack/androidx/migrate)). The same failure hit zulip-flutter ([#1330](https://github.com/zulip/zulip-flutter/issues/1330)).

Check it locally (free), per app:

```bash
cd android
# A Flutter app's build.gradle often reads dart-defines; pass them the way `flutter build` does.
DEFS=$(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' ../staging.env | while IFS= read -r l; do printf '%s' "$l" | base64; done | paste -sd, -)
./gradlew -Pdart-defines="$DEFS" :app:checkJetifier
```

If it prints `does not use any legacy support libraries`, set `android.enableJetifier=false` in `android/gradle.properties`.

A Jetifier warning that a library "contains references to both AndroidX and old support library" is not proof the library needs Jetifier. `androidx.media:media` itself still ships `android.support.v4.media.*` classes (`MediaSessionCompat`, `PlaybackStateCompat`, `MediaMetadataCompat`), so references to those resolve without rewriting (seen with `me.carda:AndroidAwnCore` from awesome_notifications). Verify by listing the classes in the AndroidX jar from `~/.gradle/caches/modules-2/files-2.1/`.

If something really needs Jetifier, keep it and exclude the Flutter engine jars instead: `android.jetifier.ignorelist=armeabi_v7a_debug,arm64_v8a_debug,x86_64_debug` (community workaround, not official documentation).

## Workflow snippets

Free disk space, first step of the Android job (before Java and Flutter are installed). This deletes preinstalled tools on the disposable GitHub-hosted runner; never run it on your own machine:

```yaml
      - name: Free disk space
        working-directory: .
        run: sudo rm -rf /usr/share/dotnet /opt/ghc /usr/local/.ghcup /usr/local/share/boost /opt/hostedtoolcache/CodeQL
```

Per-app Gradle cache in a monorepo matrix. A custom `cache-dependency-path` replaces setup-java's defaults, so include the wrapper properties too ([setup-java](https://github.com/actions/setup-java)):

```yaml
      - uses: actions/setup-java@v6
        with:
          distribution: temurin
          java-version: '17'
          cache: gradle
          cache-dependency-path: |
            apps/${{ matrix.app }}/android/**/*.gradle*
            apps/${{ matrix.app }}/android/**/gradle-wrapper.properties
```

CI-only Gradle sizing for an 8 GB runner. `~/.gradle/gradle.properties` (`GRADLE_USER_HOME`) takes precedence over the project file ([Gradle build environment](https://docs.gradle.org/current/userguide/build_environment.html)), so local builds keep their settings:

```yaml
      - name: Size Gradle for the runner
        working-directory: .
        run: |
          mkdir -p ~/.gradle
          cat >> ~/.gradle/gradle.properties <<'EOF'
          org.gradle.jvmargs=-Xmx3g -XX:MaxMetaspaceSize=1g -XX:ReservedCodeCacheSize=256m
          kotlin.daemon.jvmargs=-Xmx1536m
          org.gradle.workers.max=2
          EOF
```

Temporary memory evidence for one diagnostic run (remove once the build is green). The `trap` stops the monitor even when the build fails, and the build's exit code is kept:

```yaml
      - name: Build debug APK
        run: |
          (while true; do
            echo "[memory $(date -u +%H:%M:%S)] $(free -m | awk '/Mem:/ {print "used=" $3 "MB avail=" $7 "MB"} /Swap:/ {print "swap_used=" $3 "MB"}' | paste -sd' ') load=$(cut -d' ' -f1-3 /proc/loadavg)"
            ps -eo rss=,comm= --sort=-rss | head -4 | awk '{printf "  %s %dMB\n", $2, $1/1024}'
            sleep 60
          done) &
          monitor_pid=$!
          trap 'kill "$monitor_pid" 2>/dev/null || true' EXIT
          flutter build apk --debug

      - name: Report out-of-memory kills
        if: always()
        working-directory: .
        run: |
          if ! kernel_log=$(sudo dmesg -T 2>&1); then
            echo "Kernel log unavailable: $kernel_log"
            exit 0
          fi
          echo "$kernel_log" | grep -i -E "out of memory|oom-kill|killed process" || echo "No out-of-memory kills in the kernel log"
```

`if: always()` steps may not run after a job-level timeout, so the inline monitor is the evidence that survives a stall.

## Measure locally before pushing

A Mac cannot reproduce the x64 Linux runner, but it can show whether a setting works and how much memory the build really uses:

1. Apply the CI settings through a temporary `~/.gradle/gradle.properties` (back it up or delete it afterwards).
2. Stop daemons (`./gradlew --stop`, `pkill -f KotlinCompileDaemon`) so new JVM args apply, and delete `build/`, `android/app/build`, `android/build`, `android/.gradle` for a clean build.
3. Run `flutter build apk --debug --flavor <flavor> ...` while sampling `ps -axo rss=,command=` for `GradleDaemon`, `KotlinCompileDaemon`, `dart` every 2 s; record the peak and the `-Xmx` each daemon actually got.

Measured on a mid-size two-flavor app: peak about 3.7-4.3 GB of resident memory either way; the failures came from Jetifier's heap demand and the `-Xmx8G` ceilings on an 8 GB machine, not from steady-state use.

## Escalation when memory is healthy but the build is still slow

- Build one ABI for the CI smoke build: `flutter build apk --debug --target-platform android-arm64` (stops checking the other ABIs).
- Use a larger runner (4 CPU / 16 GB); billed per minute on private repos.
