# GitHub Actions CI/CD Pipeline for valid8r

This document visualizes the complete CI/CD pipeline using Mermaid diagrams.

## Developer Workflow → CI → Release → Publish

```mermaid
graph TB
    Start([Developer: Create Feature Branch])
    Commit[Commit with Conventional Format<br/>feat: add UUID parser]
    PR[Create Pull Request]

    Start --> Commit
    Commit --> PR

    subgraph CI["CI Workflow (ci.yml) - Runs on PR + Push to Main"]
        Lint[Lint & Format<br/>ruff]
        Type[Type Check<br/>mypy]
        Docs[Build Docs<br/>sphinx]

        Test311[Unit Tests<br/>Python 3.11]
        Test312[Unit Tests<br/>Python 3.12]
        Test313[Unit Tests<br/>Python 3.13]
        Test314[Unit Tests<br/>Python 3.14]

        BDD[BDD Tests<br/>behave]
        Smoke[Smoke Test]
        DocTest[Doc Tests]

        AllChecks[All Checks Pass]

        Lint --> AllChecks
        Type --> AllChecks
        Docs --> AllChecks
        Test311 --> AllChecks
        Test312 --> AllChecks
        Test313 --> AllChecks
        Test314 --> AllChecks
        BDD --> AllChecks
        Smoke --> AllChecks
        DocTest --> AllChecks
    end

    PR --> Lint
    PR --> Type
    PR --> Docs
    PR --> Test311
    PR --> Test312
    PR --> Test313
    PR --> Test314
    PR --> BDD
    PR --> Smoke
    PR --> DocTest

    Review[Get Review & Merge to Main]
    AllChecks --> Review

    subgraph Release["Semantic Release Workflow (semantic-release.yml)"]
        Analyze[Analyze Conventional Commits<br/>feat: → minor<br/>fix: → patch<br/>BREAKING: → major]
        Bump[Update pyproject.toml Version]
        Tag[Create Git Tag v0.2.0]
        Changelog[Generate Changelog]
        GHRelease[Create GitHub Release]

        Analyze --> Bump
        Bump --> Tag
        Tag --> Changelog
        Changelog --> GHRelease
    end

    Review --> Analyze

    subgraph Publish["Publish to PyPI Workflow (publish-pypi.yml)"]
        Build[Build Package<br/>uv build]
        Verify[Test Built Package<br/>Python 3.11-3.14]
        PyPI[Publish to PyPI]

        Build --> Verify
        Verify --> PyPI
    end

    GHRelease --> Build

    Success([✓ Package Available<br/>pip install valid8r])
    PyPI --> Success

    style Start fill:#e1f5e1
    style Success fill:#e1f5e1
    style AllChecks fill:#fff4e1
    style Review fill:#e1f0ff
```

## Conventional Commit Examples

```mermaid
graph LR
    subgraph "Version Bumps"
        Feat["feat: add UUID parser<br/>0.1.0 → 0.2.0 (minor)"]
        Fix["fix: handle None values<br/>0.1.0 → 0.1.1 (patch)"]
        Docs["docs: update examples<br/>0.1.0 → 0.1.1 (patch)"]
        Breaking["feat!: redesign API<br/>0.1.0 → 1.0.0 (major)"]
        CI["ci: update workflows<br/>no bump"]

        style Feat fill:#d4edff
        style Fix fill:#ffe4d4
        style Docs fill:#e8f5e8
        style Breaking fill:#ffd4d4
        style CI fill:#f0f0f0
    end
```

## Python Version Support Matrix

| Python Version | Status | Notes |
|----------------|--------|-------|
| 3.11 | ✅ Supported | Minimum required version |
| 3.12 | ✅ Supported | Recommended |
| 3.13 | ✅ Supported | Latest stable |
| 3.14 | ✅ Supported | Latest release |

## CI Job Details

```mermaid
graph TB
    subgraph "Parallel CI Jobs"
        subgraph "Quality Checks"
            L[Lint: ruff check]
            F[Format: ruff format]
            I[Import Sort: isort]
            T[Type Check: mypy]
        end

        subgraph "Test Matrix"
            T1[pytest + coverage<br/>Python 3.11]
            T2[pytest + coverage<br/>Python 3.12]
            T3[pytest + coverage<br/>Python 3.13]
            T4[pytest + coverage<br/>Python 3.14]
        end

        subgraph "Integration"
            B[BDD Tests<br/>behave]
            D[Doc Tests<br/>tox -e doctests]
            S[Smoke Test]
            DB[Build Docs<br/>sphinx]
        end
    end

    style L fill:#e3f2fd
    style F fill:#e3f2fd
    style I fill:#e3f2fd
    style T fill:#e3f2fd
    style T1 fill:#f3e5f5
    style T2 fill:#f3e5f5
    style T3 fill:#f3e5f5
    style T4 fill:#f3e5f5
    style B fill:#e8f5e9
    style D fill:#e8f5e9
    style S fill:#e8f5e9
    style DB fill:#e8f5e9
```

## Manual Workflow Triggers

```bash
# Override automatic version detection
gh workflow run semantic-release.yml

# Trigger CI manually
gh workflow run ci.yml

# Re-run publish workflow
gh workflow run publish-pypi.yml
```

## Useful Links

- **Actions**: https://github.com/mikelane/valid8r/actions
- **Releases**: https://github.com/mikelane/valid8r/releases
- **PyPI**: https://pypi.org/project/valid8r/
- **Docs**: https://valid8r.readthedocs.io/

## Migration Note: Poetry → uv

As of this migration, all workflows use `uv` for dependency management:
- `poetry install` → `uv sync`
- `poetry run` → `uv run`
- `poetry build` → `uv build`

Performance improvements:
- CI runs: 8-12 min → 3-5 min (60% faster)
- Dependency resolution: ~2-3 min → ~380ms (300x+ faster)
