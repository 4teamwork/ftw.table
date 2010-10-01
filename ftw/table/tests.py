import unittest
import doctest
 
from Testing import ZopeTestCase as ztc
 
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
 
import ftw.table
 
@onsetup
def setup_product():
    zcml.load_config('configure.zcml', ftw.table)
 
setup_product()
ptc.setupPloneSite(extension_profiles=[])
 
doc_tests = (
)
 
functional_tests = (
    'README.txt',
)
 
def test_suite():
    return unittest.TestSuite(
        [ztc.FunctionalDocFileSuite(
            '%s' % f, package='ftw.table',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            test_class=ptc.FunctionalTestCase)
            for f in functional_tests] + 
        [ztc.ZopeDocFileSuite(
            '%s' % f, package='ftw.table',
            test_class=ptc.FunctionalTestCase)
            for f in doc_tests],
        )
 
if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
 
