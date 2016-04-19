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
    '{': ('}', lambda x: json.loads(u'{' + x + u'}')),
    '+++': ('+++', toml.loads),
    '---': ('---', yaml.load),
}

def _getmtime(path):
    mtime = os.path.getmtime(path)
    return datetime.datetime.utcfromtimestamp(mtime)


def parse_file(file_path):
    raw_data = []
    content = []
    state = BEGIN_FILE
    end_sep = None
    data_parser = None
    with open(file_path) as fp:
        for line in fp:
            if state == BEGIN_FILE:
                line = line.strip()
                if not line:
                    continue
                if line in DATA_SEPS:
                    state = IN_DATA
                    end_sep, data_parser = DATA_SEPS[line]
                    continue
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
        data = data_parser(''.join(raw_data).decode('utf-8'))
    else:
        data = {}
    html = Markup(markdown2.markdown(
        ''.join(content),
        extras=['markdown-in-html', 'smarty-pants']))
    return data, html


class PathConflict(ValueError): pass

CONFIG_FILES = (('config.toml', toml.loads),
                ('config.yaml', yaml.load),
                ('config.json', json.loads))


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
                    return parser(open(p).read())
            return {}

        d = self.data_dir
        config = eval_config(d)
        path_elems = filter(None, path.split(os.path.sep))
        for elem in path_elems:
            d = os.path.join(d, elem)
            if os.path.isdir(d):
                config.update(eval_config(d))
            else:
                break
        return config

    def get_data(self, path):
        if path.startswith('/'):
            path = path[1:]
        file_path = os.path.join(self.data_dir, path)
        if os.path.isdir(file_path):
            if os.path.isfile(file_path + '.md'):
                raise PathConflict(
                    "path {} is both a file and a directory".format(path))
            else:
                file_path = os.path.join(file_path, 'index.md')
        else:
            file_path += '.md'
        data, md_content = parse_file(file_path)
        data['path'] = '/%s' % path
        data['id'] = ('index' if path == ''
                      else os.path.basename(path))
        data['last_mod'] = _getmtime(file_path)
        data['content'] = md_content
        return data


    
