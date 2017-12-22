from ftw.builder.content import register_dx_content_builders
from ftw.builder.testing import BUILDER_LAYER
from ftw.testing import IS_PLONE_5
from ftw.testing.quickinstaller import snapshots
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig


snapshots.disable()


class FtwTableLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

    def setUpPloneSite(self, portal):
        if IS_PLONE_5:
            applyProfile(portal, 'plone.app.contenttypes:default')
            register_dx_content_builders(force=True)


FTWTABLE_FIXTURE = FtwTableLayer()
FTWTABLE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTWTABLE_FIXTURE, ), name="ftw.table:integration")
