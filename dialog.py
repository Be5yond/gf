from __future__ import unicode_literals
from prompt_toolkit.application import Application
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent as E
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window, HSplit
from prompt_toolkit.layout.margins import ConditionalMargin, ScrollbarMargin
from prompt_toolkit.widgets import Label
from prompt_toolkit.widgets.base import _DialogList

from typing import List, Sequence, Tuple, TypeVar
from prompt_toolkit.formatted_text import AnyFormattedText, HTML, to_formatted_text
from prompt_toolkit.formatted_text.utils import fragment_list_to_text
from prompt_toolkit.filters import Condition
from prompt_toolkit.shortcuts import prompt


_T = TypeVar("_T")


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
        layout=Layout(HSplit([ Label(title), radio_list])),
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
    def title():
        def bottom_toolbar():
            return HTML('commit purpose, should less than <b><style bg="ansired">50</style></b> letters. Press <b><style bg="ansired">[Ctrl + C]</style></b> to abort.')
        return prompt('header: ', rprompt='igit', bottom_toolbar=bottom_toolbar())

    @staticmethod
    def commit_type():
        result = radiolist_dialog(
            title='Choose a commit type: (Press [Enter] to confirm, [Esc] to cancel.)',
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
    def body():
        def bottom_toolbar():
            return HTML('Press <b><style bg="ansired">[Esc]</style></b> followed by <b><style bg="ansired">[Enter]</style></b> to accept input. Press <b><style bg="ansired">[Ctrl + C]</style></b> to abort')
        bindings = KeyBindings()
        @bindings.add("enter")
        def _(event):
            b = event.app.current_buffer
            idx = int(b.document.current_line[0])
            b.insert_text(f'\n{idx+1}.')
        return prompt('body: ', rprompt='igit', bottom_toolbar=bottom_toolbar(), multiline=True, key_bindings=bindings, default='1.') 

    @staticmethod
    def footer():
        def bottom_toolbar():
            return HTML('BREAKING CHANGE or Close Issue. Press <b><style bg="ansired">[Ctrl + C]</style></b> to abort')
        return prompt('footer: ', rprompt='igit', bottom_toolbar=bottom_toolbar(), default='#')

    @classmethod
    def message(cls, body: bool, footer: bool):
        type = cls.commit_type()
        title = cls.title()
        header = f'{type} {title}'
        if body:
            body = cls.body()
        if footer:
            footer = cls.footer()
        return '\n\n'.join(filter(bool, [header, body, footer]))

