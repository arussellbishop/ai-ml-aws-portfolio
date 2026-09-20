# Russell Bishop — AI engineering and AWS portfolio

The central portfolio contains 60 static pages, 44 public project dossiers, four selected engineering case studies, employer/examiner review routes, transparent readiness scores and an editable synthetic data-quality demo. The private register tracks 46 projects/workstreams. Private administration and original documents are excluded. The demo runs in the browser; the separate Python/S3/Lambda implementation is included for deployment and cloud integration testing.

## Build and check

From this directory:

```sh
python3 build.py
python3 build_hosting.py
python3 scripts/build_walkthrough.py
python3 build_hub.py
python3 scripts/package_release.py
python3 -m unittest discover -s tests -v
node --check site/assets/demo.js
cfn-lint infra/hosting.json infra/data-quality.json
python3 scripts/package_release.py
```

The public generators read the versioned `data/projects.json` and `data/resources.json`. A sanitized CSV is also included in the downloadable source bundle. Private original paths are not required for a clean rebuild. Development-only dependencies are `cfn-lint` and `playwright`. `scripts/check_browser.py` uses installed Google Chrome and a loopback HTTP server, checks interaction and responsive layout, and exercises the CloudFront content security policy. Dependencies are isolated in `.tools-venv` in this workspace.

## AWS hosting

`infra/hosting.json`: private encrypted/versioned S3 → CloudFront with signed origin access, HTTPS redirection, caching and security headers. No custom domain or always-on compute is required. This is standard usage-based hosting; free-tier eligibility has not been established and no free-plan enrollment is implied.

Authenticate through AWS CLI browser sign-in or IAM Identity Center. Do not put credentials in the repository, source bundle or chat.

```sh
aws login --profile portfolio --region eu-north-1
python3 scripts/deploy.py --profile portfolio
python3 scripts/deploy.py --profile portfolio --apply
```

The first script invocation verifies identity, release hashes and the template without creating resources. `--apply` creates/updates hosting and uploads only the verified site directory, then invalidates the CloudFront cache. It writes the resulting URL to `release/deployment.json`. Before treating publication as complete, check that URL and all pages/downloads over HTTPS. AWS operations require suitable permissions. IAM Identity Center users should use `aws configure sso --profile portfolio` and `aws sso login --profile portfolio` instead of `aws login`.

The user has requested publication. AWS authentication and hosting deployment completed on 20 September 2026. The account-plan API returned no plan data, so free-tier coverage remains unverified. Public checks are recorded separately under release/.

## Data-quality pipeline

`quality.py` validates at most 1,000 JSON rows and 256 KiB. `infra/data-quality.json` embeds that source. S3 events must refer to a versioned `incoming/*.json` object in the expected bucket. Results go to a separate private bucket with deterministic version-derived keys. Reads/writes have prefix-scoped permissions. Logs retain seven days. HTTPS and encryption are enforced.

Repeated delivery overwrites the same result key, while bucket versioning can retain multiple versions. Dates are day-granularity provenance checks, not proof of point-in-time source availability. Input errors fail the invocation; the demonstration has no dead-letter queue and disables retries. Production needs alarms, a failure destination, recovery procedures and load testing. The deployment script publishes the website only; it does not claim or silently deploy the pipeline.

## Cost and recovery

CloudFront/S3 requests, transfer, storage and other resources can be billable. Account credits and free-tier status need verification. Budget alerts do not cap spending. Buckets are retained on stack deletion and need explicit cleanup to stop storage charges.

Release archives and SHA256 manifests live under `release/`. Roll back by restoring a prior site archive, verifying its manifest, uploading its files and invalidating the distribution. The upload does not delete previous objects. There is no verified independent backup from this build alone.

## Evidence boundaries

AIVouch's 30-test result comes from the dated local audit, not from re-running or migrating its production service here. Historical AWS coursework is not current-account verification. Research projects and workstreams are not all finished products. No production uptime, trading profitability, earned AWS certification or measured model quality is asserted.

## Central portfolio records

`data/projects.json` contains curated descriptions, criteria, evidence, run notes and improvement actions. `data/resources.json` links existing Google Drive/Colab material without changing sharing. Scores are portfolio evidence readiness, not actual production or academic completion. Unknown evidence receives no credit in its gate; partial credit is explained. `build_hub.py` generates the full dashboard and dossier set.

Three public notebooks are included: two sanitized historical TensorFlow coursework copies (not freshly trained in this audit), and a self-contained standard-library demonstration executed by the release tests. Original submission acceptance is not inferred from filenames.

Keep private working notes and the original evidence outside this public source repository. The local owner notes workspace supports explicit JSON export and does not write to the public site.
