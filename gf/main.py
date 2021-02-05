import time
import re
import typer
from prompt_toolkit.formatted_text import HTML
from .dialog import CommitMsgPrompt, radiolist_dialog, stats_dialog, ansired, log_dialog
from . import feature, hotfix
from .utils import no_traceback as nt
from .utils import get_create_time, repo


app = typer.Typer()
app.add_typer(feature.app, name='feature')
app.add_typer(hotfix.app, name='hotfix')


@app.command()
def init():
    """
    create base branches: develop | test | release
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
    if not message:
        raise typer.Abort()
    typer.echo(message)
    repo.index.commit(message)


@app.command()
def branch():
    """ list branchs in this repository"""
    current_branch = repo.head.reference
    for head in repo.heads:
        date = get_create_time(head.name)
        if head == current_branch:
            color = typer.colors.GREEN
            prefix = '*'
        else:
            color = typer.colors.WHITE
            prefix = ' '
        typer.secho(f'{prefix} {head.name:<30}{date}', fg=color)


@app.command()
def switch():
    """ switch branch
    """
    current_branch = repo.head.reference
    values = [(head, head.name) for head in repo.heads if not head == current_branch]
    values.insert(0, (current_branch, HTML(f'<style fg="green">{current_branch.name}</style>')))
    result = radiolist_dialog(
            title=HTML(f'Checkout to branch (Press {ansired("Enter")} to confirm, {ansired("Esc")} to cancel):'),
            values=values)
    if not result:
        raise typer.Abort()
    else:
        nt(repo.git.switch)(result.name)


@app.command()
def tag(major: bool=typer.Option(False, '--major', '-M', help='increse major version number. e.g: tag -M (v0.1.2 -> v1.0.0)'),
        minor: bool=typer.Option(False, '--minor', '-m', help='increse minor version number. e.g: tag -m (v0.1.2 -> v0.2.0)'),
        patch: bool=typer.Option(False, '--minor', '-p', help='increse patch version number. e.g: tag -p (v0.1.2 -> v0.1.3)'),
        delete: bool=typer.Option(False, '--delete', '-d', help='chose tag to delete'),):
    """Use -M/-m/-p to create a tag in 'v{major}.{minor}.{patch}_{date}' format. The version number is self-increasing.
    no-option: list tags.
    """
    # get latest tag name, default v0.0.0
    try:
        name = repo.tags[-1].name
    except IndexError:
        mj, mi, p = 0, 0, 0
    else:
        mj, mi, p, date = re.split('[._]', name[1:])
    
    # increse tag version number by cmd option
    if major:
        mj, mi, p = int(mj)+1, 0, 0
    elif minor:
        mi, p = int(mi)+1, 0
    elif patch:
        p = int(p)+1
    elif delete:
        try:
            values = [(tag, tag.name) for tag in reversed(repo.tags)]
            result = radiolist_dialog(
                    title=HTML(f'Choose a tag to delete (Press {ansired("Enter")} to confirm, {ansired("Esc")} to cancel):'),
                    values=values)
        except AssertionError:
            pass
        else: 
            msg = repo.git.tag(result, d=True)
            typer.echo(msg)
        finally:
            raise typer.Exit(0)
    else:
        for tag in reversed(repo.tags):
            typer.echo(tag.name)
        raise typer.Exit(0)
    tag = f'v{mj}.{mi}.{p}_{time.strftime("%Y%m%d")}'
    typer.echo(tag)
    repo.git.tag(tag)


@app.command()
def status():
    'status info'
    ret = stats_dialog()
    typer.echo(ret)


@app.command()
def undo():
    'undo last commit'
    msg = repo.git.reset('HEAD^')
    typer.echo(msg)
    typer.echo(f'reset head to {repo.head.commit.hexsha[:8]}\t\t{repo.head.commit.message[:8]}')


@app.command()
def log(skip: int=typer.Argument(0, help='Skip number commits before starting to show the commit output.'), 
        size: int=typer.Argument(10, help='Limit the number of commits to output.')):
    log_dialog(skip, size)


app.command('b', help='alias: branch')(branch)
app.command('c', help='alias: commit')(commit)
app.command('st', help='alias: status')(status)
app.command('sw', help='alias: switch')(switch)
app.command('t', help='alias: tag')(tag)
app.command('i', help='alias: init')(init)
app.command('r', help='alias: release')(release)
app.command('u', help='alias: undo')(undo)
app.command('l', help='alias: log')(log)
app.add_typer(feature.app, name='f', help='alias: feature')
app.add_typer(hotfix.app, name='h', help='alias: hotfix')



def main():
    app()

if __name__ == "__main__":
    app()

