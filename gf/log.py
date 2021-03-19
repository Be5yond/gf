from configparser import NoSectionError
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window, HSplit, VSplit
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.widgets import Label
import xml
from .utils import repo
from .dialog import ansired
from .db import GfDB


page = 0


def row(cmt, num, ins, de):
    message = cmt.message.split('\n')[0]
    
    # 添加分支和tag信息
    try:
        for ref in repo.remote().refs:
            if cmt == ref.commit:
                message = f'<b><style bg="ansired" fg="ansiwhite">[️{ref.name}]</style></b>'+message
    except NoSectionError:
        # 处理未关联remote分支的场景
        pass
    for tag in repo.tags:
        if cmt == tag.commit:
            message = f'<b><style bg="ansiyellow" fg="ansiblack">[️Tag:{tag.name}]</style></b>'+message
    for head in repo.heads:
        if cmt == head.commit:
            message = f'<b><style bg="ansigreen" fg="ansiblack">[️{head.name}]</style></b>'+message
    if cmt == repo.head.commit:
        message = '<b><style bg="ansiblue" fg="ansiblack">[HEAD]</style></b>'+message

    try:
        message = HTML(message)
    except xml.parsers.expat.ExpatError:
        # messge中包含特殊字符时
        pass
    
    return VSplit([
        Window(content=FormattedTextControl(f'{num}'), width=5),
        Window(width=1, char="|"),
        Window(content=FormattedTextControl(cmt.hexsha[:7]), width=9),
        Window(width=1, char="|"),
        Window(content=FormattedTextControl(cmt.committer.name), width=20),
        Window(width=1, char="|"),
        Window(content=FormattedTextControl(cmt.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')), width=21),
        Window(width=1, char="|"),
        Label(HTML(f'<b><style fg="ansigreen">+{ins}</style></b>'), width=5),
        Label(HTML(f'<b><style fg="ansired">-{de}</style></b>'), width=5),
        Window(width=1, char="|"),
        Label(message)
    ])


def rows(commits):
    children = []
    with GfDB() as db:
        for cmt in commits:
            num, ins, de = db.setdefault(cmt)
            children.append(row(cmt, num, ins, de))
    return children


def log_dialog(max_count=10):
    branch = repo.head.reference.name
    commits = [c for c in repo.iter_commits(branch, skip=0, max_count=max_count)]
    help = Label(HTML(f'(Press {ansired("n][Down")} or {ansired("b][Up")} to turn pages. {ansired("Ctrl+C][Esc")} to quit)'))
    header = VSplit([
        Label(HTML('Num'), width=5),
        Window(width=1, char="|"),
        Label(HTML('Commit'), width=9),
        Window(width=1, char="|"),
        Label(HTML('Author'), width=20),
        Window(width=1, char="|"),
        Label('Date', width=21),
        Window(width=1, char="|"),
        Label('Stats', width=10),
        Window(width=1, char="|"),
        Label('Description')
    ])
    body = HSplit(rows(commits))
    root_container = HSplit([
        help,
        Window(height=1, char="-"), 
        header,
        Window(height=1, char="-"), 
        body
    ])

    kb = KeyBindings()
    @kb.add("c-c", eager=True)
    @kb.add("escape")
    def _(event):
        event.app.exit()

    @kb.add('n')
    @kb.add('down')
    def _(event):
        global page
        page += max_count
        commits = [c for c in repo.iter_commits(branch, skip=page, max_count=max_count)]
        if not commits:
            event.app.exit()
        body.children = rows(commits)
        event.app.layout.reset()

    @kb.add('b')
    @kb.add('up')
    def _(event):
        global page
        page = max(page-max_count, 0)
        commits = [c for c in repo.iter_commits(branch, skip=page, max_count=max_count)]
        body.children = rows(commits)
        event.app.layout.reset()

    application = Application(
        layout=Layout(root_container),
        key_bindings=kb,
        # Let's add mouse support!
        mouse_support=False,
        # It switches the terminal to an alternate screen.
        full_screen=False
    )
    return application.run()