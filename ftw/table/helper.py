from DateTime import DateTime
from datetime import datetime, timedelta 

def linked_title(obj):
    return '<a href="%s">%s</a>' % (obj.absolute_url(), obj.Title())

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0

def readable_author(author):
    return author

def readable_modified(date):

	    today = datetime.today().strftime('%Y%m%d')
	    yesterday = (datetime.today() - timedelta(1)).strftime('%Y%m%d')

	    strftimestring = '%d.%m.%Y %H:%M'
	    if date.strftime('%Y%m%d') == today:
	        strftimestring = "%s, %%H:%%M" % 'heute' #XXX i18n not working atm
	    elif date.strftime('%Y%m%d') == yesterday:
	        strftimestring = "%s, %%H:%%M" % 'gestern' #XXX i18n not working atm

	    return date.strftime(strftimestring)