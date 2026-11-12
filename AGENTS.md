# Working agreement

- Source of truth is this repository. Do not edit a deployed HTML page by hand.
- Use `.venv/bin/python`; set up with `uv venv .venv` then `uv pip install --python .venv/bin/python -e '.[dev]'`.
- Run `.venv/bin/python -m pytest` and the README's real example build before committing.
- Use a fresh directory under out/ for each build. Never build over a live website.
- data/ and out/ are private/derived and must remain untracked. Do not copy production history, credentials, family descriptions or photos into a commit.
- Preserve category pages, AND filtering, pagination and lightbox behavior. Test escaping and path boundaries.
- Review code and engineering habits independently before release. Record evidence under docs/reviews/ without private paths or names.
- Deployment requires inspecting the staging site first. Follow deploy/README.md; never restart unrelated services.
