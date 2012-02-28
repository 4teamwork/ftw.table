from Products.CMFCore.utils import getToolByName
from datetime import datetime, timedelta
from plone.memoize import ram
from zope.app.component.hooks import getSite
from zope.i18nmessageid import MessageFactory
import cgi
import os.path


def draggable(item, value):
    return '<span id="draggable-%s" class="draggable">::</span>' % item.id


def path_checkbox(item, value):
    title = cgi.escape(item.Title, quote=True)
    return '''<input type="checkbox" class="noborder selectable"
    name="paths:list" id="%s" value="%s"
    alt="Select %s" title="Select %s" />''' % (
        item.id, item.getPath(), title, title)


def path_radiobutton(item, value):
    _marker = [object(), ]
    title = cgi.escape(item.Title, quote=True)
    return '''<input type="radio" class="noborder selectable"
    name="paths:list" id="%s" '
    value="%s" alt="Select %s" '
    title="Select %s"%s />''' % (
        item.id, item.getPath(),
        title,
        title,
        item.REQUEST.get(
            'paths', _marker)[0]==item.getPath() and ' checked' or '')


def readable_size(item, num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0


@ram.cache(lambda m, i, author: author)
def readable_author(item, author):
    #TODO: terribly inefficient. Make some HelperCommons or something
    if not author:
        return '-'
    name = author
    user = item.acl_users.getUserById(author)
    if user is not None:
        name = user.getProperty('fullname', author) or author
        if not len(name):
            name = author
    return '<a href="%s/author/%s">%s</a>' % (item.portal_url(), author, name)


def readable_date_time_text(item, date):
    today = datetime.today().strftime('%Y%m%d')
    yesterday = (datetime.today() - timedelta(1)).strftime('%Y%m%d')
    strftimestring = '%d.%m.%Y %H:%M'
    if date == None:
        return None
    if not getattr(date, 'strftime', None):
        return None
    if date.strftime('%Y%m%d') == today:
        strftimestring = "%s, %%H:%%M" % 'heute' #XXX i18n not working atm
    elif date.strftime('%Y%m%d') == yesterday:
        strftimestring = "%s, %%H:%%M" % 'gestern' #XXX i18n not working atm
    return date.strftime(strftimestring)


def readable_date_time(item, date):
    strftimestring = '%d.%m.%Y %H:%M'
    if date == None:
        return None
    try:
        return date.strftime(strftimestring)
    except (ValueError, AttributeError):
        return None


def readable_date_text(item, date):
    today = datetime.today().strftime('%Y%m%d')
    yesterday = (datetime.today() - timedelta(1)).strftime('%Y%m%d')
    strftimestring = '%d.%m.%Y'
    if date == None:
        return None
    if not getattr(date, 'strftime', None):
        return None
    if date.strftime('%Y%m%d') == today:
        strftimestring = 'heute' #XXX i18n not working atm
    elif date.strftime('%Y%m%d') == yesterday:
        strftimestring = 'gestern' #XXX i18n not working atm
    return date.strftime(strftimestring)


def readable_date(item, date):
    if not date:
        return u''
    strftimestring = '%d.%m.%Y'
    try:
        return date.strftime(strftimestring)
    except (ValueError, AttributeError):
        return None


def linked(item, value, show_icon=True):
    url_method = lambda: '#'
    #item = hasattr(item, 'aq_explicit') and item.aq_explicit or item
    if hasattr(item, 'getURL'):
        url_method = item.getURL
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url

    type_class=''
    if show_icon:
        plone_utils = getToolByName(getSite(), 'plone_utils')
        img = u'<img src="%s/%s"/>' % (
            item.portal_url(), item.getIcon)
        if not item.getIcon:
            type_class = ' class="contenttype-%s"' % \
                plone_utils.normalizeString(item.portal_type)
    else:
        img = u''

    value = cgi.escape(value.decode('utf8'), quote=True)

    href = url_method()

    # do we need to add /view ?
    if hasattr(item, 'portal_type'):
        props = getToolByName(getSite(), 'portal_properties')
        types_using_view = props.get('site_properties').getProperty(
            'typesUseViewActionInListings')
        if item.portal_type in types_using_view:
            href = os.path.join(href, 'view')

    link = u'<a href="%s"%s>%s%s</a>' % (
        href, type_class, img, value)
    wrapper = u'<span class="linkWrapper">%s</span>' % link
    return wrapper


def linked_without_icon(item, value):
    return linked(item, value, show_icon=False)


def quick_preview(item, value):
    url_method = lambda: '#'
    #item = hasattr(item, 'aq_explicit') and item.aq_explicit or item
    if hasattr(item, 'getURL'):
        url_method = item.getURL
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url
    img = u'<img src="%s/%s"/>' % (item.portal_url(), item.getIcon)

    value = cgi.escape(value.decode('utf8'), quote=True)


    link = u'<a class="quick_preview" href="%s/quick_preview">%s%s</a>' % (
        url_method(), img, value)
    wrapper = u'<span class="linkWrapper">%s</span>' % link
    return wrapper


def translated_string(domain='plone'):
    factory = MessageFactory(domain)

    def translate(item, value):
        if not value:
            return value
        if not isinstance(value, unicode):
            value = value.decode('utf8')
        return factory(value)
    return translate
