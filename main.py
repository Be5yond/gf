from typing import Optional
from enum import Enum
from git import Repo
import typer
from dialog import CommitMsgPrompt, radiolist_dialog
from prompt_toolkit.formatted_text import HTML
import feature

repo = Repo()
app = typer.Typer()
app.add_typer(feature.app, name='feature')


@app.command()
def init():
    """
    create branches: 
    """
    repo.git.branch('develop')
    repo.git.branch('release')
    repo.git.branch('test')


@app.command()
def hotfix():
    typer.echo('hotfix')


@app.command()
def release():
    typer.echo('release')


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
def checkout():
    current_branch = repo.head.reference
    values = [(head, head.name) for head in repo.heads if not head == current_branch]
    values.insert(0, (current_branch, HTML(f'<style fg="green">{current_branch.name}</style>')))
    result = radiolist_dialog(
            title='Checkout to branch (Press [Enter] to confirm, [Esc] to cancel):',
            values=values)
    if not result:
        raise typer.Abort()
    else:
        repo.git.checkout(result.name)


@app.command()
def tag(ver: str):
    """major.minor.patch"""
    typer.echo(f'delete user {ver}')


@app.callback()
def main(verbose: bool = False):
    """
    Manage users in the awesome CLI app.
    """
    if verbose:
        typer.echo("Will write verbose output")


if __name__ == "__main__":
    app()

