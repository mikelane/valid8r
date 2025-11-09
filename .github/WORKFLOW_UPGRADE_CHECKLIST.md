# Workflow Action Upgrade Checklist

When upgrading GitHub Actions, follow this checklist to avoid breaking changes.

## Before Upgrading

- [ ] Check action's CHANGELOG for breaking changes
- [ ] Review action's `action.yml` for input parameter changes
- [ ] Review action's `action.yml` for output changes
- [ ] Check for deprecated features being removed
- [ ] Note the major version jump (e.g., v1 → v3 is high risk)

## Common Breaking Changes

1. **Parameter name changes** (e.g., kebab-case → snake_case)
2. **Required inputs added**
3. **Default values changed**
4. **Output format changes**
5. **Runner requirements changed** (node version, OS support, etc.)
6. **Authentication methods changed**
7. **Permissions requirements changed**

## During Upgrade

- [ ] Update parameter names if changed
- [ ] Update output references if changed
- [ ] Update permissions if required
- [ ] Test workflow syntax: `yamllint .github/workflows/*.yml`
- [ ] Review diff carefully before committing
- [ ] Update workflow comments with review date

## After Upgrade

- [ ] Monitor first workflow run for failures
- [ ] Check workflow logs for deprecation warnings
- [ ] Update documentation if workflow behavior changed
- [ ] Add comment to PR noting any behavioral changes

## Example: actions/first-interaction v1 → v3

**Breaking changes:**
- `repo-token` → `repo_token`
- `issue-message` → `issue_message`
- `pr-message` → `pr_message`

**Lesson:** Always check action.yml even for "simple" actions.

## Resources

- [GitHub Actions Breaking Changes](https://github.blog/changelog/label/actions/)
- Action repositories usually have a CHANGELOG.md or RELEASES page
- Use `gh api repos/OWNER/REPO/readme --jq .content | base64 -d` to view README
- Check action.yml directly: `https://github.com/OWNER/REPO/blob/VERSION/action.yml`

## Workflow Upgrade Template Commit Message

```
chore: upgrade OWNER/ACTION from vX to vY

Breaking changes:
- parameter_old → parameter_new
- output_old → output_new

Verified:
- Workflow syntax valid
- First run successful
- No deprecation warnings

Refs: https://github.com/OWNER/ACTION/releases/tag/vY
```
