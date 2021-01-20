import typer
from git import Repo
from .utils import no_traceback as nt

app = typer.Typer(help='start/finish a hotfix branch')
repo = Repo()


def branch_validate(value: str):
    if not value.startswith("H-"):
        raise typer.BadParameter(f"Wrong branch name!, should be a hotfix branch ,current is: < {value} >")
    return value


@app.command()
def start(name: str = typer.Argument(..., help='branch name')):
    """create a branch from main branch
    """
    nt(repo.git.checkout)('main')
    branch = repo.create_head(f"H-{name}")
    repo.head.reference = branch
    typer.echo(f'start hotfix {branch}')


@app.command()
def finish(name: str = typer.Argument(repo.head.reference.name, help='branch name', callback=branch_validate)):
    """ merge branch to main branch and delete this branch.
    """

    nt(repo.git.checkout)('main')
    nt(repo.git.merge)(name)
    typer.echo(f'merge {name} -> main')
    head = repo.heads[name]
    repo.delete_head(head)

