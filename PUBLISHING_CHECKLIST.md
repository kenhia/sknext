# PyPI Publishing Checklist

## Pre-Publishing Setup (One-Time)

- [ ] **PyPI Account Setup**
  - [ ] Create account on [PyPI](https://pypi.org)
  - [ ] Create account on [TestPyPI](https://test.pypi.org)

- [ ] **Configure Trusted Publishing on PyPI**
  - [ ] Add pending publisher for `sknext` on PyPI:
    - Project Name: `sknext`
    - Owner: `kenhia`
    - Repository: `sknext`
    - Workflow: `publish.yml`
    - Environment: `pypi`
  - [ ] Add pending publisher for `sknext` on TestPyPI (use environment: `testpypi`)

- [ ] **GitHub Repository Setup**
  - [ ] Push repository to GitHub as `kenhia/sknext`
  - [ ] Create GitHub environment: `pypi`
  - [ ] Create GitHub environment: `testpypi`
  - [ ] (Optional) Add protection rules to `pypi` environment

## Before Each Release

- [ ] **Code Quality**
  - [ ] All tests pass locally (`uv run pytest`)
  - [ ] No linting errors (`uv run ruff check .`)
  - [ ] No formatting issues (`uv run ruff format --check .`)
  - [ ] No type errors (`uv run mypy src/sknext`)

- [ ] **Documentation**
  - [ ] Update version number in `pyproject.toml`
  - [ ] Update CHANGELOG or create release notes
  - [ ] Review README.md for accuracy
  - [ ] Ensure all new features are documented

- [ ] **Build Testing**
  - [ ] Build package locally: `uv build`
  - [ ] Verify package: `uv run twine check dist/*`
  - [ ] Inspect contents: `tar -tzf dist/sknext-*.tar.gz`
  - [ ] Test local installation: `uv pip install dist/sknext-*.whl`

## Publishing Process

- [ ] **Commit and Tag**
  - [ ] Commit version bump: `git commit -am "chore: bump version to X.Y.Z"`
  - [ ] Push to main: `git push`
  - [ ] Create git tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
  - [ ] Push tag: `git push origin vX.Y.Z`

- [ ] **Create GitHub Release**
  - [ ] Go to GitHub Releases page
  - [ ] Click "Create a new release"
  - [ ] Select the version tag (vX.Y.Z)
  - [ ] Add release title and notes
  - [ ] Click "Publish release"

- [ ] **Verify CI/CD**
  - [ ] Check GitHub Actions for workflow run
  - [ ] Verify build job completes successfully
  - [ ] Verify TestPyPI publication succeeds
  - [ ] Verify PyPI publication succeeds

## Post-Publishing Verification

- [ ] **Package Verification**
  - [ ] Check package on PyPI: https://pypi.org/project/sknext/
  - [ ] Check package on TestPyPI: https://test.pypi.org/project/sknext/
  - [ ] Test installation from PyPI: `pip install sknext`
  - [ ] Test CLI works: `sknext --version`

- [ ] **Cleanup**
  - [ ] Clean local dist directory: `rm -rf dist/`
  - [ ] Update project board or issues with release info

## Troubleshooting Reference

If publishing fails, check [PUBLISHING.md](PUBLISHING.md#troubleshooting) for common issues and solutions.

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 0.1.0   | TBD  | Initial release |
