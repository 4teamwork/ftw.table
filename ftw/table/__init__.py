from zope.i18nmessageid import MessageFactory


_ = MessageFactory('ftw.table')

# Workaround for making i18ndude properly.
# The problem is that we only have "-manual" messages.
_(u'sortDescText')
