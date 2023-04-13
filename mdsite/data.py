from builtins import object
import datetime
import os
import json

from markupsafe import Markup
import markdown2
import yaml
import toml

BEGIN_FILE = 0
IN_DATA = 1
DATA_DONE = 2
DATA_SEPS = {
    "{": ("}", lambda x: json.loads("{" + x + "}")),
    "+++": ("+++", toml.loads),
    "---": ("---", yaml.safe_load),
}


def _getmtime(path):
    mtime = os.path.getmtime(path)
    return datetime.datetime.utcfromtimestamp(mtime)


def _getlisting(dir):
    _, dirs, files = next(os.walk(dir))
    files = [f[:-3] for f in files if f.endswith(".md")]
    return sorted(dirs), sorted(files)


def parse_file(file_path):
    raw_data = []
    content = []
    state = BEGIN_FILE
    end_sep = None
    data_parser = None
    seen_sep = False
    with open(file_path) as fp:
        for line in fp:
            if state == BEGIN_FILE:
                stripped = line.strip()
                if stripped in DATA_SEPS:
                    seen_sep = True
                    state = IN_DATA
                    end_sep, data_parser = DATA_SEPS[stripped]
                else:
                    state = DATA_DONE
                    content.append(line)
            elif state == IN_DATA:
                if line.strip() == end_sep:
                    state = DATA_DONE        
                else:
                    raw_data.append(line)
            elif state == DATA_DONE:
                content.append(line)
            else:
                raise AssertionError("Unreached")
    if raw_data:
        if not data_parser:
            raise ValueError("malformed input")
        data = data_parser("".join(raw_data))
    else:
        data = {}
    html = Markup(
        markdown2.markdown(
            "".join(content), extras=["markdown-in-html", "smarty-pants"]
        )
    )
    return data, html


class PathConflict(ValueError):
    pass


CONFIG_FILES = (
    ("config.toml", toml.loads),
    ("config.yaml", yaml.safe_load),
    ("config.json", json.loads),
)


class DB(object):
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def get_config(self, path):
        """Return hierarchically overrideable configuration,
        stored in config.{toml,yaml,json} files."""

        def eval_config(directory):
            for filename, parser in CONFIG_FILES:
                p = os.path.join(directory, filename)
                if os.path.exists(p):
                    with open(p) as fp:
                        raw = fp.read()
                    return parser(raw)
            return {}

        d = self.data_dir
        config = eval_config(d)
        path_elems = [_f for _f in path.split(os.path.sep) if _f]
        for elem in path_elems:
            d = os.path.join(d, elem)
            if os.path.isdir(d):
                config.update(eval_config(d))
            else:
                break
        return config

    def _clean_path(self, path):
        path = os.path.normpath(path)
        if path.startswith("/"):
            path = path[1:]
        return path, os.path.join(self.data_dir, path)

    def get_data(self, path, listing=None):
        path, file_path = self._clean_path(path)
        if os.path.isdir(file_path):
            if os.path.isfile(file_path + ".md"):
                raise PathConflict(
                    "path {} is both a file and a directory".format(path)
                )
            if listing is None:
                listing = _getlisting(file_path)
            mtime = _getmtime(file_path)
            file_path = os.path.join(file_path, "index.md")
        else:
            file_path += ".md"
            if not os.path.exists(file_path):
                return {}
            mtime = _getmtime(file_path)
        if os.path.basename(file_path) == "index.md" and not os.path.exists(file_path):
            data = {"content": ""}
        else:
            data, md_content = parse_file(file_path)
            data["content"] = md_content
        data["listing"] = listing
        data["last_mod"] = mtime
        data["path"] = "/%s" % path
        data["id"] = "index" if path == "" else os.path.basename(path)
        return data

    def get_recursive_listing(self, path="/"):
        listing = {}
        path, file_path = self._clean_path(path)
        for root, dirs, files in os.walk(file_path):
            files = [f[:-3] for f in files if f.endswith(".md")]
            relroot = os.path.relpath(root, self.data_dir)
            if relroot.startswith("."):
                relroot = relroot[1:]
            listing[relroot] = (
                sorted(os.path.join(relroot, d) for d in dirs),
                sorted(files),
            )
        return listing

    def get_recursive_data(self, path="/"):
        data = {}
        listings = self.get_recursive_listing(path)
        for path, listing in listings.items():
            data[path] = self.get_data(path, listing)
        return data
