DEFAULT_MIN_VALUE = 1

PAGE_SIZE = 6

CODE_LEN = 10

TEXT_FONT_SIZE = 14

TITLE_FONT_SIZE = 16

ADMIN_PER_PAGE = 20

LENGTH_TEXT = 32

MEASUREMENT_UNIT_LEN = 64

INGREDIENT_NAME_LEN = 128

MAX_NAME_FIELD = 150

MAX_URL_FIELD = 250

MAX_EMAIL_FIELD = 254

RECIPE_NAME_LEN = 256

DEFAULT_MAX_VALUE = 1440

DEFAULT_MAX_AMOUNT = 32000

TITLE_FONT_SIZE = 16
TEXT_FONT_SIZE = 14
PAGE_WIDTH_MARGIN = 100
LINE_SPACING = 20
PAGE_TOP = 800
PAGE_BOTTOM_MARGIN = 50

RESOLVED_CHARS = (
    'Допустимы только латинские буквы, '
    'цифры и символы @/./+/-/_. '
)

FORBIDDEN_NAME = 'Имя пользователя \'me\' использовать нельзя!'

HELP_TEXT_NAME = RESOLVED_CHARS + FORBIDDEN_NAME

UNIQUE_FIELDS = (
    'Пользователь с таким email уже существует!',
    'Пользователь с таким username уже существует!',
    'Ингредиенты не должны повторяться!',
    'Теги не должны повторяться!'
)

MIN_TIME_MSG = 'Любой рецепт требует как минимум 1-й минуты!'

MAX_TIME_MSG = (
    'Вы наверное ошиблись? '
    'Время пригтовления блюда должно быть менее суток!'
)

MESSAGE_AMOUNT = (
    'Количество ингредиента в рецепте должно быть равно хотя бы 1, '
    'и не превышать значение 32000 единиц'
)

EMPTY_FIELDS = (
    'Поле `tags` не может быть пустым!',
    'Поле `ingredient` не может быть пустым!',
    'Поле `image` не может быть пустым!'
)

FORBIDDEN_FILE = 'Загруженный файл не является корректным файлом изображения!'

RESOLVED_TYPE = ('.png', '.jpg', '.jpeg')
