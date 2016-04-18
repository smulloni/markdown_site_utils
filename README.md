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
