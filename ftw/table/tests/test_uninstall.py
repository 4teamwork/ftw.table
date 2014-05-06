from ftw.testing.genericsetup import apply_generic_setup_layer
from ftw.testing.genericsetup import GenericSetupUninstallMixin
from unittest2 import TestCase


@apply_generic_setup_layer
class TestDefaultGenericSetupUninstall(TestCase, GenericSetupUninstallMixin):

    package = 'ftw.table'


@apply_generic_setup_layer
class TestSlideGenericSetupUninstall(TestCase, GenericSetupUninstallMixin):

    package = 'ftw.table'
    install_profile_name = 'extjs'
    skip_files = ('cssregistry.xml')
