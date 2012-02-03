from plone.testing import Layer
from plone.testing import zca
from zope.configuration import xmlconfig
from plone.mocktestcase import MockTestCase


class FtwTableZCMLLayer(Layer):
    """A layer which only sets up the zcml, but does not start a zope
    instance.
    """

    defaultBases = (zca.ZCML_DIRECTIVES, )

    def testSetUp(self):
        self['configurationContext'] = zca.stackConfigurationContext(
            self.get('configurationContext'))

        import ftw.table.tests
        xmlconfig.file('tests.zcml', ftw.table.tests,
                       context=self['configurationContext'])

    def testTearDown(self):
        del self['configurationContext']


FTWTABLE_ZCML_LAYER = FtwTableZCMLLayer()
