import html
import re
from pprint import pformat, pprint  # pylint: disable=unused-import # noqa: F401
from typing import Any


class Mod:
    mod_id: str
    re_param = re.compile(r"{{ *([_a-z0-9]+) *}}")
    re_param_mention = re.compile(r"\b[_a-z0-9]+\b")
    re_backtick = re.compile(r"`(.+?)`")
    re_md_link = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")

    def render(
        self, args: dict[str, Any], params: dict[str, Any], _task: dict[str, Any]
    ) -> str:
        raise NotImplementedError

    def assert_bool(self, val: Any) -> bool:
        if isinstance(val, bool):
            return val
        raise TypeError("Value {} is not boolean".format(pformat(val)))

    @classmethod
    def render_param_markup(cls, key: str, val: str) -> str:
        return f'<span data-name="{key}" class="param">{val}</span>'

    @classmethod
    def render_param_mention(cls, val: str) -> str:
        return f'<span class="param-mention">{val}</span>'

    def render_params(self, val: str, params: dict[str, Any]) -> str:
        return self.re_param.sub(
            lambda m: self.render_param_markup(m.group(1), params[m.group(1)]), val
        )

    @classmethod
    def render_param_mentions(cls, val: str, params: dict[str, Any]) -> str:
        return cls.re_param_mention.sub(
            lambda m: (
                cls.render_param_mention(m.group(0))
                if m.group(0) in params
                else m.group(0)
            ),
            val,
        )

    def render_param_places(self, val: str) -> str:
        return self.re_param.sub(
            lambda m: self.render_param_markup(m.group(1), m.group(1)), val
        )

    @classmethod
    def render_code(cls, val: str) -> str:
        return f"<code>{val}</code>"

    @classmethod
    def render_block_code(cls, val: str) -> str:
        return f"<pre>{val}</pre>"

    @classmethod
    def render_backtick(cls, val: str) -> str:
        return cls.re_backtick.sub(lambda m: cls.render_code(m.group(1)), val)

    @classmethod
    def render_markdown_links(cls, val: str) -> str:
        return cls.re_md_link.sub(
            lambda m: '<a href="{}">{}</a>'.format(m.group(2), m.group(1)), val
        )

    @classmethod
    def render_debug(cls, val: str) -> str:
        return '<div class="debug">{}</div>'.format(
            cls.render_new_lines(cls.render_markdown_links(cls.render_backtick(val)))
        )

    @classmethod
    def render_new_lines(cls, val: str) -> str:
        return val.replace("\n", "<br>")

    def parse_bool(self, val: Any) -> bool:
        if isinstance(val, bool):
            return val
        raise TypeError("Value {} is not boolean".format(pformat(val)))

    def parse_loosy_list(self, val: Any | str) -> list[str]:
        if isinstance(val, str):
            return [x.strip() for x in val.split(",") if x.strip()]
        if isinstance(val, list):
            return val
        raise TypeError("Value {} is not a list of CSV string".format(pformat(val)))


class DebugMod(Mod):
    mod_id = "debug"

    def render(
        self, args: dict[str, Any], _params: dict[str, Any], _task: dict[str, Any]
    ) -> str:
        msg = args["msg"]
        assert isinstance(msg, str)
        return self.render_debug(msg)


class FailMod(Mod):
    mod_id = "fail"

    def render(
        self, args: dict[str, Any], _params: dict[str, Any], _task: dict[str, Any]
    ) -> str:
        msg = args["msg"]
        assert isinstance(msg, str)
        return "Fail book with message {}".format(self.render_block_code(msg))


class AptMod(Mod):
    mod_id = "apt"

    def render(
        self, args: dict[str, Any], _params: dict[str, Any], _task: dict[str, Any]
    ) -> str:
        update_cache = self.assert_bool(args.get("update_cache", False))
        pkg_name = None
        state = None
        if not update_cache:
            pkg_name = args["name"]
            state = args.get("state", "installed")
            if isinstance(pkg_name, list):
                pkg_name = " ".join(pkg_name)
        update_cache_msg = "Update APT cache with command {}. ".format(
            self.render_code("apt update")
        )
        if pkg_name:
            msg = update_cache_msg if update_cache else ""
            if state == "installed":
                return "{}Run command <code>apt install {}</code>".format(msg, pkg_name)
            raise RuntimeError(f"Unexpected apt state: {state}")
        if update_cache:
            return update_cache_msg
        return "Do nothing"


class SystemdServiceMod(Mod):
    mod_id = "systemd_service"

    def render(
        self, args: dict[str, Any], _params: dict[str, Any], _task: dict[str, Any]
    ) -> str:
        pkg_name = args["name"]
        state = args.get("state")
        enabled = args.get("enabled")
        ret = []
        if state == "started":
            ret.append("systemctl start {}".format(pkg_name))
        elif state == "stopped":
            ret.append("systemctl stop {}".format(pkg_name))
        elif state == "restarted":
            ret.append("systemctl restart {}".format(pkg_name))
        elif state:
            raise RuntimeError(f"Unexpected systemd_service state: {state}")
        if enabled is True:
            ret.append("systemctl enable {}".format(pkg_name))
        elif enabled is False:
            ret.append("systemctl disable {}".format(pkg_name))
        elif enabled is not None:
            raise RuntimeError(
                "Unexpected systemd_service enabled value: {}".format(pformat(enabled))
            )
        render_func = self.render_block_code if len(ret) > 1 else self.render_code
        return "Run command: {}".format(render_func(" \\\n    && ".join(ret)))


class UserMod(Mod):
    mod_id = "user"

    def render(
        self, args: dict[str, Any], _params: dict[str, Any], _task: dict[str, Any]
    ) -> str:
        name = args["name"]
        groups = self.parse_loosy_list(args["groups"]) if "groups" in args else None
        append = self.parse_bool(args.get("append", False))
        if groups:
            if append:
                return "Add user {} to group{} {}".format(
                    self.render_code(name),
                    "s" if len(groups) > 1 else "",
                    self.render_code(",".join(groups)),
                )
            return "Set supplimentary (all but main) groups of user {} to {}".format(
                name, ",".join(groups)
            )
        return "Do nothing"


class CommandMod(Mod):
    mod_id = "command"

    def render(
        self, args: dict[str, Any], _params: dict[str, Any], _task: dict[str, Any]
    ) -> str:
        cmd = args["cmd"]
        func = self.render_block_code if "\n" in cmd else self.render_code
        return "Run shell command {}".format(func(cmd))


class GetUrlMod(Mod):
    mod_id = "get_url"

    def render(
        self, args: dict[str, Any], _params: dict[str, Any], _task: dict[str, Any]
    ) -> str:
        url = args["url"]
        dest = args["dest"]
        return (
            "Download document at {} and save it to {}"
            " , do nothing if file exists already".format(url, dest)
        )


class SysctlMod(Mod):
    mod_id = "ansible.posix.sysctl"

    def render(
        self, args: dict[str, Any], _params: dict[str, Any], _task: dict[str, Any]
    ) -> str:
        name = args["name"]
        value = args["value"]
        conf_file = "/etc/sysctl.conf"
        cmd = "sysctl -p"
        return "Add setting {} = {} to {} and run {}".format(
            self.render_code(name),
            self.render_code(value),
            self.render_code(conf_file),
            self.render_code(cmd),
        )


class CopyMod(Mod):
    mod_id = "copy"

    def render(
        self, args: dict[str, Any], _params: dict[str, Any], _task: dict[str, Any]
    ) -> str:
        dest = args["dest"]
        content = args.get("content")
        src = args.get("src")
        force = args.get("force", False)
        group = args.get("group")
        owner = args.get("owner")
        extra = []
        extra_msg = ""
        if owner:
            extra.append("owner is {}".format(self.render_code(owner)))
        if group:
            extra.append("group is {}".format(self.render_code(group)))
        if extra:
            extra_msg = ", ensure its {}".format(" and ".join(extra))
        msg = " ({} if file exists)".format(
            "OVERWRITE" if force else "DO NOT overwrite"
        )
        if content and src:
            raise RuntimeError("Both content and src option are defined")
        if content:
            return "Write to file {}{} this content{}<pre>{}</pre>".format(
                self.render_code(dest), msg, extra_msg, html.escape(content)
            )
        if src:
            return "Copy from book directory file {} to file {}{}{}".format(
                self.render_code(src), self.render_code(dest), msg, extra_msg
            )
        raise RuntimeError("Either content or src option must be defined")


class LineInFileMod(Mod):
    mod_id = "lineinfile"

    def render(
        self, args: dict[str, Any], _params: dict[str, Any], task: dict[str, Any]
    ) -> str:
        path = args["path"]
        insertbefore = args.get("insertbefore", "EOF")
        line = args["line"]
        regexp = args["regexp"]
        if "render-simple-setting" in task.get("tags", []):
            return "Add line {} to file {}".format(
                self.render_code(line),
                self.render_code(path),
            )
        return (
            "In file {} search for line matching {} and replace it with {}."
            " If no match, insert this line before {}".format(
                self.render_code(path),
                self.render_code(regexp),
                self.render_code(line),
                self.render_code(insertbefore),
            )
        )


class FileMod(Mod):
    mod_id = "file"

    def render(
        self, args: dict[str, Any], _params: dict[str, Any], _task: dict[str, Any]
    ) -> str:
        path = args["path"]
        attributes = args.get("attributes")
        group = args.get("group")
        owner = args.get("owner")
        state = args.get("state")
        mode = args.get("mode")
        extra = []
        if owner and group:
            extra.append("chown {}:{} {}".format(owner, group, path))
        elif owner:
            extra.append("chown {} {}".format(owner, path))
        elif group:
            extra.append("chown :{} {}".format(group, path))
        if attributes:
            extra.append("chattr {} {}".format(attributes, path))
        if mode:
            extra.append("chmod {} {}".format(mode, path))
        extra_cmd = " \\\n    && ".join(extra) if extra else ""
        extra_cmd_joiner = " \\\n    && " if extra_cmd else ""
        if state == "directory":
            ret = "mkdir -p {}{}{}".format(path, extra_cmd_joiner, extra_cmd)
        elif state == "link":
            src = args.get("src")
            ret = "ln -s {} {}{}{}".format(src, path, extra_cmd_joiner, extra_cmd)
        else:
            ret = extra_cmd
        func = self.render_block_code if "\n" in ret else self.render_code
        return "Run command: {}".format(func(ret))


class ReplaceMod(Mod):
    mod_id = "replace"

    def render(
        self, args: dict[str, Any], _params: dict[str, Any], _task: dict[str, Any]
    ) -> str:
        path = args["path"]
        regexp = args["regexp"]
        replace = args["replace"]
        return "In file {} replace all lines that match regexp {} with {}".format(
            path, regexp, replace
        )


class AuthorizedKeyMod(Mod):
    mod_id = "ansible.posix.authorized_key"

    def render(
        self, args: dict[str, Any], _params: dict[str, Any], _task: dict[str, Any]
    ) -> str:
        key = args["key"]
        user = args["user"]
        return "Add key located at {} to SSH authorized keys of user {}".format(
            key, user
        )


ALL_MODS = [
    DebugMod,
    FailMod,
    AptMod,
    SystemdServiceMod,
    CopyMod,
    LineInFileMod,
    FileMod,
    ReplaceMod,
    UserMod,
    CommandMod,
    GetUrlMod,
    SysctlMod,
    AuthorizedKeyMod,
]
