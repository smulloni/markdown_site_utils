# Markdown Site Utils

Some utilities for managing Markdown files with metadata.

Requires Python 3.11 or later; tested on Python 3.11 through 3.15.

## Installation

    pip install markdown-site-utils

or, in a uv-managed project:

    uv add markdown-site-utils

## Overview

The notion is that a content-oriented website may be written as a
hierarchical series of Markdown files (with an ".md" extension) underneath
some data directory, e.g.:

    DATA_DIR/
      index.md
      foo.md
      bar.md
      subdir/
        index.md
        foo.md
        bar.md

Each file may contain metadata, written in TOML in a section at
the top, bounded by '+++' lines:

    +++
    title = "My Page Title"
    +++

    # Some Markdown

YAML and JSON may also be used. YAML blocks should start and end with lines
consisting of three dashes; JSON blocks should consist of a single JSON object
with opening and closing braces on lines by themselves. The data block is optional
but if present must begin on the first line of the file.

TOML is parsed with the standard library's
[`tomllib`](https://docs.python.org/3/library/tomllib.html), so the TOML syntax
accepted is whatever your Python version supports (TOML 1.0, plus TOML 1.1 on
Python 3.15 and later). If you need to support several Python versions, stick
to TOML 1.0 syntax.

## Usage

To use the library, create an `mdsite.DB` object with the path to your
data directory:

    mydb = mdsite.DB("/path/to/data/dir")

Then call `get_data(path)` for the path into the directory you want, leaving
out the `.md` filename suffix, and, if you are looking for an index file, leaving
out `index.md`:

    data = mydb.get_data("/node/leaf")

The above gets data for `$DATA_DIR/node/leaf.md`, or for
`$DATA_DIR/node/leaf/index.md`, if that file exists instead. If both
`node/leaf.md` and a `node/leaf/` directory exist, `mdsite.PathConflict` is
raised. If nothing exists at the path, an empty dict is returned.

The returned dict contains the file's metadata, plus these keys:

- `content`: the Markdown rendered to HTML, as a `markupsafe.Markup` string
- `last_mod`: the modification time of the Markdown file, as a timezone-aware
  `datetime` in UTC. For a directory this is the time of its `index.md` (the
  same value `get_data("/node/leaf/index")` returns), or of the directory
  itself if it has no `index.md`
- `path`: the normalized path, with a leading slash
- `id`: the last component of the path, or `"index"` for the root
- `listing`: for a directory, a `(subdirectories, pages)` tuple of sorted
  names; otherwise `None`

`get_recursive_data(path)` returns the data for a directory and every
directory beneath it, keyed by path relative to the data directory (without a
leading slash; the root is `""`). It raises `mdsite.PathConflict` if any
directory in the tree conflicts with a file.

The library also supports hierarchical configuration, also written in TOML,
YAML, or JSON, stored in files called `config.{toml,yaml,json}` depending on the
config language employed. `get_config(path)` merges the configuration found in
the data directory and each directory along `path`, with deeper files
overriding shallower ones.

## Upgrading to 0.3.0

- `last_mod` is now a timezone-aware UTC `datetime`. It used to be a naive
  `datetime` (one with no timezone) holding the UTC time. Comparing it with a
  naive `datetime` now raises `TypeError`. Compare it with aware datetimes
  instead, such as `datetime.datetime.now(datetime.UTC)`.
- For a directory, `last_mod` now comes from its `index.md` rather than the
  directory itself, so editing an index file updates it. It used to change
  only when entries were added to or removed from the directory.
- TOML is now parsed with `tomllib` instead of the third-party `toml` package.
  Parse errors are `tomllib.TOMLDecodeError` (still a `ValueError` subclass),
  and offset datetimes in TOML metadata use `datetime.timezone.utc`.

## Development

The project is managed with [uv](https://docs.astral.sh/uv/) and linted and
formatted with [ruff](https://docs.astral.sh/ruff/):

    uv sync                    # create the virtualenv and install dependencies
    uv run pytest              # run the tests
    uv run ruff check .        # lint
    uv run ruff format .       # format
    uv build                   # build the sdist and wheel

To run the tests against a particular Python version:

    uv run --isolated --python 3.15 pytest
