# Releasing morphoview to PyPI

Publishing is automated by
[`.github/workflows/publish.yml`](.github/workflows/publish.yml). It builds
the sdist and wheel on every push/PR as a smoke test, and uploads them to
PyPI when a GitHub Release is published, using
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC) — so
there are no API tokens to store as secrets.

## One-time PyPI setup

At <https://pypi.org/manage/account/publishing/> add a *pending publisher*
for this project with:

- PyPI project name: `morphoview`
- Owner: `subhacom`
- Repository: `morphoview`
- Workflow: `publish.yml`
- Environment: `pypi`

The Environment field must be `pypi` to match the `environment:` declared in
the workflow — a blank Environment box is the most common cause of an
`invalid-publisher` error.

## Cutting a release

1. Bump `version` in `pyproject.toml` (and commit).
2. Create a GitHub Release with a tag matching that version, e.g. `v0.1.0`
   (the leading `v` is optional). The workflow verifies the tag matches
   `pyproject.toml` and fails fast on a mismatch.
3. Publishing runs automatically once the release is published.
