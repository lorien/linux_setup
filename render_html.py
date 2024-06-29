#!/usr/bin/env python3
from render import process_files


def main() -> None:
    process_files("ansible/book.yml", "ansible/tasks.yml")


if __name__ == "__main__":
    main()
