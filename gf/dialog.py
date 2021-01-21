from __future__ import unicode_literals
from typing import List, Sequence, Tuple, TypeVar
from prompt_toolkit.application import Application
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent as E
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window, HSplit
from prompt_toolkit.layout.margins import ConditionalMargin, ScrollbarMargin
from prompt_toolkit.widgets import Label, Frame, CheckboxList
from prompt_toolkit.widgets.base import _DialogList

from prompt_toolkit.formatted_text import AnyFormattedText, HTML, to_formatted_text
from prompt_toolkit.formatted_text.utils import fragment_list_to_text
from prompt_toolkit.filters import Condition
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.key_binding.bindings.focus import focus_next



_T = TypeVar("_T")

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
    bindings = KeyBindings()
    @bindings.add('c-d')
    @bindings.add("escape")
    def exit_(event):
        """
        Pressing Ctrl-d will exit the user interface.
        """
        event.app.exit()    

    radio_list = SingleSelectList(values)        
    application = Application(
        layout=Layout(HSplit([Label(title), radio_list])),
        key_bindings=bindings,
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
            title=HTML(f'Choose a commit type: (Press {ansired("Enter")} to confirm, {ansired("Esc")} to cancel.)'),
            values=[
                ('⚙️', HTML('<style bg="orange" fg="black">⚙️[feature], 新功能</style>')),
                ('🐛', HTML('<style bg="green" fg="black">🐛[bugfix], 修复问题</style>')),
                ('♻️', HTML('<style bg="red" fg="black">♻️[refactor], 重构</style>')),
                ('🛠️', HTML('<style bg="blue" fg="black">🛠️[chore], 工具依赖变动</style>')),
                ('📝', HTML('<style bg="gray" fg="white">📝[document], 文档或注释</style>')),
                ('️🎵', HTML('<style bg="gray" fg="white">🎵[style], 格式</style>')),
                ('️🩺', HTML('<style bg="gray" fg="white">🩺[test], 添加测试</style>'))
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
            event.app.exit(result=event.app.current_buffer)

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


def stats_dialog(title: str, stage: List[tuple], modified: List[tuple], untracked: List[tuple]):
    frame_stage = Frame(
                body = CheckboxList(values=stage) if stage else Label(text=''),
                title = HTML(f'Changes to be committed: (After selecting file, press {ansired("Ctrl+R")} to unstage file)')
            )
    frame_modified = Frame(
                body = CheckboxList(values=modified) if stage else Label(text=''),
                title = HTML(f'Changes not staged for commit: (After selecting file, press {ansired("Ctrl+R")} to discard change, {ansired("Ctrl+A")} to stage file)')
            )
    frame_untracked = Frame(
                body = CheckboxList(values=untracked) if stage else Label(text=''),
                title = HTML(f'Untracked files: (After selecting file, press {ansired("Ctrl+A")} to stage file, {ansired("Ctrl+I")} to ignore file.') 
            )
    root_container = HSplit(
        [
            # Horizontal separator.
            Label(HTML(f'(Press {ansired("N")} to switch window. {ansired("Up][Down")} to move cursor. {ansired("Enter")} to select. {ansired("Ctrl+C")} to quit.)')),
            # Window(height=1, char="-", style="class:line"),
            # HSplit([frame_stage, frame_modified, frame_untracked])
            frame_stage, frame_modified, frame_untracked
        ]
    )

    from git import Repo
    repo = Repo()

    kb = KeyBindings()
    kb.add("n")(focus_next)
    # frames = deque([frame_stage, frame_modified, frame_untracked])

    # @kb.add("n")
    # def _(event):
    #     event.app.layout.focus(frames[-1])
    #     frames.rotate(1)

    @kb.add("c-c", eager=True)
    def _(event):
        event.app.exit()

    @kb.add("c-a")
    def _(event):
        repo.index.add()
        event.app.exit()

    @kb.add("c-r")
    def _(event):
        pass

    @kb.add("c-i")
    def _(event):
        pass
    


    application = Application(
        layout=Layout(root_container, focused_element=frame_modified),
        key_bindings=kb,
        # Let's add mouse support!
        mouse_support=True,
        # Using an alternate screen buffer means as much as: "run full screen".
        # It switches the terminal to an alternate screen.
        full_screen=False
    )
    application.run()
