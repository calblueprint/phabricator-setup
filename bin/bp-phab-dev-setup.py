#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import os
import sys
import urllib
import subprocess

GITHUB_RAW_URL = 'https://raw.githubusercontent.com/calblueprint/phabricator-setup/master'

GITHOOKS = {
    'pre-commit':         '%s/git-hooks/pre-commit',
    'pre-push':           '%s/git-hooks/pre-push',
    'prepare-commit-msg': '%s/git-hooks/prepare-commit-msg',
}
for k, v in GITHOOKS.iteritems():
    GITHOOKS[k] = v % GITHUB_RAW_URL

COMMIT_TEMPLATE_URL = '%s/commit-template' % GITHUB_RAW_URL


class FileNotFoundError(Exception):
    pass


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Configures a Blueprint repo for Phabricator workflow.')
    parser.add_argument(
        '--dir',
        default=os.getcwd(),
        help='directory of repo. default to current directory')
    parser.add_argument(
        '--no-git-hooks',
        action='store_true',
        help='do not install git hook')
    parser.add_argument(
        '--no-commit-template',
        action='store_true',
        help='do set up commit template')
    parser.add_argument(
        '--no-pull-rebase',
        action='store_true',
        help='do not set "git pull --rebase" to default action for "git pull"')
    return parser.parse_args()


def _log_success(msg):
    logging.info('SUCCESS: %s' % msg)


def _log_failure(msg):
    logging.error('FAILURE: %s' % msg)


def _curl_file_to_dst(file_url, dst, chmod=0o644):
    if urllib.urlopen(file_url).getcode() >= 400:
        logging.error("ERROR: couldn't find file at %s" % file_url)
        raise FileNotFoundError
    urllib.urlretrieve(file_url, dst)
    os.chmod(dst, chmod)


def _curl_file_to_buf(file_url):
    f = urllib.urlopen(file_url)
    if f.getcode() >= 400:
        logging.error("ERROR: couldn't find file at %s" % file_url)
        raise FileNotFoundError
    return f.read()


def set_git_hooks(no_template):
    if no_template:
        del GITHOOKS['prepare-commit-msg']
    try:
        for name, url in GITHOOKS.iteritems():
            _curl_file_to_dst(url, '.git/hooks/'+name, chmod=0o755)
    except FileNotFoundError:
        return _log_failure("couldn't configure git hooks")
    _log_success('git hooks configured.')


def set_commit_template():
    try:
        tmpl = _curl_file_to_buf(COMMIT_TEMPLATE_URL)
    except FileNotFoundError:
        return _log_failure("couldn't configure git hooks")
    format_args = {
        'project': raw_input((
            "\nType the name of your project as it appears on Phabricator.\n"
            "(Visit http://phab.calblueprint.org/project/query/active/ for reference.)\n"
            "> ")),
        'project_lead': raw_input((
            "\nType the name of your project leader as it appears on Phabricator.\n"
            "(Visit http://phab.calblueprint.org/people/ for reference.)\n"
            "> ")),
        'teammates': raw_input((
            "\nType the names of your teammates as they appear on Phabricator, comma delimited.\n"
            "(Example: '> caseytaco, generic, tofu, aleks')\n"
            "> "))
    }
    with open('.git/commit-template', 'w+') as f:
        f.write(tmpl.format(**format_args))

    subprocess.check_call(
        'git config --local commit.template .git/commit-template'.split())
    subprocess.check_call(
        'git config --local core.commentchar %'.split())
    subprocess.check_call(
        'arc alias vdiff diff -- --verbatim'.split())

    _log_success('commit template configured.')
    _log_success("be sure to modify '.git/commit-template' for your team's specifics!")


def set_default_pull_rebase():
    subprocess.check_call(
        'git config --local pull.rebase true'.split())
    _log_success('rebase by default on pull configured.')


def _setup_repo(cli_args):
    os.chdir(args.dir)
    if not os.path.isdir('.git'):
        logging.critical('Not a git repo. Exiting...')
        sys.exit(1)

    if not cli_args.no_git_hooks:
        set_git_hooks(cli_args.no_commit_template)
    if not cli_args.no_commit_template:
        set_commit_template()
    if not cli_args.no_pull_rebase:
        set_default_pull_rebase()


if __name__ == '__main__':
    args = _parse_args()

    logging.basicConfig(format='%(message)s')
    logging.getLogger().setLevel(logging.INFO)

    logging.info('Setting up repo for Blueprint Phabricator workflow...')

    _setup_repo(args)
    logging.info('All done!')
