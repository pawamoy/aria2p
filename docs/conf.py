# -*- coding: utf-8 -*-

"""Sphinx configuration file."""

from __future__ import unicode_literals

import os

from recommonmark.transform import AutoStructify

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.ifconfig",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinxcontrib.spelling",
    "recommonmark",
]
spelling_show_suggestions = True
spelling_lang = "en_US"

autodoc_default_flags = ["members", "special-members", "show-inheritance"]

source_parsers = {".md": "recommonmark.parser.CommonMarkParser"}
source_suffix = ['.rst', '.md']
master_doc = "index"
project = "Aria2p"
year = "2018"
author = "Timothée Mazzucotelli"
copyright = "{0}, {1}".format(year, author)
version = release = "0.2.0"

pygments_style = "trac"
templates_path = ["."]
extlinks = {
    "issue": ("https://github.com/pawamoy/aria2p/issues/%s", "#"),
    "pr": ("https://github.com/pawamoy/aria2p/pull/%s", "PR #"),
}

# on_rtd is whether we are on readthedocs.org
on_rtd = os.environ.get("READTHEDOCS", None) == "True"

if not on_rtd:  # only set the theme if we're building docs locally
    html_theme = "sphinx_rtd_theme"

html_last_updated_fmt = "%b %d, %Y"
html_split_index = False
html_sidebars = {"**": ["searchbox.html", "globaltoc.html", "sourcelink.html"]}
html_short_title = "%s-%s" % (project, version)

html_context = {"extra_css_files": ["_static/extra.css"]}

html_static_path = ["extra.css"]

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False
suppress_warnings = ["image.nonlocal_uri"]

github_doc_root = "https://github.com/pawamoy/aria2p/tree/master/doc/"


def setup(app):
    app.add_config_value(
        "recommonmark_config",
        {
            "url_resolver": lambda url: github_doc_root + url,
            "auto_toc_tree_section": "Welcome to Aria2p's documentation!",
        },
        True,
    )
    app.add_transform(AutoStructify)
