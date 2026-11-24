# devops-ci-concurrency-audit

A small script that checks GitHub Actions workflows for a missing or weak
`concurrency` block. Without one, every push to a pull request branch starts a
new run while the stale ones keep burning runner minutes.

Only workflows triggered by `pull_request` or `pull_request_target` are checked.
It reports:

- no `concurrency` at the workflow level or on any job
- a group name with no `${{ }}` expression, so every ref shares one queue
- a block that does not set `cancel-in-progress`, so stale runs still finish

`cancel-in-progress` may be an expression such as
`${{ github.event_name == 'pull_request' }}`; that keeps main runs from being
cancelled while PR runs are.

## Usage

```sh
pip install -r requirements.txt
python3 scripts/audit_concurrency.py                  # .github/workflows/*.y*ml
python3 scripts/audit_concurrency.py path/to/ci.yml   # specific files
```

Exit code is 0 when clean and 1 when there are findings.

## Validation

```sh
make validate   # unit tests, actionlint on .github/workflows, and the audit itself
```

`tests/fixtures/` holds one small workflow per rule. `actionlint` must be on
the `PATH`; CI runs the tests and the audit.

## Limits

The audit reads YAML only. It does not resolve reusable workflows
(`uses: ./.github/workflows/x.yml`) or check that a group expression really
varies per ref.
