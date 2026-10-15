# Work 1
# VFS Shell Emulator

Эмулятор командной оболочки UNIX-подобной ОС с виртуальной файловой
системой (VFS) в памяти. Написан на Python с графическим интерфейсом
на tkinter.

## Возможности

- REPL с графическим интерфейсом (tkinter)
- Виртуальная файловая система (VFS), загружаемая из директории на диске
- Все операции VFS — в памяти, диск после загрузки не трогается
- Раскрытие переменных окружения реальной ОС (`$HOME`, `${VAR}`)
- Конфигурация через CLI-параметры и INI-файл
- Приоритет CLI > INI > значение по умолчанию
- Стартовые скрипты с комментариями и эхом ввода
- Обработка ошибок на всех уровнях

## Поддерживаемые команды

| Команда | Описание | Флаги / формы |
|---|---|---|
| `ls` | список файлов и папок | `-a`, `-l`, `-h`, `-S`, `-R`, пути |
| `cd` | переход между директориями | `~`, `-`, `..`, `.`, `/`, кавычки |
| `tail` | последние N строк файла | `-n N` |
| `wc` | счёт строк / слов / байт | `-l`, `-w`, `-c` |
| `touch` | создать пустой файл в VFS | несколько файлов |
| `echo` | вывести аргументы | раскрытие `$VAR` |
| `conf-dump` | параметры эмулятора | — |
| `exit` | закрыть окно | — |

## Структура проекта

```
.
├── src/
│   ├── main.py          # точка входа, GUI, диспатчер команд
│   └── vfs.py           # модель VFS: Node, VFS, VfsError
├── tests/
│   └── test_smoke.py    # простейший смоук-тест
├── script/
│   └── startup.txt      # стартовый скрипт эмулятора
├── os_script/
│   ├── run_default.bat  # запуск без параметров
│   ├── run_config.bat   # запуск с config.ini
│   ├── run_cli.bat      # запуск только с CLI
│   ├── run_override.bat # CLI перекрывает INI
│   ├── run_all.bat      # все тесты подряд
│   └── run_errors.bat   # тесты ошибок конфига
├── vfs_samples/         # тестовые VFS (минимальная, несколько файлов, глубокая)
├── config.ini           # конфигурация
├── run.bat              # скрипт запуска
└── README.md
```

## Требования

- Python 3.8+
- tkinter (входит в стандартную поставку Python для Windows)

## Запуск

### Через run.bat

```bat
run.bat
```

### Вручную

```bash
python src/main.py --vfs vfs_samples
```

### С параметрами

```bash
# только VFS
python src/main.py --vfs vfs_samples

# VFS + стартовый скрипт
python src/main.py --vfs vfs_samples --script scripts/startup.txt

# через конфиг
python src/main.py --config config.ini

# CLI перекрывает конфиг
python src/main.py --config config.ini --vfs other_vfs
```

## Параметры командной строки

| Параметр | Описание |
|---|---|
| `--vfs PATH` | путь к физическому расположению VFS |
| `--script PATH` | путь к стартовому скрипту |
| `--config PATH` | путь к INI-конфигу |

## Конфигурационный файл

`config.ini` в формате INI:

```ini
[main]
vfs_path     = vfs_samples
start_script = scripts/startup.txt
```

Приоритет: **CLI > INI > значение по умолчанию**.

## Стартовый скрипт

Файл с командами эмулятора. Поддерживает комментарии (`#`).
При выполнении отображается ввод и вывод — имитация диалога:

```
> ls
вв.txt
папка1
> cd папка1
/папка1
```

## Примеры использования

### `ls` с флагами

```
> ls
> ls -a
> ls -l
> ls -lh
> ls -la /
> ls -lS
> ls -R
```

### `cd` со спец-формами

```
> cd /
> cd папка1
> cd ..
> cd ~
> cd -
> cd 'папка с пробелом'
```

### `tail` и `wc`

```
> tail файл.txt
> tail -n 5 файл.txt
> wc файл.txt
> wc -l файл.txt
```

### `touch`

```
> touch new.txt
> touch a.txt b.txt c.txt
```

### Раскрытие переменных

```
> echo $HOME
C:\Users\danil
> echo ${USERNAME}
danil
> echo $TEMP
C:\Users\danil\AppData\Local\Temp
```

### `conf-dump`

```
> conf-dump
Параметры эмулятора:
  vfs_path = vfs_samples  (источник: cli)
  start_script = scripts/startup.txt  (источник: cli)
  config_path = None
  vfs_loaded = True
  vfs_name   = vfs_samples
  vfs_pwd    = /
```

## Тесты

```bash
python tests/test_smoke.py
```

## Обработка ошибок

Эмулятор корректно обрабатывает:

- неизвестные команды: `error: unknown command 'xyz'`
- неверные аргументы: `cd: too many arguments: [...]`
- несуществующие пути в VFS: `ls: cannot access 'nope': No such file or directory`
- файлы вместо директорий: `cd: not a directory: file.txt`
- ошибки конфига: файл не найден, нет секции `[main]`, синтаксическая ошибка
- ошибки загрузки VFS: путь не найден, не директория

## Лицензия

Учебный проект.
