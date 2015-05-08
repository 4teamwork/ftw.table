Introduction
============

The `ftw.table` package provides a utility for generating HTML tables of
dicts, catalog brains and other objects.

It comes with a jQuery plugin installable with a Plone Generic Setup profile,
providing features such as sorting, filter, grouping checkboxes and more.


Purpose
-------

The main purpose of this library package is to abstract the table generation
for the `ftw.tabbedview`_ package but it can also be used in a plain
plone / zope installation.


Table generator utility
-----------------------

The table generator utility can generate HTML or JSON output.
It expects a list of data objects, accessible either in dict-like syntax by
using ``item.get(attrname)`` or in a object-like syntax by using
``item.attrname``.
It also expects a column configuration indicating which columns / attributes
are displayed in the table and how they are presented.

Examples:

    >>> from ftw.table.interfaces import ITableGenerator
    >>> from zope.component import getUtility
    >>>
    >>> generator = getUtility(ITableGenerator, name="ftw.tablegenerator")
    >>>
    >>> data = [
    ...     {'id': 1,
    ...      'name': 'Ptolemy I Soter',
    ...      'dates': '305-285 BC',
    ...     },
    ...     {'id': 2,
    ...      'name': 'Ptolemy II Philadelphos',
    ...      'dates': '288-246 BC',
    ...     }]
    >>>
    >>> columns = ['id', 'name', 'dates']
    >>> print generator.generate(data, columns)
    <table class="listing">
        <colgroup>
            <col class="col-id" />
            <col class="col-name" />
            <col class="col-dates" />
        </colgroup>
        <thead>
            <tr>
    <BLANKLINE>
                    <th id="header-id">
                        <span>id</span>
                    </th>
    <BLANKLINE>
    <BLANKLINE>
                    <th id="header-name">
                        <span>name</span>
                    </th>
    <BLANKLINE>
    <BLANKLINE>
                    <th id="header-dates">
                        <span>dates</span>
                    </th>
    <BLANKLINE>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>
                    1
                </td>
                <td>
                    Ptolemy I Soter
                </td>
                <td>
                    305-285 BC
                </td>
            </tr>
            <tr>
                <td>
                    2
                </td>
                <td>
                    Ptolemy II Philadelphos
                </td>
                <td>
                    288-246 BC
                </td>
            </tr>
        </tbody>
    </table>
    <BLANKLINE>

    >>> columns = ['id', 'name', 'dates']
    >>> print generator.generate(data, columns, output='json')
    {"totalCount": 2, "rows": [{"dates": "305-285 BC", "id": 1, "name": "Ptolemy I Soter"}, {"dates": "288-246 BC", "id": 2, "name": "Ptolemy II Philadelphos"}], "metaData": {"fields": [{"type": "string", "name": "id"}, {"type": "string", "name": "name"}, {"type": "string", "name": "dates"}], "translations": {"dragDropLocked": "dragDropLocked", "sortDescText": "sortDescText", "columnsText": "columnsText", "showGroupsText": "showGroupsText", "groupByText": "groupByText", "itemsSingular": "itemsSingular", "sortAscText": "sortAscText", "selectedRowen": "selectedRowen", "itemsPlural": "itemsPlural"}, "totalProperty": "totalCount", "root": "rows", "config": {"sort": null, "dir": "ASC", "gridstate": null}, "columns": [{"header": "id", "hidden": false, "sortable": true, "id": "id", "dataIndex": "id"}, {"header": "name", "hidden": false, "sortable": true, "id": "name", "dataIndex": "name"}, {"header": "dates", "hidden": false, "sortable": true, "id": "dates", "dataIndex": "dates"}]}}


**Defining columns**

The column definition can be either a list of attribute names or a dict with
a more complex configuration:

    >>> advanced_columns = [
    ...     {'column': 'the_attribute_name',
    ...      'column_title': 'Title to display',
    ...      'condition': lambda: True,
    ...      'sort_index': 'sortable_title',
    ...      'transform': lambda item, value: str(value)}
    ... ]

**Sorting**

The *sortable* argument adds a "sortable" css class is added to each
column header in HTML output mode.

   >>> 'sortable' in generator.generate(data, columns, sortable=True)
   True



Data sources and configurations
-------------------------------

For generating listing tables from a data source such as the Plone Catalog
there is an advanced abstraction layer.
It allows to create generic listing views of different sources such as the
Plone Catalog, SQL Alchemy or python dictionaries.

A table source is an adapter retrieving data for a table source configuration.
It is a generic way to get the data. For example there is a built-in catalog
source which has the Plone Catalog as source.

The table source config specifies which data the source has to load and how
the are sorted and presented.

See the interfaces definitions and the built in sources and configurations
for further details.


Uninstall
=========

This package provides an uninstall Generic Setup profile, however, it will
not uninstall the package dependencies.
Make sure to uninstall the dependencies if you no longer use them.


Links
=====

- Github: https://github.com/4teamwork/ftw.table
- Issues: https://github.com/4teamwork/ftw.table/issues
- Pypi: http://pypi.python.org/pypi/ftw.table
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.table


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.table`` is licensed under GNU General Public License, version 2.


.. _ftw.tabbedview: https://github.com/4teamwork/ftw.tabbedview
