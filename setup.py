from setuptools import setup, find_packages
import os

version = '1.7.2'
maintainer = 'Jonas Baumann'

tests_require = [
    'plone.app.testing',
    'plone.mocktestcase',
    ]

setup(name='ftw.table',
      version=version,
      description='Table generator utility for use within zope.',
      long_description=open("README.rst").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],

      keywords='ftw table generator',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.table',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        ],

      tests_require=tests_require,
      extras_require={
        'extjs': ['collective.js.extjs'],
        'tests': tests_require},

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
