#!/usr/bin/env python3
from render import process_files


def main() -> None:
    process_files("book_install.yml", "tasks_install.yml")


if __name__ == "__main__":
    main()
