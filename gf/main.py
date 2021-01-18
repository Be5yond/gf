import time
import re
from git import Repo
from git.exc import GitCommandError
from prompt_toolkit.application import current
import typer
from prompt_toolkit.formatted_text import HTML
from .dialog import CommitMsgPrompt, radiolist_dialog
from . import feature, hotfix
from .utils import no_traceback as nt


repo = Repo()
app = typer.Typer()
app.add_typer(feature.app, name='feature')
app.add_typer(hotfix.app, name='hotfix')


@app.command()
def init():
    """
    create branches: 
    """
    repo.git.branch('develop')
    repo.git.branch('release')
    repo.git.branch('test')


@app.command()
def release():
    """ After passing the test phase, merge test branch to main branch.
    """
    nt(repo.git.checkout)('main')
    nt(repo.git.merge)('test')


@app.command(help=f"""
    {"Standardize the format of commit":<74}
    {"-":->74}   
    {"<type>(emoji): <subject> (brief description of commit purpose)":<74}
    {"<BLANK LINE>":<74}
    {"<body> (commit Multi-line detailed description)":<74}
    {"<BLANK LINE>":<74}
    {"<footer> (breaking change or close issue)":<74}
    {"-":->74}""")
def commit(body: bool = typer.Option(False, '--body', '-b', help='include body message'), 
        footer: bool = typer.Option(False, '--foot', '-f', help='include footer message')):
    message = CommitMsgPrompt.message(body, footer)
    typer.echo(message)
    repo.index.commit(message)


@app.command()
def branch():
    """ list branchs in this repository"""
    current_branch = repo.head.reference
    for head in repo.heads:
        if head == current_branch:
            typer.secho(head.name, fg=typer.colors.GREEN)
        else:
            typer.echo(head.name)



@app.command()
def switch():
    """ switch branch
    """
    current_branch = repo.head.reference
    values = [(head, head.name) for head in repo.heads if not head == current_branch]
    values.insert(0, (current_branch, HTML(f'<style fg="green">{current_branch.name}</style>')))
    result = radiolist_dialog(
            title='Checkout to branch (Press [Enter] to confirm, [Esc] to cancel):',
            values=values)
    if not result:
        raise typer.Abort()
    else:
        nt(repo.git.checkout)(result.name)


@app.command()
def tag(major: bool=typer.Option(False, '--major', '-M', help='increse major version number. e.g: tag -M (v0.1.2 -> v1.0.0)'),
        minor: bool=typer.Option(False, '--minor', '-m', help='increse minor version number. e.g: tag -m (v0.1.2 -> v0.2.0)'),
        patch: bool=typer.Option(False, '--minor', '-p', help='increse patch version number. e.g: tag -p (v0.1.2 -> v0.1.3)'),):
    """Use -M/-m/-p to create a tag in 'v{major}.{minor}.{patch}_{date}' format. The version number is self-increasing.
       no-option: list tags.
    """
    try:
        name = repo.tags[-1].name
    except IndexError:
        mj, mi, p = 0, 0, 0
    else:
        mj, mi, p, date = re.split('[._]', name[1:])

    if major:
        mj, mi, p = int(mj)+1, 0, 0
    elif minor:
        mi, p = int(mi)+1, 0
    elif patch:
        p = int(p)+1
    else:
        for tag in reversed(repo.tags):
            typer.echo(tag.name)
        raise typer.Exit(0)
    tag = f'v{mj}.{mi}.{p}_{time.strftime("%Y%m%d")}'
    typer.echo(tag)
    repo.git.tag(tag)


@app.callback()
def main(verbose: bool = False):
    """
    Manage users in the awesome CLI app.
    """
    if verbose:
        typer.echo("Will write verbose output")


def main():
    app()

if __name__ == "__main__":
    app()

