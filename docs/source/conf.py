# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
import pymagic9
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('./../../src'))

author = pymagic9.__author__
copyright = '2023, ' + author
project = pymagic9.nameof(pymagic9)
release = pymagic9.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.napoleon", "sphinx.ext.autodoc", "sphinx_multiversion"]

autosectionlabel_prefix_document = True

templates_path = ['_templates']
exclude_patterns = ['*.md', '**/*.md']

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = [
    "_static",
]
html_theme = "sphinx_rtd_theme"

# https://github.com/dls-controls/versiongit/blob/master/docs/conf.py
html_theme_options = dict(style_nav_header_background="rgb(7, 43, 93)")

html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# -- Options for sphinx-multiversion -----------------------------------------
smv_tag_whitelist = r'^v\d+\.\d+\.\d+$'
# smv_branch_whitelist = None
smv_released_pattern = r'^tags/.*$'
