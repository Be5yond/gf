import time
import re
import typer
from prompt_toolkit.formatted_text import HTML
from .dialog import CommitMsgPrompt, radiolist_dialog, stats_dialog, ansired
from .log import log_dialog
from . import feature, hotfix 
from .utils import no_traceback as nt
from .utils import get_create_date, repo
from .db import GfDB
from . import inspector 


app = typer.Typer()
app.add_typer(feature.app, name='feature')
app.add_typer(hotfix.app, name='hotfix')


@app.command()
def init():
    """
    create base branches: develop | test | release
    """
    repo.git.branch('release')
    repo.git.branch('test')
    repo.git.branch('develop')
    with GfDB() as d:
        d.create_table()


@app.command()
def test():
    """ Merge develop -> test 
    """
    nt(repo.git.checkout)('test')
    nt(repo.git.merge)('develop')

@app.command()
def release():
    """ After passing the test phase, merge test -> release
    """
    nt(repo.git.checkout)('release')
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
    cmt = repo.index.commit(message)
    with GfDB() as d:
        d.setdefault(cmt)


@app.command()
def branch():
    """ list branchs info this repository. switch between local branch"""
    def row(head):
        date = get_create_date(head.name)
        try:
            remote = head.tracking_branch().name
            syn = len(list(repo.iter_commits(f'{remote}..{head}'))) - len(list(repo.iter_commits(f'{head}..{remote}')))
            syn = f'{syn:+}'
        except AttributeError:
            remote = ''
            syn = ''
        return f'{head.name:<20} {remote:<20} {syn:<5} {date}'
    current_branch = repo.head.reference
    values = [(head, row(head)) for head in repo.heads if not head == current_branch]
    values.insert(0, (current_branch, HTML(f'<style fg="ansigreen">{row(current_branch)}</style>')))
    result = radiolist_dialog(
            title=HTML(
            f'''Checkout to branch (Press {ansired("Enter")} to confirm, {ansired("Esc")} to cancel):
<b><style fg="ansiyellow">    {"Local":<20} {"Remote":<20} Sync  Date</style></b>
{"-":-<63}'''),
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
def log(size: int=typer.Argument(15, help='Limit the number of commits to output.')):
    log_dialog(size)


@app.command()
def inspect(sync: bool=typer.Option(False, '--sync', '-s', help='synchronize latest commits to statistics'),
            trending: bool=typer.Option(False, '--trending', '-t', help='show code modifycation trending of this repository'),
            ):
    "statistics of the submitter activity"
    if sync:
        inspector.sync()
    elif trending:
        inspector.trending()
    inspector.rank()
    


app.command('b', help='alias: branch')(branch)
app.command('c', help='alias: commit')(commit)
app.command('s', help='alias: status')(status)
app.command('t', help='alias: tag')(tag)
app.command('i', help='alias: init')(init)
app.command('r', help='alias: release')(release)
app.command('u', help='alias: undo')(undo)
app.command('l', help='alias: log')(log)
app.command('ins', help='alias: inspect')(inspect)
app.add_typer(feature.app, name='f', help='alias: feature')
app.add_typer(hotfix.app, name='h', help='alias: hotfix')


def main():
    app()

if __name__ == "__main__":
    app()

