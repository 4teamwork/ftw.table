from zope.i18nmessageid import MessageFactory


_ = MessageFactory('ftw.table')

# Workaround for making i18ndude properly.
# The problem is that we only have "-manual" messages.
_(u'sortDescText')


def initialize(context):
    """Initializer called when used as a Zope 2 product.

    This is referenced from configure.zcml. Regstrations as a "Zope 2 product"
    is necessary for GenericSetup profiles to work, for example.

    """
