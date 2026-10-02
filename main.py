import tkinter as tk
import argparse
import configparser
import os


def parse_args():
    p = argparse.ArgumentParser(prog="vfs-emulator")
    p.add_argument("--vfs",    help="Путь к физическому расположению VFS")
    p.add_argument("--script", help="Путь к стартовому скрипту")
    p.add_argument("--config", help="Путь к конфигурационному файлу (INI)")
    return p.parse_args()


def load_ini(path):
    if path is None:
        return {}

    if not os.path.isfile(path):
        print(f"[ERROR] Конфиг не найден: {path}")
        return {}

    cfg = configparser.ConfigParser()
    try:
        read = cfg.read(path, encoding="utf-8")
        if not read:
            print(f"[ERROR] Не удалось прочитать конфиг: {path}")
            return {}
    except configparser.MissingSectionHeaderError:
        print(f"[ERROR] Нет заголовка секции в конфиге: {path}")
        return {}
    except configparser.ParsingError as e:
        print(f"[ERROR] Синтаксическая ошибка конфига: {e}")
        return {}
    except configparser.Error as e:
        print(f"[ERROR] Ошибка конфига: {e}")
        return {}

    if "main" not in cfg:
        print("[ERROR] В конфиге отсутствует секция [main]")
        return {}

    return {
        "vfs_path":     cfg["main"].get("vfs_path"),
        "start_script": cfg["main"].get("start_script"),
    }


def merge_config(ini, args):
    vfs_cli, vfs_ini = args.vfs, ini.get("vfs_path")
    scr_cli, scr_ini = args.script, ini.get("start_script")
    return {
        "vfs_path":         vfs_cli or vfs_ini,
        "vfs_path_src":     "cli" if vfs_cli else ("ini" if vfs_ini else "none"),
        "start_script":     scr_cli or scr_ini,
        "start_script_src": "cli" if scr_cli else ("ini" if scr_ini else "none"),
        "config_path":      args.config,
    }


def dump_config(cfg):
    print("[DEBUG] Параметры эмулятора:")
    for k, v in cfg.items():
        print(f"  {k} = {v}")


def build_gui(cfg):
    root = tk.Tk()
    root.title("VFS: shell emulator")
    root.geometry("800x500")

    output = tk.Text(
        root,
        state=tk.DISABLED,
        wrap=tk.WORD,
        background="#1e1e1e",
        foreground="#d4d4d4",
        font=("Consolas", 11),
        borderwidth=0,
    )
    output.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

    scrollbar = tk.Scrollbar(root, command=output.yview)
    scrollbar.place(relx=1.0, rely=0.0, relheight=0.85, anchor="ne")
    output.config(yscrollcommand=scrollbar.set)

    def out(text=""):
        output.config(state=tk.NORMAL)
        output.insert(tk.END, text + "\n")
        output.see(tk.END)
        output.config(state=tk.DISABLED)

    def tokenize(line):
        tokens, cur, quote = [], [], None
        for ch in line:
            if quote:
                if ch == quote:
                    quote = None
                else:
                    cur.append(ch)
            elif ch in ("'", '"'):
                quote = ch
            elif ch.isspace():
                if cur:
                    tokens.append("".join(cur))
                    cur = []
            else:
                cur.append(ch)
        if cur:
            tokens.append("".join(cur))
        return tokens

    def parse_flags(args):
        flags, operands = set(), []
        for a in args:
            if a.startswith("-") and len(a) > 1:
                flags.update(a[1:])
            else:
                operands.append(a)
        return flags, operands

    def cmd_ls(args):
        flags, operands = parse_flags(args)
        out(f"ls: flags={sorted(flags)}, paths={operands}")

    def cmd_cd(args):
        if not args:
            out("cd: go to home directory")
        elif len(args) > 1:
            out(f"cd: too many arguments: {args}")
        else:
            out(f"cd: go to '{args[0]}'")

    def cmd_exit(args):
        out("exit: exit")
        root.destroy()

    def cmd_conf_dump(args):
        out("Параметры эмулятора:")
        for k, v in cfg.items():
            if k.endswith("_src"):
                continue
            src = cfg.get(f"{k}_src")
            if src:
                out(f"  {k} = {v}  (источник: {src})")
            else:
                out(f"  {k} = {v}")

    COMMANDS = {
        "ls":        cmd_ls,
        "cd":        cmd_cd,
        "exit":      cmd_exit,
        "conf-dump": cmd_conf_dump,
    }

    def execute(line):
        parts = tokenize(line)
        if not parts:
            return
        name, args = parts[0], parts[1:]
        handler = COMMANDS.get(name)
        if handler is None:
            out(f"error: unknown command '{name}'")
            return
        handler(args)

    def run_script(path):
        if not path:
            return
        if not os.path.isfile(path):
            out(f"[ERROR] Скрипт не найден: {path}")
            return
        out(f"# --- выполнение скрипта: {path} ---")
        try:
            with open(path, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    out(f"> {line}")
                    execute(line)
        except OSError as e:
            out(f"[ERROR] Не удалось прочитать скрипт: {e}")
        out("# --- конец скрипта ---")

    def on_enter(event=None):
        line = entry.get()
        entry.delete(0, tk.END)
        out(f"> {line}")
        execute(line)

    entry = tk.Entry(root, font=("Consolas", 11))
    entry.pack(fill=tk.X, padx=10, pady=10)
    entry.bind("<Return>", on_enter)
    entry.focus_set()

    out("Shell Emulator — этап 2")
    out(f"vfs_path     = {cfg['vfs_path']}  (источник: {cfg['vfs_path_src']})")
    out(f"start_script = {cfg['start_script']}  (источник: {cfg['start_script_src']})")
    out("")

    if cfg["start_script"]:
        run_script(cfg["start_script"])

    return root


def main():
    args = parse_args()
    ini  = load_ini(args.config)
    cfg  = merge_config(ini, args)

    dump_config(cfg)

    root = build_gui(cfg)
    root.mainloop()


if __name__ == "__main__":
    main()
