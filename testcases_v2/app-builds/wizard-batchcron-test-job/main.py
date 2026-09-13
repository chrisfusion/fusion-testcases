import json
import os

# Proves per-entry parameterization actually works: fusion-flux injects one
# JOB_* env var per field of the BatchCron job entry that fired this run
# (see fusion-flux/internal/trigger/batchjobs.go decodeJob). Unlike
# wizard-batch-test-job (a single fixed OnDemand/Cron job with no batch
# context), this fixture is meant to be run from a BatchCron trigger.

JOB_ENV_KEYS = [
    "JOB_ID",
    "JOB_NAME",
    "JOB_TOPIC",
    "JOB_MAINTAINER",
    "JOB_STARTDATE",
    "JOB_STARTTIME",
    "JOB_SCHEDULE",
    "JOB_METADATA",
]


def main() -> None:
    print("wizard-batchcron-test-job: single job-entry run starting...")

    job_env = {key: os.environ.get(key, "") for key in JOB_ENV_KEYS}
    metadata = {}
    if job_env["JOB_METADATA"]:
        try:
            metadata = json.loads(job_env["JOB_METADATA"])
        except json.JSONDecodeError:
            metadata = {"_unparsed": job_env["JOB_METADATA"]}

    for key, value in job_env.items():
        print(f"{key}={value}")

    print("wizard-batchcron-test-job: done.")
    # Last stdout line must be the JSON payload for fusion-weave's
    # producesOutput capture rule to pick it up.
    print(json.dumps({"job": "wizard-batchcron-test-job", "jobEnv": job_env, "metadata": metadata}))


if __name__ == "__main__":
    main()
