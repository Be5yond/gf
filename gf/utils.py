import re
import git
import typer
from git.exc import GitCommandError

repo= git.Repo()


def no_traceback(f):
    """block out python traceback message"""
    def _wapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except GitCommandError as e:
            # typer.echo(e)
            raise typer.Exit(e)
    return _wapper


def get_create_time(branch_name: str):
    """Get branch creation time"""
    txt = repo.git.reflog(branch_name, date='short')
    try:
        dates = re.findall('{[\d-]+}', txt)
        return dates[-1]
    except IndexError:
        return ''


def index_status():
    """Get staged, modified, untracked file"""
    empty = [(None, 'Empty!')]
    staged = [(diff.a_path, diff.a_path) for diff in repo.index.diff('HEAD')] or empty
    modified = [(diff.a_path, diff.a_path) for diff in repo.index.diff(None)] or empty
    untracked = [(path, path) for path in repo.untracked_files] or empty
    return (staged, modified, untracked)