from plone.mocktestcase import MockTestCase
from mocker import ANY
from zope.app.component.hooks import setSite, getSite
from Products.CMFCore.utils import getToolByName


class  TestHelperMethods(MockTestCase):

    def setUp(self):
        self.REQUEST = {}
        self.item = self.mocker.mock(count=False)
        self.expect(self.item.id).result('theid')
        self.expect(self.item.Title).result('the <"escaped"> Title')
        self.expect(self.item.getPath()).result('/path/to/object')
        self.expect(self.item.getURL()).result('http://path/to/portal')
        self.expect(self.item.getIcon).result('icon.gif')
        self.expect(self.item.portal_type).result('MockType')
        # Simple REQUEST
        self.expect(self.item.REQUEST).call(lambda x: self.REQUEST)

        # plone_utils
        self.site = self.mocker.mock(count=False)
        self.plone_utils = self.mocker.mock(count=False)
        # Mock simple normalizeString Method
        self.expect(self.plone_utils.normalizeString(ANY)).call(lambda x: x.lower())
        setSite(self.site)
        self.expect(getToolByName(getSite(), 'plone_utils')).result(self.plone_utils)

        # Moke portal_properties
        self.prop_tool = self.mocker.mock(count=False)
        self.expect(self.prop_tool.get('site_properties').getProperty(
            'typesUseViewActionInListings')).result([])
        self.expect(getToolByName(getSite(), 'portal_properties')).result(self.prop_tool)


        # portal_url
        self.expect(self.item.portal_url()).result('/path/to/portal')

        # User
        user_mock = self.mocker.mock(count=False)
        self.userid = 'Demo User Name'
        self.expect(user_mock.getProperty('fullname', ANY)).call(
            lambda x, y: self.userid)
        self.expect(self.item.acl_users.getUserById('demouserid')).result(
            user_mock)
        self.expect(self.item.acl_users.getUserById('notexisting')).result(
            user_mock)

        self.replay()



    def test_draggable(self):
        from ftw.table.helper import draggable
        self.assertEqual(
            draggable(self.item, None),
            '<span id="draggable-theid" class="draggable">::</span>')

    def  test_path_checkbox(self):
        from ftw.table.helper import path_checkbox
        self.assertEqual(
            path_checkbox(self.item, None),
            '''<input type="checkbox" class="noborder selectable"
    name="paths:list" id="theid" value="/path/to/object"
    alt="Select the &lt;&quot;escaped&quot;&gt; Title" title="Select the &lt;&quot;escaped&quot;&gt; Title" />''')

    def test_path_radiobutton(self):
        from ftw.table.helper import path_radiobutton
        # Not checked radiobutton
        self.assertEqual(
            path_radiobutton(self.item, None),
            '''<input type="radio" class="noborder selectable"
    name="paths:list" id="theid" '
    value="/path/to/object" alt="Select the &lt;&quot;escaped&quot;&gt; Title" '
    title="Select the &lt;&quot;escaped&quot;&gt; Title" />''')

        # Chamge REQUEST params
        self.REQUEST = {'paths': ['/path/to/object', ]}
        self.assertEqual(
            path_radiobutton(self.item, None),
            '''<input type="radio" class="noborder selectable"
    name="paths:list" id="theid" '
    value="/path/to/object" alt="Select the &lt;&quot;escaped&quot;&gt; Title" '
    title="Select the &lt;&quot;escaped&quot;&gt; Title" checked />''')

    def test_readable_size(self):
        from ftw.table.helper import readable_size
        value = 555
        self.assertEqual(readable_size(self.item, value), '555.0bytes')
        value = 5555
        self.assertEqual(readable_size(self.item, value), '5.4KB')
        value = 5555555
        self.assertEqual(readable_size(self.item, value), '5.3MB')
        value = 5555555555
        self.assertEqual(readable_size(self.item, value), '5.2GB')
        value = 5555555555555
        self.assertEqual(readable_size(self.item, value), '5.1TB')
        # Some more values
        value = 1023
        self.assertEqual(readable_size(self.item, value), '1023.0bytes')
        value = 1024
        self.assertEqual(readable_size(self.item, value), '1.0KB')
        value = 1048576
        self.assertEqual(readable_size(self.item, value), '1.0MB')
        value = 1073741824
        self.assertEqual(readable_size(self.item, value), '1.0GB')
        value = 1099511627776
        self.assertEqual(readable_size(self.item, value), '1.0TB')

    def test_readable_author(self):
        from ftw.table.helper import readable_author
        self.assertEqual(
            readable_author(self.item, 'demouserid'),
            '<a href="/path/to/portal/author/demouserid">Demo User Name</a>')

        self.assertEqual(
            readable_author(self.item, None),
            '-')

        self.userid = ''
        self.assertEqual(
            readable_author(self.item, 'notexisting'),
            '<a href="/path/to/portal/author/notexisting">notexisting</a>')

    def  test_readable_date_time_text(self):
        from ftw.table.helper import readable_date_time_text

        # Returns None if no date is provided
        self.assertEqual(
            readable_date_time_text(self.item, None),
            None)

        # raises ValueError if date is no a datetime object
        self.assertEqual(
            readable_date_time_text(self.item, 'invalid date'),
            None)

        # Today ("heute" in German)
        from datetime import datetime, timedelta
        today = datetime.now()
        self.assertEqual(
            readable_date_time_text(self.item, today),
            'heute, ' + today.strftime('%H:%M'))
        # Yesterday ("gestern in german")
        yesterday = (today - timedelta(1))
        self.assertEqual(
            readable_date_time_text(self.item, yesterday),
            'gestern, ' + yesterday.strftime('%H:%M'))

        # Older dates will has a date only representation
        somedate = (today - timedelta(10))
        self.assertEqual(
            readable_date_time_text(self.item, somedate),
            somedate.strftime('%d.%m.%Y %H:%M'))

    def  test_readable_date_time(self):
        from ftw.table.helper import readable_date_time
        from datetime import datetime, timedelta

        self.assertEqual(
            readable_date_time(self.item, 'invalid date'),
            None)

        self.assertEqual(
            readable_date_time(self.item, None),
            None)

        somedate = (datetime.now() - timedelta(10))
        self.assertEqual(
            readable_date_time(self.item, somedate),
            somedate.strftime('%d.%m.%Y %H:%M'))

    def  test_readable_date_text(self):
        from ftw.table.helper import readable_date_text

        # Returns None if no date is provided
        self.assertEqual(
            readable_date_text(self.item, None),
            None)

        # raises ValueError if date is no a datetime object
        self.assertEqual(
            readable_date_text(self.item, 'invalid date'),
            None)

        # Today ("heute" in German)
        from datetime import datetime, timedelta
        today = datetime.now()
        self.assertEqual(
            readable_date_text(self.item, today),
            'heute')
        # Yesterday ("gestern in german")
        yesterday = (today - timedelta(1))
        self.assertEqual(
            readable_date_text(self.item, yesterday),
            'gestern')

        # Older dates will has a date only representation
        somedate = (today - timedelta(10))
        self.assertEqual(
            readable_date_text(self.item, somedate),
            somedate.strftime('%d.%m.%Y'))

    def test_readable_date(self):
        from ftw.table.helper import readable_date
        from datetime import datetime, timedelta

        self.assertEqual(
            readable_date(self.item, 'invalid date'),
            None)

        self.assertEqual(
            readable_date(self.item, None),
            u'')

        somedate = (datetime.now() - timedelta(10))
        self.assertEqual(
            readable_date(self.item, somedate),
            somedate.strftime('%d.%m.%Y'))

    def test_linked(self):
        from ftw.table.helper import linked, linked_without_icon
        # With a brain and with icon
        self.assertEqual(
            linked(self.item, self.item.Title),
            u'<span class="linkWrapper"><a href="http://path/to/portal">'
            '<img src="/path/to/portal/icon.gif"/>the &lt;&quot;escaped&quot;&gt; Title</a></span>')

        # With a brain and without icon
        self.assertEqual(
            linked_without_icon(self.item, self.item.Title),
            u'<span class="linkWrapper"><a href="http://path/to/portal">'
            'the &lt;&quot;escaped&quot;&gt; Title</a></span>')

    def test_quick_preview(self):
        from ftw.table.helper import quick_preview

        self.assertEqual(
            quick_preview(self.item, self.item.Title),
            u'<span class="linkWrapper"><a class="quick_preview" '
            'href="http://path/to/portal/quick_preview">'
            '<img src="/path/to/portal/icon.gif"/>the &lt;&quot;escaped&quot;&gt; Title</a></span>')

    def test_translated_string(self):
        """Translate something from ftw.table domain"""
        from ftw.table.helper import translated_string

        self.assertEqual(
            translated_string('ftw.table')(self.item, u'sortAscText'),
            u'sortAscText')
        self.assertEqual(
            translated_string('ftw.table')(self.item, None),
            None)
        self.assertEqual(
            translated_string('ftw.table')(self.item, 'sortAscText'),
            u'sortAscText')
