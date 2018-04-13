# -*- coding: utf-8 -*-
import sys, os, pkginfo, datetime

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
pkg_info = pkginfo.Develop(os.path.join(os.path.dirname(__file__),'..'))

extensions = [
    'sphinx.ext.autodoc',
    ]

# General
source_suffix = '.rst'
master_doc = 'index'
project = pkg_info.name
first_year = 2017
current_year = datetime.datetime.now().year
copyright = (str(current_year) if current_year==first_year else ('%s-%s'%(first_year,current_year)))+' Chris Withers'
copyright = '%s Chris Withers' % datetime.datetime.now().year
version = release = pkg_info.version
exclude_patterns = [
    'description.rst',
    '_build'
]
pygments_style = 'sphinx'

# Options for HTML output
html_theme = 'default' if on_rtd else 'classic'
htmlhelp_basename = project+'doc'

# Options for LaTeX output
latex_documents = [
  ('index',project+'.tex', project+u' Documentation',
   'Chris Withers', 'manual'),
]

