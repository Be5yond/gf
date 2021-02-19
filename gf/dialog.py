from __future__ import unicode_literals
import pathlib
from typing import List, Sequence, Tuple, TypeVar
from prompt_toolkit.application import Application
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent as E
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl,BufferControl
from prompt_toolkit.layout.containers import Window, HSplit, VSplit
from prompt_toolkit.layout.margins import ConditionalMargin, ScrollbarMargin
from prompt_toolkit.widgets import Label, Frame, CheckboxList, VerticalLine, HorizontalLine, Box
from prompt_toolkit.widgets.base import _DialogList

from prompt_toolkit.formatted_text import AnyFormattedText, HTML, to_formatted_text
from prompt_toolkit.formatted_text.utils import fragment_list_to_text
from prompt_toolkit.filters import Condition
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.key_binding.bindings.focus import focus_next
from . import emoji
from .utils import repo


_T = TypeVar("_T")
page = 0


def ansired(key: str) -> str:
    return f'<b><style bg="ansired">[{key}]</style></b>'

class SingleSelectList(_DialogList):
    """
    Common code for `RadioList` and `CheckboxList`.
    """

    open_character: str = "("
    close_character: str = ")"
    container_style: str = "class:radio-list"
    default_style: str = "class:radio"
    selected_style: str = "class:radio-selected"
    checked_style: str = "class:radio-checked"
    multiple_selection: bool = False
    show_scrollbar: bool = True

    def __init__(self, values: Sequence[Tuple[_T, AnyFormattedText]]) -> None:
        assert len(values) > 0

        self.values = values
        # current_values will be used in multiple_selection,
        # current_value will be used otherwise.
        self.current_values: List[_T] = []
        self.current_value: _T = values[0][0]
        self._selected_index = 0

        # Key bindings.
        kb = KeyBindings()

        @kb.add("up")
        def _up(event: E) -> None:
            self._selected_index = max(0, self._selected_index - 1)
            self.current_value = self.values[self._selected_index][0]

        @kb.add("down")
        def _down(event: E) -> None:
            self._selected_index = min(len(self.values) - 1, self._selected_index + 1)
            self.current_value = self.values[self._selected_index][0]

        @kb.add("pageup")
        def _pageup(event: E) -> None:
            w = event.app.layout.current_window
            if w.render_info:
                self._selected_index = max(
                    0, self._selected_index - len(w.render_info.displayed_lines)
                )
            self.current_value = self.values[self._selected_index][0]

        @kb.add("pagedown")
        def _pagedown(event: E) -> None:
            w = event.app.layout.current_window
            if w.render_info:
                self._selected_index = min(
                    len(self.values) - 1,
                    self._selected_index + len(w.render_info.displayed_lines),
                )
            self.current_value = self.values[self._selected_index][0]

        @kb.add("enter")
        @kb.add(" ")
        def _enter(event: E) -> None:
            # self._handle_enter()
            event.app.exit(result=self.current_value)

        @kb.add(Keys.Any)
        def _find(event: E) -> None:
            # We first check values after the selected value, then all values.
            values = list(self.values)
            for value in values[self._selected_index + 1 :] + values:
                text = fragment_list_to_text(to_formatted_text(value[1])).lower()

                if text.startswith(event.data.lower()):
                    self._selected_index = self.values.index(value)
                    return

        # Control and window.
        self.control = FormattedTextControl(
            self._get_text_fragments, key_bindings=kb, focusable=True
        )

        self.window = Window(
            content=self.control,
            style=self.container_style,
            right_margins=[
                ConditionalMargin(
                    margin=ScrollbarMargin(display_arrows=True),
                    filter=Condition(lambda: self.show_scrollbar),
                ),
            ],
            dont_extend_height=True,
        )


def radiolist_dialog(title='', values=None, style=None, async_=False):
    # Add exit key binding.
    kb = KeyBindings()
    @kb.add('c-c')
    @kb.add("escape")
    def exit_(event):
        """
        Pressing Ctrl-c will exit the user interface.
        """
        event.app.exit()

    radio_list = SingleSelectList(values)
    application = Application(
        layout=Layout(HSplit([Label(title), radio_list])),
        key_bindings=kb,
        mouse_support=True,
        style=style,
        full_screen=False,
        )
    if async_:
        return application.run_async()
    else:
        return application.run()


class CommitMsgPrompt:
    @staticmethod
    def commit_type():
        result = radiolist_dialog(
            title=HTML(f'Choose a commit type: (Press {ansired("Enter")} to confirm, {ansired("Ctrl+C")} to cancel.)'),
            values=[
                (emoji.Commit.FEATURE.value, HTML(f'<style bg="orange" fg="black">{emoji.Commit.FEATURE.value}[feature]:  新功能</style>')),
                (emoji.Commit.BUGFIX.value, HTML(f'<style bg="green" fg="black">{emoji.Commit.BUGFIX.value}[bugfix]:   修复问题</style>')),
                (emoji.Commit.REFACTOR.value, HTML(f'<style bg="red" fg="black">{emoji.Commit.REFACTOR.value}[refactor]: 重构</style>')),
                (emoji.Commit.CHORE.value, HTML(f'<style bg="blue" fg="black">{emoji.Commit.CHORE.value}[chore]:    工具依赖变动</style>')),
                (emoji.Commit.DOCUMENT.value, HTML(f'<style bg="gray" fg="white">{emoji.Commit.DOCUMENT.value}[document]: 文档或注释</style>')),
                (emoji.Commit.STYLE.value, HTML(f'<style bg="gray" fg="white">{emoji.Commit.STYLE.value}[style]:    格式</style>')),
                (emoji.Commit.TEST.value, HTML(f'<style bg="gray" fg="white">{emoji.Commit.TEST.value}[test]:     添加测试</style>'))
            ])
        return result

    @staticmethod
    def title():
        def bottom_toolbar():
            return HTML(f'commit purpose, should less than {ansired(50)} letters. Press {ansired("Ctrl+C")} to abort.')
        return prompt('header: ', rprompt='gf', bottom_toolbar=bottom_toolbar())

    @staticmethod
    def body():
        def bottom_toolbar():
            return HTML(f'Press {ansired("Tab")} to add a new line. {ansired("Enter")} to accept input. Press {ansired("Ctrl+C")} to abort')

        kb = KeyBindings()
        @kb.add("tab")
        def _(event):
            b = event.app.current_buffer
            idx = int(b.document.current_line[0])
            b.insert_text(f'\n{idx+1}.')

        @kb.add("enter")
        def _(event):
            event.app.exit(result=event.app.current_buffer.text)

        return prompt('body: ', rprompt='gf', bottom_toolbar=bottom_toolbar(), multiline=True, key_bindings=kb, default='1.')

    @staticmethod
    def footer():
        def bottom_toolbar():
            return HTML(f'BREAKING CHANGE or Close Issue. Press {ansired("Enter")} to accept input {ansired("Ctrl+C")} to abort')
        return prompt('footer: ', rprompt='gf', bottom_toolbar=bottom_toolbar(), default='#')

    @classmethod
    def message(cls, body: bool, footer: bool):
        type = cls.commit_type()
        if not type:
            return None
        title = cls.title()
        header = f'{type} {title}'
        if body:
            body = cls.body()
        if footer:
            footer = cls.footer()
        return '\n\n'.join(filter(bool, [header, body, footer]))


def stats_dialog():
    branch = repo.head.reference.name
    # 获取暂存区的diff
    staged = [diff for diff in repo.head.commit.diff()]
    # 获取workspace的diff
    modified = [diff for diff in repo.index.diff(None)]
    untracked = repo.untracked_files

    empty=[(None, HTML(f'<style bg="gray" fg="white">No files</style>'))]
    values_stage = [(v, HTML(f'{emoji.Change.__getattr__(v.change_type).value} <style fg="green">{v.a_path}</style>')) for v in staged] or empty
    values_modified = [(v, HTML(f'{emoji.Change.__getattr__(v.change_type).value} <style fg="red">{v.a_path}</style>')) for v in modified] or empty
    values_untracked = [(v, HTML(f'<style fg="orange">{v}</style>')) for v in untracked] or empty

    frame_stage = Frame(
                body = CheckboxList(values=values_stage),
                title = HTML(f'Changes to be committed: (After selecting file, press {ansired("Ctrl+R")} to unstage file)')
            )
    frame_modified = Frame(
                body = CheckboxList(values=values_modified),
                title = HTML(f'Changes not staged for commit: (After selecting file, press {ansired("Ctrl+R")} to discard change, {ansired("Ctrl+A")} to stage file)')
            )
    frame_untracked = Frame(
                body = CheckboxList(values=values_untracked),
                title = HTML(f'Untracked files: (After selecting file, press {ansired("Ctrl+A")} to stage file, {ansired("Ctrl+I")} to ignore file.')
            )
    root_container = HSplit(
        [
            Label(HTML(f'on branch <style fg="orange">{branch}</style>\n (Press {ansired("N")} to switch window. {ansired("Up][Down")} to move cursor. {ansired("Enter")} to select. {ansired("Ctrl+C")} to quit.)')),
            # Window(BufferControl(buffer=buffer)),
            frame_stage,
            frame_modified,
            frame_untracked
        ]
    )

    kb = KeyBindings()
    kb.add("n")(focus_next)
    @kb.add("c-c", eager=True)
    def _(event):
        event.app.exit()

    @kb.add("c-a")
    def _(event):
        "add file to stage"
        for diff in frame_modified.body.current_values:
            if diff.change_type == 'D':
                repo.index.remove(diff.a_path)
            else:
                repo.index.add(diff.a_path)
        for diff in frame_untracked.body.current_values:
            repo.index.add(diff.a_path)
        event.app.exit()

    @kb.add("c-r")
    def _(event):
        for diff in frame_stage.body.current_values:
            repo.git.restore(diff.a_path, staged=True)
        for diff in frame_modified.body.current_values:
            repo.index.checkout(diff.a_path, force=True)
        event.app.exit()

    @kb.add("c-i")
    def _(event):
        exclude_path = pathlib.Path('.git')/'info'/'exclude'
        with open (exclude_path, encoding='utf-8', mode='a') as file:
            file.writelines([f'{path}\n' for path in frame_untracked.body.current_values])
        return event.app.exit(frame_untracked.body.current_values)

    application = Application(
        layout=Layout(root_container, focused_element=frame_modified),
        key_bindings=kb,
        # Let's add mouse support!
        mouse_support=True,
        # It switches the terminal to an alternate screen.
        full_screen=False
    )
    return application.run()


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

    def row(cmt):
        message = cmt.message.split('\n')[0]
        
        # 添加分支和tag信息
        for ref in repo.remote().refs:
            if cmt == ref.commit:
                message = f'<b><style bg="ansired" fg="ansiwhite">[️{ref.name}]</style></b>'+message
        for tag in repo.tags:
            if cmt == tag.commit:
                message = f'<b><style bg="ansiyellow" fg="ansiblack">[️Tag:{tag.name}]</style></b>'+message
        for head in repo.heads:
            if cmt == head.commit:
                message = f'<b><style bg="ansigreen" fg="ansiblack">[️{head.name}]</style></b>'+message
        if cmt == repo.head.commit:
            message = '<b><style bg="ansiblue" fg="ansiblack">[HEAD]</style></b>'+message

        return VSplit([
            Window(content=FormattedTextControl(f'{cmt.count()}'), width=5),
            Window(width=1, char="|"),
            Window(content=FormattedTextControl(cmt.hexsha[:7]), width=9),
            Window(width=1, char="|"),
            Window(content=FormattedTextControl(cmt.committer.name), width=20),
            Window(width=1, char="|"),
            Window(content=FormattedTextControl(cmt.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')), width=21),
            Window(width=1, char="|"),
            Label(HTML(f'<b><style fg="ansigreen">+{cmt.stats.total["insertions"]}</style></b>'), width=5),
            Label(HTML(f'<b><style fg="ansired">-{cmt.stats.total["deletions"]}</style></b>'), width=5),
            Window(width=1, char="|"),
            Label(HTML(message))
        ])

    body = HSplit([row(cmt) for cmt in commits])

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
        body.children = [row(cmt) for cmt in commits]
        event.app.layout.reset()

    @kb.add('b')
    @kb.add('up')
    def _(event):
        global page
        page = max(page-max_count, 0)
        commits = [c for c in repo.iter_commits(branch, skip=page, max_count=max_count)]
        body.children = [row(cmt) for cmt in commits]
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