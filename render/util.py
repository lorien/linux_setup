from pprint import pformat, pprint  # pylint: disable=unused-import # noqa: F401
from typing import Any

import msgspec
from msgspec import Struct

from .mod import ALL_MODS, Mod

DOC_START = """
<html>
<head>
<style>
    body {
        max-width: 800px;
        margin: 1em auto;
        font-family: system-ui, sans-serif;
    }
    h3 {
        /*color: #2C3E50;*/
        margin-top: 1.5em;
    }
    p {
        margin-top: 0.5em;
    }
    pre {
        background-color: #f3f3f3;
        padding: 1em;
    }
    code {
        background-color: #f3f3f3;
        padding: 0.2em;
    }
    .warning {
        color: #900;
        font-weight: bold;
    }
    .param {
        background-color: #D6EAF8;
        font-weight: bold;
        padding: 0.2em;
    }
    .param-mention {
        font-weight: bold;
    }
    .label {
        background-color: #E5E8E8;
        padding: 0.2em;
    }
    .when-label {
        margin-bottom: 1em;
    }
    .indent-1 {
        padding-left: 0em;
        /*border-left: 5px solid #f3f3f3;*/
    }
    .debug {
        background-color: white;
        padding: 0.4em;
        border-left: 5px solid #FAD7A0;
    }
</style>
</head>
<body>
"""


class Book(Struct, kw_only=True):
    hosts: str
    connection: None | str = None
    vars: dict[str, Any]
    tasks: list[dict[str, Any]]


def build_mod_registry(mods: list[type[Mod]]) -> dict[str, Mod]:
    reg = {}
    for cls in mods:
        if cls.mod_id in reg:
            raise RuntimeError("Multiple modules have same id: {}".format(cls.mod_id))
        mod = cls()
        reg[cls.mod_id] = mod
    return reg


def get_module_args(
    task: dict[str, Any], mod_reg: dict[str, Mod]
) -> tuple[Mod, dict[str, Any]]:
    mod_id: None | str = None
    for key in task:
        if key not in {"name", "when"}:
            mod_id = key
    if mod_id is None:
        raise RuntimeError("Invalid task item: {}".format(pformat(task)))
    try:
        mod = mod_reg[mod_id]
    except KeyError as ex:
        raise RuntimeError("Unknown module: {}".format(pformat(task))) from ex
    return mod, task[mod_id]


def render_when(task: dict[str, Any], params: dict[str, Any]) -> str:
    when = task["when"]
    return Mod.render_param_mentions(
        '<div class="when-label">(!) Do this only when {}"</div>'.format(
            Mod.render_code(when)
        ),
        params,
    )


def render_tasks(
    tasks: list[dict[str, Any]],
    mod_reg: dict[str, Mod],
    params: dict[str, Any],
    indent: int,
) -> None:
    # provided_tags = set()
    print('<div class="indent-{}">'.format(indent))
    for task in tasks:
        # for tag in task.provide_tags:
        #    if tag in provided_tags:
        #        raise RuntimeError("Multiple tasks provide same tag: {}".format(tag))
        #    provided_tags.add(tag)
        # for tag in task.require_tags:
        #    if tag not in provided_tags:
        #        raise RuntimeError(
        #            "Dependency tag {} must be provided before runing"
        #            " this task: {}".format(tag, pformat(task))
        #        )
        #    provided_tags.add(tag)
        # if task.todo_comment:
        #    print(
        #        '<span class="warning">To be done: {}</span>'.format(
        #            task.todo_comment
        #        )
        #    )
        if "do-not-render" in task.get("tags", []):
            continue
        if "block" in task:
            task_name = task.get("name", "Unnamed group of tasks")
            print("<h3>{}</h3>".format(task_name))
            render_tasks(task["block"], mod_reg, params, indent + 1)
        else:
            mod, args = get_module_args(task, mod_reg)
            # task_name = task.get("name")
            # if task_name or not indent:
            #    print("<h3>{}</h3>".format(task_name if task_name else mod.mod_id))
            print("<p>")
            try:
                if "when" in task:
                    print(render_when(task, params))
                print(mod.render_params(mod.render(args, params, task), params))
            except RuntimeError:
                raise
            except Exception:
                pprint(task)
                raise
            print("</p>")
    print("</div><!-- end of div.indent-* -->")


def get_book_params(book: Book) -> dict[str, Any]:
    params = {}
    for key, val in book.vars.items():
        if key in params:
            raise RuntimeError("Parameter {} is already defined".format(key))
        params[key] = val
    return params


def render_book_params(params: dict[str, Any]) -> None:
    print("<h3>Parameters</h3>")
    if params:
        for key, val in params.items():
            print("<div>{} = {}</div>".format(key, Mod.render_param_markup(key, val)))
    else:
        print("No parameters")


def process_files(vars_path: str, tasks_path: str) -> None:
    mod_reg = build_mod_registry(ALL_MODS)
    print(DOC_START)
    with open(vars_path, mode="rb") as inp:
        params = msgspec.yaml.decode(inp.read(), type=dict[str, Any])
        render_book_params(params)
    with open(tasks_path, mode="rb") as inp:
        tasks = msgspec.yaml.decode(inp.read(), type=list[dict[str, Any]])
        render_tasks(tasks, mod_reg, params, 0)
    print("</body>")
