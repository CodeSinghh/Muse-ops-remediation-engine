# AIOps Log Analysis and Terraform Remediation

A small Python prototype that turns high-signal application and Kubernetes log lines into a model-assisted root-cause analysis (RCA) and a proposed Terraform patch. It uses Baseten's Muse model for analysis and generation, then asks Terraform to validate and plan the proposed change.

This repository is a human-reviewed prototype, not a production-ready autonomous operator. The model's output is untrusted until an operator has inspected it and independently reviewed the Terraform plan.

## At A Glance

1. Read `sample_logs.log` and keep lines matching configured error and infrastructure-failure patterns.
2. Send the extracted events to Baseten's `meta-models/muse-spark-open-1026` model.
3. Ask Muse for an RCA and a Terraform patch in JSON format.
4. Normalize the response, save the patch as `remediation_patch.tf`, and run Terraform formatting and validation.
5. Pause for operator input, then initialize Terraform and create a plan file named `tfplan`.

The current `main.py` path does **not** apply the plan. Pressing Enter passes through the approval prompt, but the executor is called with `auto_apply=False`. Review the code and plan before considering any separate apply operation.

## Where Muse Fits

Muse is the reasoning and generation step in this project. The Python code prepares filtered log events as JSON and sends them to Baseten's OpenAI-compatible inference API. The system prompt asks Muse to:

- Explain the likely root cause in concise form.
- Draft a Terraform HCL patch intended to address the infrastructure issue.
- Return exactly two JSON fields: `rca` and `terraform_patch`.

The model is configured with temperature `0.0` to make output more consistent. Its response is not executed directly: the normalizer parses it, the validator writes and checks the HCL, and the pipeline pauses before Terraform planning. Muse can help explain incidents and draft a candidate fix; it cannot establish that the diagnosis is correct, that the patch is safe for a particular environment, or that applying it is appropriate.

For an AI assistant or coding agent reading this repository, use `main.py` and the modules it imports as the current implementation. Treat generated files and logs as examples or run artifacts, not as authoritative design documentation. Do not claim that a change has been applied to a cluster: this pipeline currently stages a plan only. Never expose or copy credentials from `.env` or `env.txt` into source, logs, prompts, or documentation.

## Requirements

- Python 3.9 or later (the executor uses built-in generic type annotations such as `tuple[bool, str]`).
- Terraform CLI available on `PATH`.
- A Baseten API key with access to the configured Muse model.
- A Terraform root module and provider credentials/configuration suitable for the infrastructure you intend to plan against. Do not point this prototype at production without a separate operational and security review.

Python packages used by the active pipeline:

- `openai`
- `python-dotenv`

Install them in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install openai python-dotenv
```

## Configuration

Create a local `.env` file in the project directory and set the Baseten credential:

```dotenv
BASETEN_API_KEY=your_baseten_api_key
```

Keep the key private. Do not commit `.env`, `env.txt`, or any other file containing credentials. The model endpoint and model identifier are currently set in `agent.py`; the pipeline loads `.env` with `python-dotenv`.

## Run

From the project directory, with the virtual environment activated and Terraform installed:

```bash
python main.py
```

The active pipeline reads `sample_logs.log`. To analyze a different log file, either replace that sample input or change the `log_file` value in `main.py`. The parser only forwards lines that match its configured high-signal patterns, such as `ERROR`, `FATAL`, `OOMKilled`, `CrashLoopBackOff`, `Timeout`, or `AccessDenied`.

At the operator prompt:

- Type `abort` to stop before Terraform initialization and planning.
- Press Enter to continue to Terraform initialization and plan creation.

Pressing Enter does not apply the plan, despite the prompt text. A successful run stages `tfplan`; inspect the configuration and plan independently before deciding what to do next.

## Project Structure

| File | Purpose |
| --- | --- |
| `main.py` | Orchestrates the active end-to-end pipeline and human review prompt. |
| `parser.py` | Filters a log file into structured high-signal events. |
| `agent.py` | Calls Baseten Muse and requests RCA plus Terraform HCL. |
| `normalizer.py` | Parses Muse's JSON response into `rca` and `terraform_patch`. |
| `validator.py` | Writes the patch and runs Terraform formatting, initialization without a backend, and validation. |
| `remediation_executor.py` | Initializes Terraform and creates `tfplan`; applying is conditional on `auto_apply=True`. |
| `metrics_tracker.py` | Records model token usage and an estimated cost in `.metrics_log.json`. |
| `sample_logs.log` | Default input used by `main.py`. |
| `payment-api-oom-crashloop.log`, `real_incident.log` | Additional example log inputs; not selected by `main.py` by default. |
| `check_metrics.py` | Separate endpoint/token probe; it is not part of the main pipeline. |
| `pipeline_runner.py` | Older prototype that imports modules not present in this repository; it is not the supported entry point. |

Generated or local runtime artifacts include `remediation_patch.tf`, `tfplan`, `.metrics_log.json`, `.pipeline_state.json`, Terraform working data, and raw model responses. Review `.gitignore` before deciding whether any such artifact belongs in version control.

## Safety and Data Handling

- Log events selected by the parser are sent to an external Baseten inference endpoint. Confirm that your organization permits sending the relevant log data to that service; redact secrets, personal data, tokens, and sensitive identifiers before running.
- Treat both the RCA and Terraform patch as model-generated suggestions. Verify resource names, provider assumptions, limits, and blast radius against the actual infrastructure.
- `terraform validate` checks Terraform configuration validity; it does not prove that a change is operationally correct or safe.
- `terraform plan` can contact configured providers and may disclose configuration details to them. Review the plan and the target account/workspace before any apply.
- The interactive prompt is not a production authorization system. The current pipeline does not apply changes, but `remediation_executor.py` contains an apply path when called with `auto_apply=True`. Do not enable that path without deliberate safeguards, approval controls, and testing.
- Token-cost values are local estimates based on rates hard-coded in `metrics_tracker.py`; they are not an invoice or a source of truth for Baseten billing.

## Current Limitations

- `main.py` uses a fixed input filename (`sample_logs.log`) and the model endpoint/model identifier are configured in source.
- Parser coverage is regex-based; events that do not match its patterns are omitted from the model context.
- Model output parsing expects JSON with `rca` and `terraform_patch`; malformed or incomplete responses stop the pipeline.
- Terraform validation and planning depend on the Terraform configuration and provider setup in the working directory. HCL syntax validation alone does not establish that the patch targets the intended resources.
- There is no automated test suite or production approval integration included in this repository.
