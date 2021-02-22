import typer
from .db import GfDB
from .utils import repo


def sync():
    "同步所有的commit到db"
    cmts = repo.iter_commits("main")
    with GfDB() as db:
        try:
            while cmts:
                db.setdefault(next(cmts))
        except StopIteration:
            pass


def rank():
    with GfDB() as db:
        rows = db.rank()
        typer.echo(f'{"-":-^90}')
        typer.echo(f'|Rank |Author    |Commits |Addtions |Deletions |First Commit        |Last Commit         |')
        typer.echo(f'{"-":-^90}')
        for idx, r in enumerate(rows):
            typer.echo(f'|{idx+1:<5}|{r[0]:<10}|{r[1]:<8}|+{r[2]:<8}|-{r[3]:<9}|{r[4]:<20}|{r[5]:<20}|')
        