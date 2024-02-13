# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import enum
import inspect
import os
import sys

sys.path.insert(0, os.path.abspath("../"))

from lauterbach.trace32.rcl.version import __version__

# -- Project information -----------------------------------------------------

project = "pystart"
copyright = "2023, Lauterbach GmbH"
author = "Lauterbach GmbH"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",  # https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
    "sphinx.ext.napoleon",  # https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
    "sphinx.ext.todo",  # https://www.sphinx-doc.org/en/master/usage/extensions/todo.html
]

# Extension config options
autoclass_content = "both"  # on classes combine class and __init__ docstrings
autodoc_member_order = "bysource"  # order class members in docs as they are in the sources
autodoc_typehints = "description"  # put type hints in the method/class description, not in the signature
autodoc_typehints_types_qualified = "class-only"  # (not-upstream yet) show only the class, not the module for all types
autodoc_typehints_description_target = "documented_params"  # (not-upstream yet) don't add types for undocumented parameters, but add them for undocumented return values
napoleon_google_docstring = True  # use google docstring style
napoleon_numpy_docstring = False  # use google docstring style
napoleon_include_special_with_doc = True  # include special functions in the documentation iff they have a docstring

# Custom handlers for extensions
def autodoc_process_signature(app, what, name: str, obj, options, signature, return_annotation):
    if inspect.isclass(obj):
        # Show enum classes without constructor parameters.
        if issubclass(obj, enum.Enum) and signature == "(value)":
            return (None, None)
        # Show services classes without constructor parameters, because they are only used internally.
        if name.endswith("Service") and signature == "(api)":
            return (None, None)


def setup(app):
    app.connect("autodoc-process-signature", autodoc_process_signature)


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"

# Configuration of the theme: see https://sphinx-rtd-theme.readthedocs.io/en/stable/configuring.html
html_theme_options = {
    # "style_nav_header_background": "#56BCD8",
}

# html_logo = "_static/logo.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# We use some custom CSS to workaround an issue and customize the layout.
# html_css_files = [
#     "custom.css",
# ]
