from ftw.table.testing import FTWTABLE_ZCML_LAYER
from plone.testing import layered
from unittest2 import TestSuite
import doctest


def test_suite():
    readme_path = '../../../README.rst'

    suite = TestSuite()
    suite.addTests([
            layered(doctest.DocFileSuite(readme_path),
                    layer=FTWTABLE_ZCML_LAYER),
            ])
    return suite
