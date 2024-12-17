LENGTH_TEXT = 30
MAX_EMAIL_FIELD = 254
MAX_NAME_FIELD = 150
RESOLVED_CHARS = (
    'Допустимы только латинские буквы, '
    'цифры и символы @/./+/-/_. '
)
FORBIDDEN_NAME = 'Имя пользователя \'me\' использовать нельзя!'
HELP_TEXT_NAME = RESOLVED_CHARS + FORBIDDEN_NAME
UNIQUE_FIELDS = (
    'Пользователь с таким email уже существует.',
    'Пользователь с таким username уже существует.'
)
