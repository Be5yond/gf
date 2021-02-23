import typer
from typing import List
from .db import GfDB
from .utils import repo
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.formatted_text import FormattedText



def sync():
    "同步所有的commit到db"
    commits = repo.iter_commits("master")
    with GfDB() as db:
        for commit in commits:
            db.setdefault(commit)


class Cell:
    def __init__(self, value:str, width:int, color:str='white'):
        self.v = str(value)
        self.w = width
        self.c = color

    def __str__(self):
        return f'<b><style fg="ansi{self.c}">{self.v.ljust(self.w)}</style></b>'


class Row:
    def __init__(self, cells:List[Cell]):
        self.cells = cells

    def __str__(self):
        return '|'+'|'.join([str(cell) for cell in self.cells])+'|'


def rank():
    with GfDB() as db:
        rows = db.rank()
        sizes = [5, 16, 8, 9, 10, 20, 20]
        columns = ['Rank', 'Author', 'Commits', 'Addtions', 'Deletions', 'First Commit', 'Last Commit']
        header = Row(cells=[Cell(col, wid, 'yellow') for col,wid in zip(columns, sizes)])

        print_formatted_text(f'{"-":-^96}')
        print_formatted_text(HTML(str(header)))
        print_formatted_text(f'{"-":-^96}')
        for idx, r in enumerate(rows):
            cells = [
                Cell(idx + 1, sizes[0]),
                Cell(r[0][:16], sizes[1]),
                Cell(r[1], sizes[2]),
                Cell(f'+{r[2]}', sizes[3], 'green'),
                Cell(f'-{r[3]}', sizes[4], 'red'),
                Cell(r[4], sizes[5]),
                Cell(r[5], sizes[6])
            ]
            print_formatted_text(HTML(str(Row(cells))))


def trending():
    with GfDB() as db:
        data = db.trending()
        print_formatted_text(HTML(f'{"Date":<10}| {"Lines":<8}| Trending'))
        print_formatted_text(f'{"-":-^96}')
        for date, ins, de in data:
            plus = min(ins//50+1, 50)
            minus = min(de//50+1, 50)
            print_formatted_text(HTML(f'{date:<10}| {ins+de:<8}| <b><style fg="ansigreen">{"+"*plus}</style></b><b><style fg="ansired">{"-"*minus}</style></b>'))
