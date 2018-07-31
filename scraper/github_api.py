import itertools

import colorlabels as cl
from decouple import config
from github import Github

from util import merge_whitespaces

gh = Github(config('GITHUB_ACCESS_TOKEN'))


def get_labels(issue):
    for label in issue.labels:
        yield label.name


def github_issue_repo_fetch(repo, since):
    if isinstance(repo, str):
        repo = gh.get_repo(repo)

    cl.plain('Fetching issues from repo: %s' % repo.full_name)

    for issue in repo.get_issues(state='all', since=since):
        yield {
            'id': 'issue-%d' % issue.number,
            'text': merge_whitespaces('%s %s' % (issue.title, issue.body)),
            'type': 'pull' if issue.pull_request else 'issue',
            'created_at': issue.created_at,
            'updated_at': issue.updated_at,
            'closed_at': issue.closed_at,
            'labels': ','.join(get_labels(issue)),
            'state': issue.state,
            'from_issue': None,
            'user_id': issue.user.id,
            'user_login': issue.user.login,
            'user_type': issue.user.type,
            'user_site_admin': issue.user.site_admin
        }

        for comment in issue.get_comments(since=since):
            yield {
                'id': 'comment-%d' % comment.id,
                'text': merge_whitespaces(comment.body),
                'type': 'comment',
                'created_at': comment.created_at,
                'updated_at': comment.updated_at,
                'closed_at': None,
                'labels': None,
                'state': None,
                'from_issue': issue.number,
                'user_id': comment.user.id,
                'user_login': comment.user.login,
                'user_type': comment.user.type,
                'user_site_admin': comment.user.site_admin
            }


def github_issue_org_fetch(org, since):
    org = gh.get_organization(org)
    return itertools.chain(*(
        github_issue_repo_fetch(repo, since) for repo in org.get_repos()))
