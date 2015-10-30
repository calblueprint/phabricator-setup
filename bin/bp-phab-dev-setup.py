#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import sys
import urllib
import subprocess
import shutil
import ConfigParser
from StringIO import StringIO

GITHUB_RAW_URL = 'https://raw.githubusercontent.com/calblueprint/phabricator-setup/master'

GITHOOKS = {
    'pre-commit':         '%s/git-hooks/pre-commit',
    'pre-push':           '%s/git-hooks/pre-push',
    'prepare-commit-msg': '%s/git-hooks/prepare-commit-msg',
}
for k, v in GITHOOKS.iteritems():
    GITHOOKS[k] = v % GITHUB_RAW_URL

COMMIT_TEMPLATE_URL = '%s/commit-template' % GITHUB_RAW_URL


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Configures a Blueprint repo for Phabricator workflow.')
    parser.add_argument(
        '--dir',
        default=os.getcwd(),
        help='directory of repo. default to current directory')
    parser.add_argument(
        '--undo',
        action='store_true',
        help='undo all bp phab settings')
    parser.add_argument(
        '--no-git-hooks',
        action='store_true',
        help='do not install git hook')
    parser.add_argument(
        '--no-commit-template',
        action='store_true',
        help='do not set up commit template')
    parser.add_argument(
        '--no-arc-alias',
        action='store_true',
        help='do not set up arc alias')
    parser.add_argument(
        '--no-pull-rebase',
        action='store_true',
        help='do not set "git pull --rebase" to default action for "git pull"')
    return parser.parse_args()

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[%d;3%dm"


def _color(string, color, bold=False):
    return (COLOR_SEQ % (1 if bold else 0, color)) + string + RESET_SEQ


def _log_info(msg):
    print _color(msg, GREEN)


def _log_success(msg):
    print _color('SUCCESS: ' + msg, BLUE)


def _log_failure(msg):
    print _color('FAILURE: ' + msg, YELLOW)


def _critical(msg):
    print _color('CRITICAL: ' + msg, RED)
    sys.exit(1)


def _curl_file_to_dst(file_url, dst, chmod=0o644):
    if urllib.urlopen(file_url).getcode() >= 400:
        _critical("couldn't find file at %s" % file_url)
    urllib.urlretrieve(file_url, dst)
    os.chmod(dst, chmod)


def _curl_file_to_buf(file_url):
    f = urllib.urlopen(file_url)
    if f.getcode() >= 400:
        _critical("couldn't find file at %s" % file_url)
    return f.read()


def set_git_hooks(no_template):
    if no_template:
        del GITHOOKS['prepare-commit-msg']
    for name, url in GITHOOKS.iteritems():
        _curl_file_to_dst(url, '.git/hooks/'+name, chmod=0o755)
    _log_success('git hooks configured.')


def set_commit_template():
    if os.path.isfile('.git/commit-template'):
        with open('.git/commit-template', 'r') as f:
            delim = _color(
                '############################################################',
                GREEN)
            print delim
            print f.read().rstrip()
            print delim
            print
        if _yn_query("Would you like to re-use this existing template?"):
            return
    tmpl = _curl_file_to_buf(COMMIT_TEMPLATE_URL)
    format_args = {
        'project': raw_input(_color((
            "\nType the name of your project as it appears on Phabricator.\n"
            "(Visit "), GREEN) + _color("http://phab.calblueprint.org/project/query/active/", GREEN, True) +
            _color(" for reference.)\n> ", GREEN)),
        'project_lead': raw_input(_color((
            "\nType the name of your project leader as it appears on Phabricator.\n"
            "If you are the project leader, you should probably leave this blank.\n"
            "(Visit "), GREEN) + _color("http://phab.calblueprint.org/people/", GREEN, True) +
            _color(" for reference.)\n> ", GREEN)),
        'teammates': raw_input(_color((
            "\nType the names of your teammates as they appear on Phabricator, comma delimited.\n"
            "(Example: '> caseytaco, generic, tofu, aleks')\n"
            "> "), GREEN))
    }
    with open('.git/commit-template', 'w+') as f:
        f.write(tmpl.format(**format_args))

    subprocess.check_call(
        'git config --local commit.template .git/commit-template'.split())

    _log_success('commit template configured.')


def set_arc_alias():
    subprocess.check_call(
        ['arc', 'alias', 'vdiff',
         '! $(arc which | grep -q "No revisions match") && arc diff --verbatim $* || arc diff $*'])
    # don't need to log success here because arc should do it for us


def set_default_pull_rebase():
    subprocess.check_call('git config --local pull.rebase true'.split())
    _log_success('rebase by default on pull configured.')


def backup_orig_config():
    if not os.path.isfile('.git/prebpphab_config'):
        shutil.copy('.git/config', '.git/prebpphab_config')


def _yn_query(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(_color(question + prompt, GREEN))
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write(
                _color("Please respond with 'y(es)' or 'n(o)'. ", GREEN)
            )


# Source: http://stackoverflow.com/a/23145275
def _read_gitconfig(parser, path):
    with open(path) as f:
        c = f.readlines()
    parser.readfp(StringIO(''.join([l.lstrip() for l in c])))


def _undo_repo():
    _log_info('Undoing Blueprint Phabricator workflow setup...')

    # remove hooks
    for hook in GITHOOKS.iterkeys():
        path = '.git/hooks/'+hook
        if os.path.isfile(path):
            os.remove(path)
    _log_success("removed git hooks.")

    # remove commit template
    if os.path.isfile('.git/commit-template'):
        os.remove('.git/commit-template')
    _log_success("removed commit template.")

    backup_found = True
    if not os.path.isfile('.git/prebpphab_config'):
        backup_found = False
        if not _yn_query("Could not find backup config file. Would you like to reset to defaults anyway?"):
            _critical("No backup config file, aborting.")

    # restore to default options
    options = [
        ('pull', 'rebase'),
        ('commit', 'template')
    ]
    if backup_found:
        backup_cfg = ConfigParser.ConfigParser()
        _read_gitconfig(backup_cfg, '.git/prebpphab_config')
        cfg = ConfigParser.ConfigParser()
        _read_gitconfig(cfg, '.git/config')
        for sec, opt in options:
            if backup_cfg.has_option(sec, opt):
                subprocess.check_call(
                    ('git config --local %s.%s %s' % (sec, opt, backup_cfg.get(sec, opt))).split()
                )
                cfg.set(sec, opt, backup_cfg.get(sec, opt))
            else:
                subprocess.check_call(
                    ('git config --local --unset %s.%s' % (sec, opt)).split()
                )
    else:
        for sec, opt in options:
            subprocess.check_call(
                ('git config --local --unset %s.%s' % (sec, opt)).split()
            )
    _log_success("restored repo git config options.")

    # unalias `arc vdiff`
    subprocess.check_call('arc alias vdiff'.split())
    _log_success("unaliased vdiff")

    # remove backup config
    if os.path.isfile('.git/prebpphab_config'):
        os.remove('.git/prebpphab_config')
    _log_success("removed pre-phabricator backup config")


def _setup_repo(cli_args):
    os.chdir(args.dir)
    if not os.path.isdir('.git'):
        _critical('Not at the root of the git repo! Exiting...')

    if cli_args.undo:
        _undo_repo()
        return

    _log_info('Setting up repo for Blueprint Phabricator workflow...')

    backup_orig_config()
    if not cli_args.no_git_hooks:
        set_git_hooks(cli_args.no_commit_template)
    if not cli_args.no_commit_template:
        set_commit_template()
    if not cli_args.no_arc_alias:
        set_arc_alias()
    if not cli_args.no_pull_rebase:
        set_default_pull_rebase()


if __name__ == '__main__':
    args = _parse_args()
    _setup_repo(args)
    _log_info('All done!')
