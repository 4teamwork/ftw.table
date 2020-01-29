from ftw.testing.genericsetup import GenericSetupUninstallMixin
from ftw.testing.genericsetup import apply_generic_setup_layer
from unittest import TestCase
import pkg_resources


IS_PLONE_5 = pkg_resources.get_distribution('Products.CMFPlone').version >= '5'


@apply_generic_setup_layer
class TestDefaultGenericSetupUninstall(TestCase, GenericSetupUninstallMixin):

    package = 'ftw.table'


@apply_generic_setup_layer
class TestSlideGenericSetupUninstall(TestCase, GenericSetupUninstallMixin):

    package = 'ftw.table'
    if not IS_PLONE_5:
        install_profile_name = 'extjs'
        skip_files = ('cssregistry.xml')
