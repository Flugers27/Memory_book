import os

# Дерево проекта (без корневой папки "project")
structure = {
    "common": {
        "db": {
            "base.py": "",
            "session.py": "",
            "__init__.py": ""
        },
        "security": {
            "hashing.py": "",
            "jwt_handler.py": "",
            "__init__.py": ""
        },
        "models": {
            "__init__.py": ""
        },
        "utils": {
            "__init__.py": ""
        },
        "config.py": ""
    },
    "services": {
        "auth_service": {
            "routers": {
                "auth.py": "",
                "users.py": ""
            },
            "schemas": {
                "user.py": ""
            },
            "models": {
                "user.py": ""
            },
            "repository": {
                "user_repo.py": ""
            },
            "service": {
                "auth_service.py": ""
            },
            "main.py": "",
            "__init__.py": ""
        },
        "memory_service": {
            "routers": {
                "page.py": "",
                "agent.py": "",
                "titles.py": ""
            },
            "schemas": {
                "__init__.py": ""
            },
            "models": {
                "__init__.py": ""
            },
            "repository": {
                "__init__.py": ""
            },
            "service": {
                "__init__.py": ""
            },
            "main.py": "",
            "__init__.py": ""
        },
        "genealogy_service": {
            "routers": {
                "tree.py": ""
            },
            "schemas": {
                "__init__.py": ""
            },
            "models": {
                "__init__.py": ""
            },
            "repository": {
                "__init__.py": ""
            },
            "service": {
                "__init__.py": ""
            },
            "main.py": "",
            "__init__.py": ""
        },
        "access_service": {
            "routers": {
                "access.py": ""
            },
            "schemas": {
                "__init__.py": ""
            },
            "models": {
                "__init__.py": ""
            },
            "repository": {
                "__init__.py": ""
            },
            "service": {
                "__init__.py": ""
            },
            "main.py": "",
            "__init__.py": ""
        },
        "media_service": {
            "routers": {
                "upload.py": ""
            },
            "schemas": {
                "__init__.py": ""
            },
            "models": {
                "__init__.py": ""
            },
            "repository": {
                "__init__.py": ""
            },
            "service": {
                "__init__.py": ""
            },
            "main.py": "",
            "__init__.py": ""
        }
    },
    "gateway": {
        "routes": {
            "__init__.py": ""
        },
        "main.py": "",
        "config.py": ""
    },
    "run_all.py": "",
    "README.md": ""
}


def create_structure(base_path, items):
    for name, content in items.items():
        path = os.path.join(base_path, name)

        # Если content — dict → создаём папку
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            # Иначе — создаём файл с заглушкой
            with open(path, "w", encoding="utf-8") as f:
                if name.endswith(".py"):
                    f.write("# TODO: implement\n")
                else:
                    f.write("")

# Запуск
create_structure(".", structure)
print("Структура проекта успешно создана!")
