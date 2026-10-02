import tkinter as tk


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
        if a.startswith("-") and len(a) > 1 and not a[1].isdigit():
            flags.update(a[1:])
        else:
            operands.append(a)
    return flags, operands


def build_gui():
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

    COMMANDS = {
        "ls":   cmd_ls,
        "cd":   cmd_cd,
        "exit": cmd_exit,
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

    def on_enter(event=None):
        line = entry.get()
        entry.delete(0, tk.END)
        out(f"> {line}")
        execute(line)

    entry = tk.Entry(root, font=("Consolas", 11))
    entry.pack(fill=tk.X, padx=10, pady=10)
    entry.bind("<Return>", on_enter)
    entry.focus_set()

    out("Shell Emulator — этап 1")
    out("Доступные команды: ls, cd, exit")
    out("")

    return root


def main():
    root = build_gui()
    root.mainloop()


if __name__ == "__main__":
    main()
