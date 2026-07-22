import json
import os

# Injected by fusion-weave's codeSource mechanism (internal/codesource), same
# for a Job-kind step as a Deploy-kind step — this is *this artifact's own*
# metadata as resolved from fusion-index at container start. WEAVE_PORT and
# WEAVE_INGRESS_PATH_PREFIX are expected empty here since this app has no
# runner.port/ingress in its own metadata.yaml.
ARTIFACT_KEYS = [
    "WEAVE_ARTIFACT",
    "WEAVE_TAG",
    "WEAVE_VERSION",
    "WEAVE_NAMESPACE",
    "WEAVE_MOUNT_PATH",
    "WEAVE_RUNNER_TYPE",
    "WEAVE_BUILDER_IMAGE",
    "WEAVE_MAINTAINER",
    "WEAVE_PORT",
    "WEAVE_INGRESS_PATH_PREFIX",
]

# Injected per-job by a BatchCron WeaveTrigger (internal/trigger/batchjobs.go)
# when this step's WeaveRun was created from a scheduled batch job entry.
# Empty/absent when fired any other way (OnDemand, Cron, ...).
JOB_KEYS = [
    "JOB_ID",
    "JOB_NAME",
    "JOB_TOPIC",
    "JOB_MAINTAINER",
    "JOB_STARTDATE",
    "JOB_STARTTIME",
    "JOB_SCHEDULE",
    "JOB_METADATA",
]


def run() -> None:
    """Read and report both metadata sources reaching this container: the
    artifact's own fusion-index metadata (codeSource) and, when triggered by
    a BatchCron WeaveTrigger, that job's scheduling metadata."""
    artifact_meta = {k: os.environ.get(k, "") for k in ARTIFACT_KEYS}
    job_meta = {k: os.environ.get(k, "") for k in JOB_KEYS}

    raw_job_metadata = job_meta.get("JOB_METADATA") or ""
    if raw_job_metadata:
        try:
            job_meta["JOB_METADATA"] = json.loads(raw_job_metadata)
        except json.JSONDecodeError:
            pass  # leave as raw string if it wasn't valid JSON

    print("Artifact metadata (from fusion-index, via codeSource):")
    for k, v in artifact_meta.items():
        print(f"  {k}={v}")

    print("Batch job metadata (from the BatchCron trigger, if present):")
    for k, v in job_meta.items():
        print(f"  {k}={v}")

    report = {"artifact": artifact_meta, "job": job_meta}
    print(json.dumps(report))
