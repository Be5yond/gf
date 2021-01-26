import typer
from git import Repo
from prompt_toolkit.formatted_text import HTML
from .dialog import radiolist_dialog, ansired
from .utils import no_traceback as nt

app = typer.Typer(help='start/submit/delete a feature branch')
repo = Repo()


@app.command()
def start(name: str = typer.Argument(..., help='branch name')):
    """create a branch from main branch
    """
    nt(repo.git.checkout)('develop')
    branch = repo.create_head(f"f-{name}")
    repo.head.reference = branch
    typer.echo(f'start feature {branch}')


@app.command()
def submit(name: str = typer.Argument(repo.head.reference.name, help='branch name')):
    """ submit branch to Test branch.
    """
    nt(repo.git.checkout)('test')
    nt(repo.git.merge)(name)


@app.command()
def delete():
    values = [(head, head.name) for head in repo.heads if head.name.startswith('f')]
    result = radiolist_dialog(
            title=HTML(f'Choose a branch to delete (Press {ansired("Enter")} to confirm, {ansired("Esc")} to cancel):'),
            values=values)
    if not result:
        raise typer.Abort()
    if repo.head.reference == result:
        nt(repo.git.checkout)('develop')
    nt(repo.delete_head)(result)
    # except GitCommandError as e:
    #     typer.echo(e)
    # else:
    #     typer.echo(f'delete branch {result.name}')

@app.command()
def finish(name: str = typer.Argument(repo.head.reference.name, help='branch name')):
    """ publish branch to release 
    """
    nt(repo.git.checkout)('main')
    nt(repo.git.merge(name))
