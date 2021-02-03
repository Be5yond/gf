from enum import Enum


class Commit(Enum):
    FEATURE = '⚙️' 
    BUGFIX  = '🐛'
    REFACTOR = '♻️'
    CHORE = '🧰'
    DOCUMENT = '📝'
    STYLE = '🎨'
    TEST = '🩺'


class Change(Enum):
    A = '➕' # new file
    M = '🛠️' # modified
    D = '➖' # deleted
    R = '📇'   # renamed

