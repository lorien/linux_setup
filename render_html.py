#!/usr/bin/env python3
from render import process_files


def main() -> None:
    process_files("linux_setup/vars.yml", "linux_setup/tasks.yml")


if __name__ == "__main__":
    main()
