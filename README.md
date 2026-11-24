# devops-ci-concurrency-audit

A small script that checks GitHub Actions workflows for a missing or weak
`concurrency` block. Without one, every push to a pull request branch starts a
new run while the stale ones keep burning runner minutes.

Rules are added in later commits; this README tracks them.
