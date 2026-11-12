# Initial source-preparation evidence

Date: 2026-11-12. This is a local preparation result, not a public release or a production-deployment acceptance.

## Executed

```text
$ .venv/bin/python -m pytest -q
s..................                                                      [100%]
18 passed, 1 skipped in 0.15s

$ .venv/bin/python -m oldphoto_archive --catalog examples/catalog.json --images examples/photos --output out/reviewed-example
counts: color=1, bw=1, id=1
```

The same repository generator also built a private staging catalog with 302 published records: color=230, bw=58, id=14. Private data/output are excluded from the repository; the original site's data and live output were not overwritten. No database writeback was executed.

The local venv uses an editable install of this repository. Offline dependency installation lacked cached packages, so the local test environment reuses preinstalled test tools through an untracked `.pth`. Runtime generation itself has zero third-party dependencies; downstream installation should use the documented clean installation. A clean online dependency installation has not been tested here.

## Independent review

A read-only review found image-URL encoding and header-nesting issues; both were corrected. Added invalid-config validation before output creation. Independent review did not find another path traversal or text-injection defect in its inspected code, but this is not a security certification.

## Outstanding acceptance gate

The explicit Playwright run failed when Chromium startup was forbidden by the execution sandbox (`Operation not permitted`). An escalation request to run the local-file browser test was rejected. No alternative browser invocation was attempted. The browser test remains present and is enabled in CI; CI has not run yet. Do not report end-to-end browser verification as passed.

No GitHub repository has been created or pushed. No production service was restarted or switched to this generator. Source-first deployment is documented under deploy/, but the existing Immich-driven update adapter still requires a reviewed migration before replacing the old production build path.
