# Agent Instructions

Before starting any task in this repository:

1. Run `make agents/sync`. It writes the shared Plus3 IT instructions for this repository's tardigrade-ci version to `.agents/plus3it/AGENTS.md`.
2. Read `.agents/plus3it/AGENTS.md` and follow it together with this file. If the sync fails, tell the user, and don't guess the conventions.

These rules always apply, even without the shared instructions:

- Don't push, open pull requests, publish releases, or apply infrastructure changes unless the user asks. List those steps for a person in your final report.
- Don't edit files under `.agents/plus3it/`; they are generated and overwritten by the sync.

@.agents/plus3it/AGENTS.md

## Repository-specific

### Purpose

This Terraform module deploys a Python Lambda function that replaces one Organizations service control policy (SCP) with another on a target, and EventBridge rules that invoke it. The main inputs are `project_name`, `detach_scp_id` (the SCP to detach) and `attach_scp_id` (the SCP to attach); `event_types` selects which of `CreateAccountResult`, `InviteAccountToOrganization` and `CreateOrganizationalUnit` events trigger the function, and `lambda` passes options to the Lambda module. The module has no outputs.

### Module-specific files

- `lambda/src/` — Source of the Lambda function (`replace_scp.py`), packaged by the module with `pip_requirements = true`; `requirements.txt` lists the runtime packages
- `Dockerfile` — Builds on the tardigrade-ci image and installs `lambda/src/requirements.txt` so the Lambda packages are available in the image. The tardigrade-ci `docker/run` target, which the shared lint workflow calls, builds this image when it is not already present

### Deviations from the terraform-module profile

- The Makefile defines a custom `python/deps` target that runs `python -m pip install -r lambda/src/requirements.txt` to install the Lambda dependencies. Neither the workflows nor the tardigrade-ci Makefile call it, and the Terraform test in `tests/test-replace-scp/` does not use it, so run it by hand only when you want the dependencies locally.
- The module has no Python unit tests or Python test workflow. Only the shared lint, test, and release workflows run.
