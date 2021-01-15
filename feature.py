import typer
from dialog import radiolist_dialog
from git import Repo
from git.exc import GitCommandError
app = typer.Typer()
repo = Repo()


@app.command()
def start(name: str = typer.Argument(..., help='branch name')):
    branch = repo.create_head(f"f-{name}")
    repo.head.reference = branch
    typer.echo(f'start branch {branch}')


@app.command()
def submit(name: str = typer.Argument(repo.head.reference.name, help='branch name')):
    """ submit branch to Test 
    """
    repo.git.checkout('test')
    repo.git.merge(name)


@app.command()
def delete():
    values = [(head, head.name) for head in repo.heads if head.name.startswith('f')]
    result = radiolist_dialog(
            title='Choose a branch to delete (Press [Enter] to confirm, [Esc] to cancel):',
            values=values)
    if not result:
        raise typer.Abort()
    if repo.head.reference == result:
        repo.git.checkout('develop')
    try:
        repo.delete_head(result)
    except GitCommandError as e:
        typer.echo(e)
    else:
        typer.echo(f'delete branch {result.name}')

@app.command()
def publish(name: str = typer.Argument(repo.head.reference.name, help='branch name')):
    """ publish branch to release 
    """
    repo.git.checkout('release')
    repo.git.merge(name)
