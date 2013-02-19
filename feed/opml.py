# feed.opml -- OPML XML creation library module

# This is the BSD license. For more information, see:
# http://www.opensource.org/licenses/bsd-license.php
#
# Copyright (c) 2006, Steve R. Hastings
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
# 
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
# 
#     * Neither the name of Steve R. Hastings nor the names
#       of any contributors may be used to endorse or promote products
#       derived from this software without specific prior written
#       permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



"""
Module to make it really easy to create OPML XML data.

This module is intended to be current with the most recent version of
OPML.  For OPML 1.0, please use feed.opml1 instead.

You might want to start with the test cases at the end; see how they
work, and then go back and look at the code in the module.

Please send questions, comments, and bug reports to: pyfeed@langri.com
"""



import types

from xe import *



module_name = "feed.opml"
module_version = "0.7.4"
module_banner = "%s version %s" % (module_name, module_version)



import feed.date.rfc822 as rfc822
from feed.date.rfc822 import set_default_time_offset
from feed.date.tools import tf_from_s

class Timestamp(CustomTimestampElement):
    def __init__(self, tag_name, tf=None, time_offset=None):
        CustomTimestampElement.__init__(self, tag_name, tf, time_offset,
                rfc822.s_offset_default,
                rfc822.timestamp_from_tf,
                tf_from_s,
                rfc822.cleanup_time_offset)



s_text = "text"
s_type = "type"
s_is_comment = "isComment"
s_is_breakpoint = "isBreakpoint"
s_created = "created"
s_category = "category"
s_xml_url = "xmlUrl"
s_html_url = "htmlUrl"
s_url = "url"
s_title = "title"
s_description = "description"
s_language = "language"
s_version = "version"


class Title(TextElement):
    def __init__(self, text="title of OPML document goes here"):
        TextElement.__init__(self, "title", text)
        
class DateCreated(Timestamp):
    def __init__(self, tf=None):
        Timestamp.__init__(self, "dateCreated", tf)

class DateModified(Timestamp):
    def __init__(self, tf=None):
        Timestamp.__init__(self, "dateModified", tf)

class OwnerName(TextElement):
    def __init__(self, text="owner name goes here"):
        TextElement.__init__(self, "ownerName", text)
        
class OwnerEmail(TextElement):
    def __init__(self, text="owner@example.com"):
        TextElement.__init__(self, "ownerEmail", text)
        
class OwnerID(TextElement):
    def __init__(self, text="http://www.example.com/contact_me.html"):
        TextElement.__init__(self, "ownerId", text)
        
class Docs(TextElement):
    def __init__(self, text="http://www.opml.org/spec2/"):
        TextElement.__init__(self, "docs", text)
        

class ExpansionState(CustomElement):
    def __init__(self, exstate=None):
        # exstate: a list of integer values representing expansion state
        CustomElement.__init__(self, "expansionState",
                exstate, types.ListType)

    def check_value(self, value):
        if type(value) is not types.ListType:
            raise TypeError, "expansionState must be list of integers"
        for x in value:
            if type(x) is not types.IntType:
                raise TypeError, "expansionState must be list of integers"
            # check for invalid values
            if x < 0:
                raise ValueError, "negative numbers not allowed in list"
        return value

    def value_from_s(self, s):
        s = s.replace(",", " ")     # replace each comma with a space
        lst = s.split()     # split on any whitespace

        exstate = []
        for s in lst:
            try:
                int_val = int(s)
            except ValueError:
                # it wasn't a valid integer so give up
                return None
            # check for invalid values
            if int_val < 0:
                # negative integer is not valid so give up
                return None
            exstate.append(int_val)
        return exstate

    def s_from_value(self):
        if self.value is None:
            return ""
        lst = [str(int_val) for int_val in self.value]
        return ", ".join(lst)



class VertScrollState(IntElement):
    def __init__(self, value=None):
        IntElement.__init__(self, "vertScrollState", value, min=0)

class WindowTop(IntElement):
    def __init__(self, value=None):
        IntElement.__init__(self, "windowTop", value, min=0)

class WindowLeft(IntElement):
    def __init__(self, value=None):
        IntElement.__init__(self, "windowLeft", value, min=0)

class WindowBottom(IntElement):
    def __init__(self, value=None):
        IntElement.__init__(self, "windowBottom", value, min=0)

class WindowRight(IntElement):
    def __init__(self, value=None):
        IntElement.__init__(self, "windowRight", value, min=0)

class Head(NestElement):
    def __init__(self):
        NestElement.__init__(self, "head")
        self.title = Title()
        self.date_created = DateCreated()
        self.date_modified = DateModified()
        self.owner_name = OwnerName()
        self.owner_email = OwnerEmail()
        self.owner_id = OwnerID()
        self.docs = Docs()
        self.expansion_state = ExpansionState()
        self.vert_scroll_state = VertScrollState()
        self.window_top = WindowTop()
        self.window_left = WindowLeft()
        self.window_bottom = WindowBottom()
        self.window_right = WindowRight()
        



class OutlineTimestamp(object):
    def __init__(self, value=None):
        if value is None:
            # default to current time created
            self.tf = rfc822.tf_utc()
        else:
            self.set(value)
        self.time_offset = rfc822.s_offset_default
    def __cmp__(self, o):
        return cmp(self.tf, o.tf)
    def __str__(self):
        if self.tf:
            return rfc822.timestamp_from_tf(self.tf, self.time_offset)
        return ""
    def update(self):
        self.tf = rfc822.tf_utc()
    def set(self, value):
        if type(value) is types.FloatType:
            self.tf = value
        elif type(value) in types.StringTypes:
            self.tf = value
            tf = rfc822.tf_from_timestamp(value)
            if tf:
                self.tf = tf
            else:
                raise ValueError, "string must be valid timestamp"
        else:
                raise TypeError, \
                    "must be time float or valid timestamp string"

class OutlineAttrs(Attrs):
    def __init__(self, text="", created=None):
        Attrs.__init__(self)
        self.__setitem__(s_text, text)
        self.__setitem__(s_created, OutlineTimestamp(created))
        attr_names = [s_text, s_type, s_is_comment,
            s_is_breakpoint, s_created, s_category,
            s_xml_url, s_html_url, s_url, s_title, s_description,
            s_language, s_version]
        self.set_names(attr_names)

    def __cmp__(self, o):
        return cmp(self._attrs_dict, o._attrs_dict)

    def __getitem__(self, k):
        if k == s_created:
            return self._attrs_dict[s_created]
        Attrs.__getitem__(self, k)

    def __setitem__(self, k, value):
        if k == s_created:
            try:
                created = self._attrs_dict[s_created]
                created.set(value)
                return
            except KeyError:
                pass  # fall through to Attrs.__setitem__()
        Attrs.__setitem__(self, k, value)



class Outline(ListElement):
    def __init__(self, text="", created=None):
        """
        Arguments:
            text -- text of this outline element

            Note: for <outline> the text is stored as an attribute
            called "text".  This is a NestElement, not a TextElement!
        """
        ListElement.__init__(self, Outline, "outline")

        self._lock = False
        self.attrs = OutlineAttrs(text, created)
        self._lock = True

        self._direct_types = list(types.StringTypes)

    def direct(self, value):
        """
        Handle direct assignment.

        Supported types for direct assignment: string
        """
        assert self._direct_types == list(types.StringTypes)
        assert type(value) in self._direct_types

        if type(value) in types.StringTypes:
            self.attrs[s_text] = value
        else:
            raise ValueError, "value must be a string"
        
class Body(ListElement):
    def __init__(self):
        ListElement.__init__(self, Outline, "body")
        self._flags.show_when_empty = True

        
class OPML(NestElement):
    def __init__(self):
        NestElement.__init__(self, "opml")
        self.attrs["version"] = "2.0"
        self.head = Head()
        self.body = Body()
    def Validate(self):
        # REVIEW: should do some real tests here
        assert self._parent == None
        return True
        


def new_xmldoc_opml():
    """
    Creates a new XMLDoc() with an OPML() in it.  Returns both as a tuple.

    Return a tuple: (opml, channel)
    """
    xmldoc = XMLDoc()
    opml = OPML()
    xmldoc.root_element = opml

    return (xmldoc, opml)



if __name__ == "__main__":
    failed_tests = 0

    def self_test(message):
        """
        Check to see if a test failed; if so, print warnings.

        message: string to print on test failure

        Implicit arguments:
            failed_tests -- count of failed tests; will be incremented
            correct -- the expected result of the test
            result -- the actual result of the test
        """
        global failed_tests

        if result != correct:
            failed_tests += 1
            print module_banner
            print "test failed:", message
            print "    correct:", correct
            print "    result: ", result
            print

    def diff(s0, s1):
        """
        Compare two strings, line by line; return a report on any differences.
        """
        from difflib import ndiff
        lst0 = s0.split("\n")
        lst1 = s1.split("\n")
        report = '\n'.join(ndiff(lst0, lst1))
        return report

    def self_test_diff(message):
        """
        Check to see if a test failed; if so, print a diff.

        message: string to print on test failure

        Implicit arguments:
            failed_tests -- count of failed tests; will be incremented
            correct -- the expected result of the test
            result -- the actual result of the test
        """
        global failed_tests

        if result != correct:
            failed_tests += 1
            print module_banner
            print "test case failed, diff follows:"
            print diff(correct, result)
            print


    # Since this file is indented using spaces, let's indent our test
    # code using spaces too so it will compare right.
    set_indent_str("    ")

    # The default is to make time stamps using local time offset;
    # for the tests, we want a "GMT" offset default instead.
    set_default_time_offset("GMT")


    # Test: generate a test OPML doc

    correct = """\
<?xml version="1.0" encoding="utf-8"?>
<opml version="2.0">
    <head>
        <title>Silly test of OPML</title>
        <dateCreated>Mon, 20 Mar 2006 22:40:08 GMT</dateCreated>
        <dateModified>Tue, 21 Mar 2006 01:23:12 GMT</dateModified>
        <ownerName>J. Random Guy</ownerName>
        <ownerEmail>jrandom@example.com</ownerEmail>
        <ownerId>http://www.example.com/contact_me.html</ownerId>
        <docs>http://www.opml.org/spec2/</docs>
        <expansionState>1, 3, 4</expansionState>
        <vertScrollState>1</vertScrollState>
        <windowTop>61</windowTop>
        <windowLeft>304</windowLeft>
        <windowBottom>562</windowBottom>
        <windowRight>842</windowRight>
    </head>
    <body>
        <outline text="I. Intro">
            <outline text="a. First"/>
            <outline text="b. Second"/>
            <outline text="c. Third">
                <outline text="0. Even more"/>
                <outline text="1. Even more still"/>
            </outline>
            <outline
                    text="Test"
                    isComment="false"
                    isBreakpoint="false"/>
            <outline
                    text="The Mets are the best team in baseball."
                    created="Mon, 31 Oct 2005 18:21:33 GMT"
                    category="/Philosophy/Baseball/Mets,/Tourism/New York"/>
            <outline
                    text="CNET News.com"
                    type="rss"
                    xmlUrl="http://news.com.com/2547-1_3-0-5.xml"
                    htmlUrl="http://news.com.com/"
                    title="CNET News.com"
                    description="Tech news and stuff."
                    language="unknown"
                    version="RSS2"/>
        </outline>
    </body>
</opml>"""

    xmldoc, opml = new_xmldoc_opml()

    opml.head.title = "Silly test of OPML"
    opml.head.date_created = "Mon, 20 Mar 2006 22:40:08 GMT"
    opml.head.date_modified = "Tue, 21 Mar 2006 01:23:12 GMT"
    opml.head.owner_name = "J. Random Guy"
    opml.head.owner_email = "jrandom@example.com"
    opml.head.owner_id = "http://www.example.com/contact_me.html"
    opml.head.expansion_state = "1, 3, 4"
    opml.head.vert_scroll_state = "1"
    opml.head.window_top = 61
    opml.head.window_left = 304
    opml.head.window_bottom = 562
    opml.head.window_right = 842

    outline = Outline("I. Intro", created=0.0)
    opml.body.append(outline)

    o = Outline("a. First", created=0.0)
    outline.append(o)
    o = Outline("b. Second", created=0.0)
    outline.append(o)
    o = Outline("c. Third", created=0.0)
    outline.append(o)

    o.append(Outline("0. Even more", created=0.0))

    t = Outline()
    o.append(t)
    o[1] = "1. Even more still"
    o[1].attrs["created"] = 0.0

    o = Outline("Test", created=0.0)
    o.attrs["isComment"] = "false"
    o.attrs["isBreakpoint"] = "false"
    outline.append(o)

    o = Outline("The Mets are the best team in baseball.")
    o.attrs["created"] = "Mon, 31 Oct 2005 18:21:33 GMT"
    o.attrs["category"] = "/Philosophy/Baseball/Mets,/Tourism/New York"
    outline.append(o)

    o = Outline("CNET News.com", 0.0)
    o.attrs["description"] = "Tech news and stuff."
    o.attrs["htmlUrl"] = "http://news.com.com/"
    o.attrs["language"] = "unknown"
    o.attrs["title"] = "CNET News.com"
    o.attrs["type"] = "rss"
    o.attrs["version"] = "RSS2"
    o.attrs["xmlUrl"] = "http://news.com.com/2547-1_3-0-5.xml"
    outline.append(o)


    result = str(xmldoc)
    self_test_diff("generate test document 0")


    # Test: verify that xmldoc.Validate() succeeds

    if not xmldoc.Validate():
        failed_tests += 1
        print "test case failed:"
        print "xmldoc.Validate() failed."


    # Test: update a few timestamps

    opml.head.date_modified.update()
    outline.attrs["created"].update()


    from sys import exit
    s_module = module_name + " " + module_version
    if failed_tests == 0:
        print s_module + ": self-test: all tests succeeded!"
        exit(0)
    elif failed_tests == 1:
        print s_module + " self-test: 1 test failed."
        exit(1)
    else:
        print s_module + " self-test: %d tests failed." % failed_tests
        exit(1)
