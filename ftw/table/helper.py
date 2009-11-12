from DateTime import DateTime
from datetime import datetime, timedelta 
from plone.memoize import ram

def draggable(item, value):
    return '<span id="draggable-%s" class="draggable">::</span>' % item.id

def path_checkbox(item, value):
    return '<input type="checkbox" class="noborder" name="paths:list" id="%s" value="%s" alt="Select %s" title="Select %s">' % (item.id, item.getPath(),  item.Title, item.Title)

def readable_size(item, num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0

@ram.cache(lambda m,i,author: author)
def readable_author(item, author):
    #TODO: terribly inefficient. Make some HelperCommons or something 
    name = author
    user = item.acl_users.getUserById(author)
    if user is not None:
        name = user.getProperty('fullname', author)
    return '<a href="%s/author/%s">%s</a>' % (item.portal_url(), author, name)

def readable_date(item, date):
    today = datetime.today().strftime('%Y%m%d')
    yesterday = (datetime.today() - timedelta(1)).strftime('%Y%m%d')
    strftimestring = '%d.%m.%Y %H:%M'
    if date.strftime('%Y%m%d') == today:
        strftimestring = "%s, %%H:%%M" % 'heute' #XXX i18n not working atm
    elif date.strftime('%Y%m%d') == yesterday:
        strftimestring = "%s, %%H:%%M" % 'gestern' #XXX i18n not working atm
    return date.strftime(strftimestring)
    
def linked(item, value):
    url_method = lambda: '#'
    #item = hasattr(item, 'aq_explicit') and item.aq_explicit or item
    if hasattr(item, 'getURL'):
        url_method = item.getURL
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url
    img = u'<img src="%s/%s"/>' % (item.portal_url(), item.getIcon)
    link = u'<a href="%s">%s%s</a>' % (url_method(), img, value) 
    wrapper = u'<span class="linkWrapper">%s</span>' % link
    return wrapper