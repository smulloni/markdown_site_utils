#!/usr/bin/env python

from distutils.core import setup

setup(name="Markdown Site Utils",
      version="0.1",
      description=("Utilities for generating websites from directories "
                   "of Markdown files."),
      author="Jacob Smullyan",
      author_email="smulloni@smullyan.org",
      packages=["mdsite"],
      package_dir={'mdsite': 'mdsite'},
      package_data={'mdsite': ['testdata/*.md', 
                               'testdata/conflict/*.md']})
