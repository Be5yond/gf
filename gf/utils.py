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
    dates = re.findall('{[\d-]+}', txt)
    return dates[-1]
