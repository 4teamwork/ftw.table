from DateTime import DateTime
from datetime import datetime, timedelta 

def uid_checkbox(item, value):
    return '<input type="checkbox" name="uids:list" value="%s" />' % item.UID

def readable_size(item, num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0

def readable_author(item, author):
    return author

def readable_date(item, date):
    today = datetime.today().strftime('%Y%m%d')
    yesterday = (datetime.today() - timedelta(1)).strftime('%Y%m%d')
    strftimestring = '%d.%m.%Y %H:%M'
    if date.strftime('%Y%m%d') == today:
        strftimestring = "%s, %%H:%%M" % 'today' #XXX i18n not working atm
    elif date.strftime('%Y%m%d') == yesterday:
        strftimestring = "%s, %%H:%%M" % 'yesterday' #XXX i18n not working atm
    return date.strftime(strftimestring)
    
def linked(item, value):
    url_method = lambda: '#'
    #item = hasattr(item, 'aq_explicit') and item.aq_explicit or item
    if hasattr(item, 'getURL'):
        url_method = item.getURL
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url
    img = '<img src="%s/%s"/>' % (item.portal_url(), item.getIcon)
    link = '<a href="%s">%s%s</a>' % (url_method(), img, value) 
    return link