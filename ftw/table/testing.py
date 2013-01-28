from plone.mocktestcase.dummy import Dummy
from plone.testing import Layer
from plone.testing import zca
from zope.component import getGlobalSiteManager
from zope.configuration import xmlconfig

try:
    from zope.component.hooks import setSite
except ImportError:
    # plone 4.0 support
    from zope.app.component.hooks import setSite


class FtwTableZCMLLayer(Layer):
    """ZCML test layer for ftw.table"""

    defaultBases = (zca.ZCML_DIRECTIVES, )

    def testSetUp(self):
        self['configurationContext'] = zca.stackConfigurationContext(
        self.get('configurationContext'))

        import ftw.table.tests
        xmlconfig.file('tests.zcml', ftw.table.tests,
            context=self['configurationContext'])

        response = Dummy(getHeader=lambda key: None,
                         setHeader=lambda key, value: None)
        request = Dummy(debug=False,
                        response=response)
        site = Dummy(getSiteManager=getGlobalSiteManager,
                     REQUEST=request)
        setSite(site)

    def testTearDown(self):
        del self['configurationContext']
        setSite(None)

FTWTABLE_ZCML_LAYER = FtwTableZCMLLayer()
