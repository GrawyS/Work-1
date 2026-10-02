import os


class VfsError(Exception):
    pass


class Node:
    __slots__ = ("name", "is_dir", "parent", "children", "content", "size")

    def __init__(self, name, is_dir, parent=None, content=""):
        self.name = name
        self.is_dir = is_dir
        self.parent = parent
        self.children = {} if is_dir else None
        self.content = content if not is_dir else ""
        self.size = 0 if is_dir else len(content.encode("utf-8"))

    def __repr__(self):
        kind = "dir" if self.is_dir else "file"
        return f"<Node {kind} {self.name}>"


class VFS:
    def __init__(self, root_path):
        if root_path is None:
            raise VfsError("Путь к VFS не задан")
        if not os.path.exists(root_path):
            raise VfsError(f"Файл не найден: {root_path}")
        if not os.path.isdir(root_path):
            raise VfsError(f"Не директория: {root_path}")

        try:
            root_name = os.path.basename(os.path.abspath(root_path)) or "/"
            self.root = self._load_dir(root_path, parent=None, name=root_name)
        except OSError as e:
            raise VfsError(f"Ошибка чтения VFS: {e}")

        self.cwd = self.root
        self.home = self.root
        self.prev_cwd = self.root
        self.name = self.root.name

    def _load_dir(self, path, parent, name):
        node = Node(name=name, is_dir=True, parent=parent)
        try:
            entries = os.listdir(path)
        except OSError as e:
            raise VfsError(f"Не удалось прочитать '{path}': {e}")

        for entry in entries:
            full = os.path.join(path, entry)
            try:
                if os.path.isdir(full):
                    child = self._load_dir(full, parent=node, name=entry)
                elif os.path.isfile(full):
                    with open(full, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                    child = Node(name=entry, is_dir=False, parent=node, content=content)
                else:
                    continue
            except OSError as e:
                raise VfsError(f"Не удалось загрузить '{full}': {e}")

            node.children[entry] = child

        return node

    def resolve(self, path, start=None):
        if path is None or path == "":
            return start or self.cwd

        if path == "~":
            return self.home

        if path.startswith("/"):
            node = self.root
            parts = path.strip("/").split("/")
        else:
            node = start or self.cwd
            parts = path.split("/")

        for part in parts:
            if part in ("", "."):
                continue
            if part == "..":
                node = node.parent or node
                continue
            if not node.is_dir or part not in node.children:
                return None
            node = node.children[part]

        return node

    def pwd(self):
        parts = []
        node = self.cwd
        while node is not None and node is not self.root:
            parts.append(node.name)
            node = node.parent
        return "/" + "/".join(reversed(parts)) if parts else "/"
