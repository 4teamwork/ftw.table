from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from zope.configuration import xmlconfig
from plone.testing import z2


class FtwTableLLayer(PloneSandboxLayer):
    """A layer which only sets up the zcml, but does not start a zope
    instance.
    """

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):

        import ftw.table
        xmlconfig.file('configure.zcml', ftw.table,
                       context=configurationContext)

        z2.installProduct(app, 'ftw.foo')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.table:default')

FTW_TABLE_FIXTURE = FtwTableLLayer()
FTW_TABLE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_TABLE_FIXTURE, ),
    name="ftw.table:Integration")

