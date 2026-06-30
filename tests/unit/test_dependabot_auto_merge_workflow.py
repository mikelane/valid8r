from __future__ import annotations

from pathlib import Path

import pytest
import yaml

WORKFLOW_PATH = Path(__file__).resolve().parents[2] / '.github' / 'workflows' / 'dependabot-auto-merge.yml'


class DescribeDependabotAutoMergeWorkflow:
    @pytest.fixture(autouse=True)
    def _load_workflow(self) -> None:
        self.workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding='utf-8'))
        self.steps = self.workflow['jobs']['review-dependabot-pr']['steps']

    def it_gates_auto_merge_for_major_production_updates(self) -> None:
        """Auto-merge must not be enabled for major production dependency updates.

        Major production updates are explicitly flagged as requiring manual QA via
        the 'requires-manual-qa' label. Enabling auto-merge on these PRs creates a
        footgun: any subsequent human approval (possibly accidental) causes an
        automatic merge of a potentially breaking production dependency change.
        """
        auto_merge_step = next(
            (step for step in self.steps if step.get('name') == 'Enable auto-merge for Dependabot PRs'),
            None,
        )
        assert auto_merge_step is not None, 'Expected an auto-merge step'
        condition = auto_merge_step.get('if', '')
        assert condition, (
            'Auto-merge step must have an `if:` guard that excludes '
            'version-update:semver-major + direct:production updates'
        )
        assert 'version-update:semver-major' in condition or 'dependency-type' in condition, (
            'Auto-merge guard must reference major production update classification'
        )

    def it_uses_an_elevated_token_for_merge(self) -> None:
        """Merging workflow-modifying PRs requires workflows:write.

        The automatic GITHUB_TOKEN cannot be granted workflows:write, so the merge
        step must use a dedicated PAT stored as a repository secret. Reviews and
        comments use the standard GITHUB_TOKEN because they only need pull-requests:write.
        """
        auto_merge_step = next(
            (step for step in self.steps if step.get('name') == 'Enable auto-merge for Dependabot PRs'),
            None,
        )
        assert auto_merge_step is not None, 'Expected an auto-merge step'
        token_ref = auto_merge_step.get('env', {}).get('GITHUB_TOKEN', '')
        assert token_ref, 'Auto-merge step must specify a GITHUB_TOKEN env var'
        assert 'DEPENDABOT_WORKFLOW_TOKEN' in token_ref, (
            'Auto-merge step must use the DEPENDABOT_WORKFLOW_TOKEN secret '
            'because GITHUB_TOKEN cannot be granted workflows:write'
        )

    def it_does_not_request_workflows_write_for_github_token(self) -> None:
        """workflows:write is not an available permission for GITHUB_TOKEN.

        GitHub Actions rejects workflow files that request permissions the automatic
        token cannot possess. The job should only request the permissions it actually
        needs for reviews, comments, and labels.
        """
        job = self.workflow['jobs']['review-dependabot-pr']
        permissions = job.get('permissions', {})
        assert 'workflows' not in permissions, (
            'GITHUB_TOKEN cannot be granted workflows:write; requesting it makes the workflow file fail validation'
        )

    def it_only_requests_pull_requests_write_for_github_token(self) -> None:
        """Least privilege for the automatic GITHUB_TOKEN.

        Reviews, comments, and labels only need pull-requests:write. The merge step
        uses a dedicated PAT, so contents:write is not required for GITHUB_TOKEN.
        """
        job = self.workflow['jobs']['review-dependabot-pr']
        permissions = job.get('permissions', {})
        assert set(permissions.keys()) == {'pull-requests'}, (
            'GITHUB_TOKEN should only be granted pull-requests:write; the PAT handles the workflows:write merge'
        )

    def it_prevents_duplicate_comments_on_pr_updates(self) -> None:
        """pull_request_target defaults to running on synchronize events.

        Without either (a) an event-type filter that skips synchronize, or (b)
        idempotency guards on the comment/label step, every push to a Dependabot
        PR re-runs the workflow and posts another 'requires manual QA' comment.
        """
        # PyYAML parses the YAML keyword `on:` as the Python boolean `True`, so we
        # must look up the trigger map by its canonical parsed key.
        triggers = self.workflow.get(True, {})
        if isinstance(triggers, list):
            pull_request_target = {'types': ['opened', 'synchronize', 'reopened']}
        else:
            pull_request_target = triggers.get('pull_request_target', {}) or {}

        event_types = pull_request_target.get('types', ['opened', 'synchronize', 'reopened'])
        runs_on_synchronize = 'synchronize' in event_types

        comment_step = next(
            (
                step
                for step in self.steps
                if step.get('name') == 'Comment on major updates of non-development dependencies'
            ),
            None,
        )
        assert comment_step is not None, 'Expected a comment step for major production updates'

        has_idempotency_guard = any(
            marker in (comment_step.get('if') or '').lower()
            for marker in ['contains', 'missing', 'not exists', 'unique']
        )

        assert not runs_on_synchronize or has_idempotency_guard, (
            'Workflow runs on synchronize events but the comment/label step has no '
            'idempotency guard; this spams duplicate comments on every PR update'
        )
