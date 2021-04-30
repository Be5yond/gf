import typer
from prompt_toolkit import print_formatted_text, HTML
from .utils import repo

app = typer.Typer(help='Submodule management')

@app.command()
def list():
    """ list submodules of the repository
    """
    for sub in repo.submodules:
        print_formatted_text(f'{sub.hexsha[:7]}, {sub.name}')


@app.command()
def update():
    """ Update all submodule to latest version
    """
    for sub in repo.submodules:
        origin = sub.module().remote()
        origin.pull()


@app.command()
def commit():
    """ submit commit to all changed submodules repository using the lastest commit message.
    """
    message = repo.head.commit.message
    for sub in repo.submodules:
        sub_repo = sub.module()
        if not sub_repo.index.diff("HEAD"):
            typer.echo('no changes added to commit')
        else:
            typer.echo(message)
            sub_repo.index.commit(message)


@app.command()
def add(url:str = typer.Argument(..., help="The url of the submodule repository."),
        path: str = typer.Argument('default', help='local path of the submodule. defualt: ./{submodue_name}')):
    """ add new submodule of the repository
    """
    name = url.rpartition('/')[-1]
    if path == 'deafult':
        path=name
    repo.create_submodule(name=name, path=path, url=url)


app.command('c', help='alias: commit')(commit)
app.command('l', help='alias: list')(list)