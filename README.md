# Markdown Site Utils

Some utilities for managing Markdown files with metadata.

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

To use the library, you get create an `mdsite.DB` object with the path to your
data directory:

    mydb = mdsite.DB("/path/to/data/dir")

Then call `get_data(path)` for the path into the directory you want, leaving
out the `.md` filename suffix, and, if you are looking for an index file, leaving
out `index.md`:

    data = mydb.get_data("/node/leaf")

The above gets data for `$DATA_DIR/node/leaf.md`, or for
`$DATA_DIR/node/leaf/index.md`, if that file exists instead. 

The library also supports hierarchical configuration, also written in TOML,
YAML, or JSON, stored in files called `config.{toml,yaml,json}` depending on the
config language employed.
