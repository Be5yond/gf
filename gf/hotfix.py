import typer
from git import Repo
from git.exc import GitCommandError
from .dialog import radiolist_dialog
from .utils import no_traceback as nt

app = typer.Typer()
repo = Repo()


@app.command()
def start(name: str = typer.Argument(..., help='branch name')):
    """create a branch from main branch
    """
    nt(repo.git.checkout)('main')
    branch = repo.create_head(f"H-{name}")
    repo.head.reference = branch
    typer.echo(f'start hotfix {branch}')


@app.command()
def publish(name: str = typer.Argument(repo.head.reference.name, help='branch name')):
    """ publish branch to release 
    """
    nt(repo.git.checkout)('main')
    nt(repo.git.merge)(name)