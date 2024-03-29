# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2011 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

from datetime import datetime
import unittest

from babel.core import Locale
from babel.messages.catalog import Catalog, Message
from babel.messages import pofile
from babel.util import FixedOffsetTimezone
from babel._compat import StringIO, BytesIO


class ReadPoTestCase(unittest.TestCase):

    def test_preserve_locale(self):
        buf = StringIO(r'''msgid "foo"
msgstr "Voh"''')
        catalog = pofile.read_po(buf, locale='en_US')
        self.assertEqual(Locale('en', 'US'), catalog.locale)

    def test_preserve_domain(self):
        buf = StringIO(r'''msgid "foo"
msgstr "Voh"''')
        catalog = pofile.read_po(buf, domain='mydomain')
        self.assertEqual('mydomain', catalog.domain)

    def test_applies_specified_encoding_during_read(self):
        buf = BytesIO('''
msgid ""
msgstr ""
"Project-Id-Version:  3.15\\n"
"Report-Msgid-Bugs-To: Fliegender Zirkus <fliegender@zirkus.de>\\n"
"POT-Creation-Date: 2007-09-27 11:19+0700\\n"
"PO-Revision-Date: 2007-09-27 21:42-0700\\n"
"Last-Translator: John <cleese@bavaria.de>\\n"
"Language-Team: German Lang <de@babel.org>\\n"
"Plural-Forms: nplurals=2; plural=(n != 1)\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=iso-8859-1\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Generated-By: Babel 1.0dev-r313\\n"

msgid "foo"
msgstr "bär"'''.encode('iso-8859-1'))
        catalog = pofile.read_po(buf, locale='de_DE')
        self.assertEqual('bär', catalog.get('foo').string)

    def test_read_multiline(self):
        buf = StringIO(r'''msgid ""
"Here's some text that\n"
"includesareallylongwordthatmightbutshouldnt"
" throw us into an infinite "
"loop\n"
msgstr ""''')
        catalog = pofile.read_po(buf)
        self.assertEqual(1, len(catalog))
        message = list(catalog)[1]
        self.assertEqual("Here's some text that\nincludesareallylongwordthat"
                         "mightbutshouldnt throw us into an infinite loop\n",
                         message.id)

    def test_fuzzy_header(self):
        buf = StringIO(r'''\
# Translations template for AReallyReallyLongNameForAProject.
# Copyright (C) 2007 ORGANIZATION
# This file is distributed under the same license as the
# AReallyReallyLongNameForAProject project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2007.
#
#, fuzzy
''')
        catalog = pofile.read_po(buf)
        self.assertEqual(1, len(list(catalog)))
        self.assertEqual(True, list(catalog)[0].fuzzy)

    def test_not_fuzzy_header(self):
        buf = StringIO(r'''\
# Translations template for AReallyReallyLongNameForAProject.
# Copyright (C) 2007 ORGANIZATION
# This file is distributed under the same license as the
# AReallyReallyLongNameForAProject project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2007.
#
''')
        catalog = pofile.read_po(buf)
        self.assertEqual(1, len(list(catalog)))
        self.assertEqual(False, list(catalog)[0].fuzzy)

    def test_header_entry(self):
        buf = StringIO(r'''\
# SOME DESCRIPTIVE TITLE.
# Copyright (C) 2007 THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2007.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version:  3.15\n"
"Report-Msgid-Bugs-To: Fliegender Zirkus <fliegender@zirkus.de>\n"
"POT-Creation-Date: 2007-09-27 11:19+0700\n"
"PO-Revision-Date: 2007-09-27 21:42-0700\n"
"Last-Translator: John <cleese@bavaria.de>\n"
"Language-Team: German Lang <de@babel.org>\n"
"Plural-Forms: nplurals=2; plural=(n != 1)\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=iso-8859-2\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel 1.0dev-r313\n"
''')
        catalog = pofile.read_po(buf)
        self.assertEqual(1, len(list(catalog)))
        self.assertEqual('3.15', catalog.version)
        self.assertEqual('Fliegender Zirkus <fliegender@zirkus.de>',
                         catalog.msgid_bugs_address)
        self.assertEqual(datetime(2007, 9, 27, 11, 19,
                                  tzinfo=FixedOffsetTimezone(7 * 60)),
                         catalog.creation_date)
        self.assertEqual('John <cleese@bavaria.de>', catalog.last_translator)
        self.assertEqual('German Lang <de@babel.org>', catalog.language_team)
        self.assertEqual('iso-8859-2', catalog.charset)
        self.assertEqual(True, list(catalog)[0].fuzzy)

    def test_obsolete_message(self):
        buf = StringIO(r'''# This is an obsolete message
#~ msgid "foo"
#~ msgstr "Voh"

# This message is not obsolete
#: main.py:1
msgid "bar"
msgstr "Bahr"
''')
        catalog = pofile.read_po(buf)
        self.assertEqual(1, len(catalog))
        self.assertEqual(1, len(catalog.obsolete))
        message = catalog.obsolete['foo']
        self.assertEqual('foo', message.id)
        self.assertEqual('Voh', message.string)
        self.assertEqual(['This is an obsolete message'], message.user_comments)

    def test_obsolete_message_ignored(self):
        buf = StringIO(r'''# This is an obsolete message
#~ msgid "foo"
#~ msgstr "Voh"

# This message is not obsolete
#: main.py:1
msgid "bar"
msgstr "Bahr"
''')
        catalog = pofile.read_po(buf, ignore_obsolete=True)
        self.assertEqual(1, len(catalog))
        self.assertEqual(0, len(catalog.obsolete))

    def test_with_context(self):
        buf = BytesIO(b'''# Some string in the menu
#: main.py:1
msgctxt "Menu"
msgid "foo"
msgstr "Voh"

# Another string in the menu
#: main.py:2
msgctxt "Menu"
msgid "bar"
msgstr "Bahr"
''')
        catalog = pofile.read_po(buf, ignore_obsolete=True)
        self.assertEqual(2, len(catalog))
        message = catalog.get('foo', context='Menu')
        self.assertEqual('Menu', message.context)
        message = catalog.get('bar', context='Menu')
        self.assertEqual('Menu', message.context)

        # And verify it pass through write_po
        out_buf = BytesIO()
        pofile.write_po(out_buf, catalog, omit_header=True)
        assert out_buf.getvalue().strip() == buf.getvalue().strip(), \
                                                            out_buf.getvalue()

    def test_with_context_two(self):
        buf = BytesIO(b'''msgctxt "Menu"
msgid "foo"
msgstr "Voh"

msgctxt "Mannu"
msgid "bar"
msgstr "Bahr"
''')
        catalog = pofile.read_po(buf, ignore_obsolete=True)
        self.assertEqual(2, len(catalog))
        message = catalog.get('foo', context='Menu')
        self.assertEqual('Menu', message.context)
        message = catalog.get('bar', context='Mannu')
        self.assertEqual('Mannu', message.context)

        # And verify it pass through write_po
        out_buf = BytesIO()
        pofile.write_po(out_buf, catalog, omit_header=True)
        assert out_buf.getvalue().strip() == buf.getvalue().strip(), out_buf.getvalue()

    def test_single_plural_form(self):
        buf = StringIO(r'''msgid "foo"
msgid_plural "foos"
msgstr[0] "Voh"''')
        catalog = pofile.read_po(buf, locale='ja_JP')
        self.assertEqual(1, len(catalog))
        self.assertEqual(1, catalog.num_plurals)
        message = catalog['foo']
        self.assertEqual(1, len(message.string))

    def test_singular_plural_form(self):
        buf = StringIO(r'''msgid "foo"
msgid_plural "foos"
msgstr[0] "Voh"
msgstr[1] "Vohs"''')
        catalog = pofile.read_po(buf, locale='nl_NL')
        self.assertEqual(1, len(catalog))
        self.assertEqual(2, catalog.num_plurals)
        message = catalog['foo']
        self.assertEqual(2, len(message.string))

    def test_more_than_two_plural_forms(self):
        buf = StringIO(r'''msgid "foo"
msgid_plural "foos"
msgstr[0] "Voh"
msgstr[1] "Vohs"
msgstr[2] "Vohss"''')
        catalog = pofile.read_po(buf, locale='lv_LV')
        self.assertEqual(1, len(catalog))
        self.assertEqual(3, catalog.num_plurals)
        message = catalog['foo']
        self.assertEqual(3, len(message.string))
        self.assertEqual('Vohss', message.string[2])

    def test_plural_with_square_brackets(self):
        buf = StringIO(r'''msgid "foo"
msgid_plural "foos"
msgstr[0] "Voh [text]"
msgstr[1] "Vohs [text]"''')
        catalog = pofile.read_po(buf, locale='nb_NO')
        self.assertEqual(1, len(catalog))
        self.assertEqual(2, catalog.num_plurals)
        message = catalog['foo']
        self.assertEqual(2, len(message.string))


class WritePoTestCase(unittest.TestCase):

    def test_join_locations(self):
        catalog = Catalog()
        catalog.add('foo', locations=[('main.py', 1)])
        catalog.add('foo', locations=[('utils.py', 3)])
        buf = BytesIO()
        pofile.write_po(buf, catalog, omit_header=True)
        self.assertEqual(b'''#: main.py:1 utils.py:3
msgid "foo"
msgstr ""''', buf.getvalue().strip())

    def test_write_po_file_with_specified_charset(self):
        catalog = Catalog(charset='iso-8859-1')
        catalog.add('foo', 'äöü', locations=[('main.py', 1)])
        buf = BytesIO()
        pofile.write_po(buf, catalog, omit_header=False)
        po_file = buf.getvalue().strip()
        assert b'"Content-Type: text/plain; charset=iso-8859-1\\n"' in po_file
        assert 'msgstr "äöü"'.encode('iso-8859-1') in po_file

    def test_duplicate_comments(self):
        catalog = Catalog()
        catalog.add('foo', auto_comments=['A comment'])
        catalog.add('foo', auto_comments=['A comment'])
        buf = BytesIO()
        pofile.write_po(buf, catalog, omit_header=True)
        self.assertEqual(b'''#. A comment
msgid "foo"
msgstr ""''', buf.getvalue().strip())

    def test_wrap_long_lines(self):
        text = """Here's some text where
white space and line breaks matter, and should

not be removed

"""
        catalog = Catalog()
        catalog.add(text, locations=[('main.py', 1)])
        buf = BytesIO()
        pofile.write_po(buf, catalog, no_location=True, omit_header=True,
                         width=42)
        self.assertEqual(b'''msgid ""
"Here's some text where\\n"
"white space and line breaks matter, and"
" should\\n"
"\\n"
"not be removed\\n"
"\\n"
msgstr ""''', buf.getvalue().strip())

    def test_wrap_long_lines_with_long_word(self):
        text = """Here's some text that
includesareallylongwordthatmightbutshouldnt throw us into an infinite loop
"""
        catalog = Catalog()
        catalog.add(text, locations=[('main.py', 1)])
        buf = BytesIO()
        pofile.write_po(buf, catalog, no_location=True, omit_header=True,
                         width=32)
        self.assertEqual(b'''msgid ""
"Here's some text that\\n"
"includesareallylongwordthatmightbutshouldnt"
" throw us into an infinite "
"loop\\n"
msgstr ""''', buf.getvalue().strip())

    def test_wrap_long_lines_in_header(self):
        """
        Verify that long lines in the header comment are wrapped correctly.
        """
        catalog = Catalog(project='AReallyReallyLongNameForAProject',
                          revision_date=datetime(2007, 4, 1))
        buf = BytesIO()
        pofile.write_po(buf, catalog)
        self.assertEqual(b'''\
# Translations template for AReallyReallyLongNameForAProject.
# Copyright (C) 2007 ORGANIZATION
# This file is distributed under the same license as the
# AReallyReallyLongNameForAProject project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2007.
#
#, fuzzy''', b'\n'.join(buf.getvalue().splitlines()[:7]))

    def test_wrap_locations_with_hyphens(self):
        catalog = Catalog()
        catalog.add('foo', locations=[
            ('doupy/templates/base/navmenu.inc.html.py', 60)
        ])
        catalog.add('foo', locations=[
            ('doupy/templates/job-offers/helpers.html', 22)
        ])
        buf = BytesIO()
        pofile.write_po(buf, catalog, omit_header=True)
        self.assertEqual(b'''#: doupy/templates/base/navmenu.inc.html.py:60
#: doupy/templates/job-offers/helpers.html:22
msgid "foo"
msgstr ""''', buf.getvalue().strip())

    def test_no_wrap_and_width_behaviour_on_comments(self):
        catalog = Catalog()
        catalog.add("Pretty dam long message id, which must really be big "
                    "to test this wrap behaviour, if not it won't work.",
                    locations=[("fake.py", n) for n in range(1, 30)])
        buf = BytesIO()
        pofile.write_po(buf, catalog, width=None, omit_header=True)
        self.assertEqual(b"""\
#: fake.py:1 fake.py:2 fake.py:3 fake.py:4 fake.py:5 fake.py:6 fake.py:7
#: fake.py:8 fake.py:9 fake.py:10 fake.py:11 fake.py:12 fake.py:13 fake.py:14
#: fake.py:15 fake.py:16 fake.py:17 fake.py:18 fake.py:19 fake.py:20 fake.py:21
#: fake.py:22 fake.py:23 fake.py:24 fake.py:25 fake.py:26 fake.py:27 fake.py:28
#: fake.py:29
msgid "pretty dam long message id, which must really be big to test this wrap behaviour, if not it won't work."
msgstr ""

""", buf.getvalue().lower())
        buf = BytesIO()
        pofile.write_po(buf, catalog, width=100, omit_header=True)
        self.assertEqual(b"""\
#: fake.py:1 fake.py:2 fake.py:3 fake.py:4 fake.py:5 fake.py:6 fake.py:7 fake.py:8 fake.py:9 fake.py:10
#: fake.py:11 fake.py:12 fake.py:13 fake.py:14 fake.py:15 fake.py:16 fake.py:17 fake.py:18 fake.py:19
#: fake.py:20 fake.py:21 fake.py:22 fake.py:23 fake.py:24 fake.py:25 fake.py:26 fake.py:27 fake.py:28
#: fake.py:29
msgid ""
"pretty dam long message id, which must really be big to test this wrap behaviour, if not it won't"
" work."
msgstr ""

""", buf.getvalue().lower())

    def test_pot_with_translator_comments(self):
        catalog = Catalog()
        catalog.add('foo', locations=[('main.py', 1)],
                    auto_comments=['Comment About `foo`'])
        catalog.add('bar', locations=[('utils.py', 3)],
                    user_comments=['Comment About `bar` with',
                                   'multiple lines.'])
        buf = BytesIO()
        pofile.write_po(buf, catalog, omit_header=True)
        self.assertEqual(b'''#. Comment About `foo`
#: main.py:1
msgid "foo"
msgstr ""

# Comment About `bar` with
# multiple lines.
#: utils.py:3
msgid "bar"
msgstr ""''', buf.getvalue().strip())

    def test_po_with_obsolete_message(self):
        catalog = Catalog()
        catalog.add('foo', 'Voh', locations=[('main.py', 1)])
        catalog.obsolete['bar'] = Message('bar', 'Bahr',
                                          locations=[('utils.py', 3)],
                                          user_comments=['User comment'])
        buf = BytesIO()
        pofile.write_po(buf, catalog, omit_header=True)
        self.assertEqual(b'''#: main.py:1
msgid "foo"
msgstr "Voh"

# User comment
#~ msgid "bar"
#~ msgstr "Bahr"''', buf.getvalue().strip())

    def test_po_with_multiline_obsolete_message(self):
        catalog = Catalog()
        catalog.add('foo', 'Voh', locations=[('main.py', 1)])
        msgid = r"""Here's a message that covers
multiple lines, and should still be handled
correctly.
"""
        msgstr = r"""Here's a message that covers
multiple lines, and should still be handled
correctly.
"""
        catalog.obsolete[msgid] = Message(msgid, msgstr,
                                          locations=[('utils.py', 3)])
        buf = BytesIO()
        pofile.write_po(buf, catalog, omit_header=True)
        self.assertEqual(b'''#: main.py:1
msgid "foo"
msgstr "Voh"

#~ msgid ""
#~ "Here's a message that covers\\n"
#~ "multiple lines, and should still be handled\\n"
#~ "correctly.\\n"
#~ msgstr ""
#~ "Here's a message that covers\\n"
#~ "multiple lines, and should still be handled\\n"
#~ "correctly.\\n"''', buf.getvalue().strip())

    def test_po_with_obsolete_message_ignored(self):
        catalog = Catalog()
        catalog.add('foo', 'Voh', locations=[('main.py', 1)])
        catalog.obsolete['bar'] = Message('bar', 'Bahr',
                                          locations=[('utils.py', 3)],
                                          user_comments=['User comment'])
        buf = BytesIO()
        pofile.write_po(buf, catalog, omit_header=True, ignore_obsolete=True)
        self.assertEqual(b'''#: main.py:1
msgid "foo"
msgstr "Voh"''', buf.getvalue().strip())

    def test_po_with_previous_msgid(self):
        catalog = Catalog()
        catalog.add('foo', 'Voh', locations=[('main.py', 1)],
                    previous_id='fo')
        buf = BytesIO()
        pofile.write_po(buf, catalog, omit_header=True, include_previous=True)
        self.assertEqual(b'''#: main.py:1
#| msgid "fo"
msgid "foo"
msgstr "Voh"''', buf.getvalue().strip())

    def test_po_with_previous_msgid_plural(self):
        catalog = Catalog()
        catalog.add(('foo', 'foos'), ('Voh', 'Voeh'),
                    locations=[('main.py', 1)], previous_id=('fo', 'fos'))
        buf = BytesIO()
        pofile.write_po(buf, catalog, omit_header=True, include_previous=True)
        self.assertEqual(b'''#: main.py:1
#| msgid "fo"
#| msgid_plural "fos"
msgid "foo"
msgid_plural "foos"
msgstr[0] "Voh"
msgstr[1] "Voeh"''', buf.getvalue().strip())

    def test_sorted_po(self):
        catalog = Catalog()
        catalog.add('bar', locations=[('utils.py', 3)],
                    user_comments=['Comment About `bar` with',
                                   'multiple lines.'])
        catalog.add(('foo', 'foos'), ('Voh', 'Voeh'),
                    locations=[('main.py', 1)])
        buf = BytesIO()
        pofile.write_po(buf, catalog, sort_output=True)
        value = buf.getvalue().strip()
        assert b'''\
# Comment About `bar` with
# multiple lines.
#: utils.py:3
msgid "bar"
msgstr ""

#: main.py:1
msgid "foo"
msgid_plural "foos"
msgstr[0] "Voh"
msgstr[1] "Voeh"''' in value
        assert value.find(b'msgid ""') < value.find(b'msgid "bar"') < value.find(b'msgid "foo"')

    def test_silent_location_fallback(self):
        buf = BytesIO(b'''\
#: broken_file.py
msgid "missing line number"
msgstr ""

#: broken_file.py:broken_line_number
msgid "broken line number"
msgstr ""''')
        catalog = pofile.read_po(buf)
        self.assertEqual(catalog['missing line number'].locations, [])
        self.assertEqual(catalog['broken line number'].locations, [])


class PofileFunctionsTestCase(unittest.TestCase):

    def test_unescape(self):
        escaped = '"Say:\\n  \\"hello, world!\\"\\n"'
        unescaped = 'Say:\n  "hello, world!"\n'
        self.assertNotEqual(unescaped, escaped)
        self.assertEqual(unescaped, pofile.unescape(escaped))

    def test_unescape_of_quoted_newline(self):
        # regression test for #198
        self.assertEqual(r'\n', pofile.unescape(r'"\\n"'))

    def test_denormalize_on_msgstr_without_empty_first_line(self):
        # handle irregular multi-line msgstr (no "" as first line)
        # gracefully (#171)
        msgstr = '"multi-line\\n"\n" translation"'
        expected_denormalized = 'multi-line\n translation'

        self.assertEqual(expected_denormalized, pofile.denormalize(msgstr))
        self.assertEqual(expected_denormalized,
                         pofile.denormalize('""\n' + msgstr))
