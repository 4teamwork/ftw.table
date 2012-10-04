from datetime import datetime, timedelta
from plone.memoize import ram
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.i18n import translate
import cgi
import os.path


def link(icon=True, tooltip=False, classes=None, attrs=None):
    """Generates a helper.

    Attributes:
    icon -- Shows a content type icon.
    tooltip -- Adds a "title" attribute and a "rollover" class.
    classes -- A list of additional classes.
    attrs -- A dict of additional attributes.
    """
    if classes is None:
        classes = []
    if attrs is None:
        attrs = {}

    assert isinstance(classes, list)
    assert isinstance(attrs, dict)

    def _helper(item, value):
        attributes = attrs.copy()
        attributes['class'] = classes[:]

        if tooltip:
            description = item.Description
            if callable(description):
                description = description()

            if description:
                if isinstance(description, str):
                    description = description.decode('utf-8')

                attributes['class'].append('rollover')
                attributes['title'] = cgi.escape(description, quote=True)

        return linked(item, value, show_icon=icon, attrs=attributes)
    return _helper


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
            'paths', _marker)[0] == item.getPath() and ' checked' or '')


def readable_size(item, num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0


@ram.cache(lambda m, i, author: author)
def readable_author(item, author):
    #TODO: terribly inefficient. Make some HelperCommons or something
    site = getSite()
    portal_url = getToolByName(site, 'portal_url')
    if not author:
        return '-'
    name = author
    user = site.acl_users.getUserById(author)
    if user is not None:
        name = user.getProperty('fullname', author) or author
        if not len(name):
            name = author

    if isinstance(name, unicode):
        name = name.encode('utf-8')
    if isinstance(author, unicode):
        author = author.encode('utf-8')

    return '<a href="%s/author/%s">%s</a>' % (portal_url(), author, name)


def readable_date_time_text(item, date):
    today = datetime.today().strftime('%Y%m%d')
    yesterday = (datetime.today() - timedelta(1)).strftime('%Y%m%d')
    strftimestring = '%d.%m.%Y %H:%M'
    if date is None:
        return None
    if not getattr(date, 'strftime', None):
        return None
    if date.strftime('%Y%m%d') == today:
        strftimestring = "%s, %%H:%%M" % 'heute'  # XXX i18n not working atm
    elif date.strftime('%Y%m%d') == yesterday:
        strftimestring = "%s, %%H:%%M" % 'gestern'  # XXX i18n not working atm
    return date.strftime(strftimestring)


def readable_date_time(item, date):
    strftimestring = '%d.%m.%Y %H:%M'
    if date is None:
        return None
    try:
        return date.strftime(strftimestring)
    except (ValueError, AttributeError):
        return None


def readable_date_text(item, date):
    today = datetime.today().strftime('%Y%m%d')
    yesterday = (datetime.today() - timedelta(1)).strftime('%Y%m%d')
    strftimestring = '%d.%m.%Y'
    if date is None:
        return None
    if not getattr(date, 'strftime', None):
        return None
    if date.strftime('%Y%m%d') == today:
        strftimestring = 'heute'  # XXX i18n not working atm
    elif date.strftime('%Y%m%d') == yesterday:
        strftimestring = 'gestern'  # XXX i18n not working atm
    return date.strftime(strftimestring)


def readable_date(item, date):
    if not date:
        return u''
    strftimestring = '%d.%m.%Y'
    try:
        return date.strftime(strftimestring)
    except (ValueError, AttributeError):
        return None


def linked(item, value, show_icon=True, attrs=None):
    if attrs is None:
        attrs = {}

    if 'class' not in attrs:
        attrs['class'] = []
    elif isinstance(attrs['class'], str):
        attrs['class'] = attrs['class'].decode('utf-8').strip().split(' ')
    elif isinstance(attrs, unicode):
        attrs['class'] = attrs['class'].strip().split(' ')
    else:
        attrs['class'] = list(attrs['class'])

    url_method = lambda: '#'
    #item = hasattr(item, 'aq_explicit') and item.aq_explicit or item
    if hasattr(item, 'getURL'):
        url_method = item.getURL
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url

    if show_icon:
        site = getSite()
        plone_utils = getToolByName(site, 'plone_utils')
        portal_url = getToolByName(site, 'portal_url')

        icon = item.getIcon
        if callable(icon):
            icon = icon()

        img = u'<img src="%s/%s"/>' % (portal_url(), icon)
        if not icon:
            attrs['class'].append(
                'contenttype-%s' %
                plone_utils.normalizeString(item.portal_type))
            img = u''
    else:
        img = u''

    if not isinstance(value, unicode):
        value = value.decode('utf8')
    value = cgi.escape(value, quote=True)

    href = url_method()

    # do we need to add /view ?
    if hasattr(item, 'portal_type'):
        props = getToolByName(getSite(), 'portal_properties')
        types_using_view = props.get('site_properties').getProperty(
            'typesUseViewActionInListings')
        if item.portal_type in types_using_view:
            href = os.path.join(href, 'view')

    attrs['href'] = href

    if attrs['class']:
        attrs['class'] = ' '.join(sorted(set(attrs['class'])))
    else:
        del attrs['class']
    attrs_str = ' '.join(
        ['%s="%s"' % (attrkey, attrvalue) for attrkey, attrvalue in
         sorted(attrs.items())])

    link = u'<a %s>%s%s</a>' % (attrs_str, img, value)
    wrapper = u'<span class="linkWrapper">%s</span>' % link
    return wrapper


def linked_without_icon(item, value):
    return linked(item, value, show_icon=False)


def quick_preview(item, value):
    portal_url = getToolByName(getSite(), 'portal_url')
    url_method = lambda: '#'
    #item = hasattr(item, 'aq_explicit') and item.aq_explicit or item
    if hasattr(item, 'getURL'):
        url_method = item.getURL
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url
    img = u'<img src="%s/%s"/>' % (portal_url(), item.getIcon)
    if not isinstance(value, unicode):
        value = value.decode('utf8')
    value = cgi.escape(value, quote=True)

    link = u'<a class="quick_preview" href="%s/quick_preview">%s%s</a>' % (
        url_method(), img, value)
    wrapper = u'<span class="linkWrapper">%s</span>' % link
    return wrapper


def translated_string(domain='plone'):
    domain = domain

    def _translate(item, value):
        return translate(
            value, context=getRequest(), domain=domain)
    return _translate
