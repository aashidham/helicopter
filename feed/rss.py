# feed.rss -- RSS 2.0 feed creation library module

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
Module to make it really easy to work with RSS 2.0 syndication feeds.

http://blogs.law.harvard.edu/tech/rss

You might want to start with the test cases at the end; see how they
work, and then go back and look at the code in the module.

Please send questions, comments, and bug reports to: pyfeed@langri.com
"""



import types

from xe import *



module_name = "feed.rss"
module_version = "0.7.4"
module_banner = "%s version %s" % (module_name, module_version)



class Title(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "title", text)
        
class Link(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "link", text)
        
class CommentsLink(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "comments", text)
        
class Description(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "description", text)
        
class Language(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "language", text)
        
class Copyright(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "copyright", text)

class ManagingEditor(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "managingEditor", text)

class WebMaster(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "webMaster", text)

class Category(TextElement):
    def __init__(self, text="", domain=""):
        TextElement.__init__(self, "category", text)
        self.attrs[s_domain] = domain

class Generator(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "generator", text)
        
class Docs(TextElement):
    def __init__(self, text="http://blogs.law.harvard.edu/tech/rss"):
        TextElement.__init__(self, "docs", text)

s_domain = "domain"
s_port = "port"
s_path = "path"
s_regproc = "registerProcedure"
s_protocol = "protocol"

tup_protocols = ("xml-rpc", "soap", "http-post")

class Cloud(TextElement):
    def _set_attrs(self, domain, port, path, regproc, protocol):
        tup = (domain, port, path, regproc, protocol)
        for s in tup:
            if s is not None:
                break
        else:
            return
        # okay, at least one arg was specified
        for s in tup:
            if s is port and type(s) == types.IntType:
                continue
            if type(s) not in types.StringTypes:
                raise TypeError, "bad argument type: " + str(s)
            if not s:
                raise ValueError, "must specify all five args"

        if protocol not in tup_protocols:
            raise ValueError, \
                'protocol must be one of: "xml-rpc", "soap", or "http-post"'

        self.attrs[s_domain] = domain
        self.attrs[s_port] = str(port)
        self.attrs[s_path] = path
        self.attrs[s_regproc] = regproc
        self.attrs[s_protocol] = protocol

    def __init__(self, domain=None, port=None, path=None,
            regproc=None, protocol=None):
        """
        Set cloud attributes.  All five must be specified.

        Arguments:
            domain -- domain name or IP address of the cloud
            port -- TCP port upon which the cloud is running
            path -- location of the cloud's responder
            regproc -- name of the procedure to call to request notification
            protocol -- protocol is "xml-rpc", "soap", or "http-post"

            protocol is case-sensitive.
        """
        lst = [s_domain, s_port, s_path, s_regproc, s_protocol]
        TextElement.__init__(self, "cloud", "", attr_names=lst)
        self._set_attrs(domain, port, path, regproc, protocol)

    def set(self, domain, port, path, regproc, protocol):
        """
        Set cloud attributes.  All five must be specified.

        Arguments:
            domain -- domain name or IP address of the cloud
            port -- TCP port upon which the cloud is running
            path -- location of the cloud's responder
            regproc -- name of the procedure to call to request notification
            protocol -- protocol is "xml-rpc", "soap", or "http-post"

            protocol is case-sensitive.
        """
        self._set_attrs(domain, port, path, regproc, protocol)



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

class PubDate(Timestamp):
    def __init__(self, tf=None):
        Timestamp.__init__(self, "pubDate", tf)

class LastBuildDate(Timestamp):
    def __init__(self, tf=None):
        Timestamp.__init__(self, "lastBuildDate", tf)



class TTL(IntElement):
    def __init__(self, value=None):
        IntElement.__init__(self, "ttl", value, min=0)



class ImageUrl(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "url", text)

class ImageTitle(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "title", text)

class ImageLink(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "link", text)

class ImageWidth(IntElement):
    def __init__(self, value=88):
        IntElement.__init__(self, "width", value, min=0, max=144)

class ImageHeight(IntElement):
    def __init__(self, value=31):
        IntElement.__init__(self, "height", value, min=0, max=400)

class ImageDescription(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "description", text)

class Image(NestElement):
    def __init__(self, url="", title="", link="",
            width=None, height=None, description=""):
        NestElement.__init__(self, "image")
        self.url = ImageUrl(url)
        self.title = ImageTitle(title)
        self.link = ImageLink(link)
        self.width = ImageWidth(width)
        self.height = ImageHeight(height)
        self.description = ImageDescription(description)



class Rating(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "rating", text)

class TITitle(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "title", text)

class TIDescription(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "description", text)

class TIName(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "name", text)

class TILink(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "link", text)

class TextInput(NestElement):
    def __init__(self, title="", description="", name="", link=""):
        NestElement.__init__(self, "textInput")
        self.title = TITitle(title)
        self.description = TIDescription(description)
        self.name = TIName(name)
        self.link = TILink(link)


class Hour(IntElement):
    def __init__(self, value=0):
        IntElement.__init__(self, "hour", value, min=0, max=23)



class Day(CustomElement):
    # Monday==0, etc. to match the tm_wday values in the time module
    _days = {"monday":0, "tuesday":1, "wednesday":2, \
            "thursday":3, "friday":4, "saturday":5, "sunday":6}
    _day_names = ["Monday", "Tuesday", "Wednesday", \
            "Thursday", "Friday", "Saturday", "Sunday"]

    def __init__(self, value=None):
        CustomElement.__init__(self, "day", value, types.IntType)

    def check_value(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise TypeError, "day index must be an integer"
        if not 0 <= value <= 6:
            raise ValueError, "day index must be in range 0..6"
        return value

    def value_from_s(self, s):
        try:
            value = Day._days[s.lower()]
        except (AttributeError, KeyError):
            raise ValueError, \
                'can only set to valid day name ("Monday", etc.)'
        return value

    def s_from_value(self):
        if self.value is None:
            return ""
        return Day._day_names[self.value]



class SkipHours(ListElement):
    def __init__(self):
        ListElement.__init__(self, Hour, "skipHours")
        self._flags.unique_values = True
        self._flags.sorted = True

class SkipDays(ListElement):
    def __init__(self):
        ListElement.__init__(self, Day, "skipDays")
        self._flags.unique_values = True
        self._flags.sorted = True




class Author(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "author", text)

class Channel(NestElement):
    def __init__(self):
        NestElement.__init__(self, "channel")

        self.title = Title("title of feed goes here")
        self.link = Link("URL link to feed goes here")
        self.description = Description("description of feed goes here")
        self.language = Language()
        self.copyright = Copyright()
        self.managing_editor = ManagingEditor()
        self.web_master = WebMaster()
        self.pub_date = PubDate()
        self.last_build_date = LastBuildDate()
        self.categories = Collection(Category)
        self.generator = Generator()
        self.docs = Docs()
        self.cloud = Cloud()
        self.ttl = TTL()
        self.image = Image()
        self.rating = Rating()
        self.text_input = TextInput()
        self.skip_hours = SkipHours()
        self.skip_days = SkipDays()

        self.items = Collection(Item)



class EncUrl(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "url", text)

class EncLength(IntElement):
    def __init__(self, value=None):
        IntElement.__init__(self, "length", value, min=0)

class EncType(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "type", text)

class Enclosure(NestElement):
    def __init__(self, url="", length=None, type=""):
        NestElement.__init__(self, "enclosure")
        self.url = EncUrl(url)
        self.length = EncLength(length)
        self.type = EncType(type)


s_is_permalink = "isPermalink"

class Guid(TextElement):
    """
    Arguments:
        text -- the GUID as a text string.
    Atributes:
        isPermaLink -- "true" or "false"
    """
    def __init__(self, text="", is_permalink=""):
        TextElement.__init__(self, "guid", text)
        if is_permalink not in ("", "true", "false"):
            raise ValueError, 'is_permalink must be "true" or "false"'
        self.attrs[s_is_permalink] = is_permalink

s_url = "url"

class Source(TextElement):
    def __init__(self, text="", url=""):
        TextElement.__init__(self, "source", text)
        if text and not url:
            raise ValueError, "must specify both text and url"
        self.attrs[s_url] = url
    def set(self, text, url):
        self.text = text
        self.attrs[s_url] = url

class Item(NestElement):
    def __init__(self):
        NestElement.__init__(self, "item")
        self.title = Title()
        self.link = Link()
        self.description = Description()
        self.author = Author()
        self.categories = Collection(Category)
        self.comments = CommentsLink()
        self.enclosure = Enclosure()
        self.guid = Guid()
        self.pub_date = PubDate()
        self.source = Source()

s_version = "version"

class RSS(NestElement):
    def __init__(self):
        attr_names = [ s_version ]
        NestElement.__init__(self, "rss", s_version, "2.0", attr_names)
    def Validate(self):
        # REVIEW: should do some real tests here
        assert self._parent == None
        return True


def new_xmldoc_channel():
    """
    Creates a new XMLDoc() with a Channel() in it.  Returns both as a tuple.

    Return a tuple: (rss, channel)
    """
    xmldoc = XMLDoc()
    rss = RSS()
    xmldoc.root_element = rss

    channel = Channel()
    channel.generator = module_banner
    rss.channel = channel

    return (xmldoc, channel)



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


    # Test: generate an RSS doc

    correct = """\
<rss version="2.0">
    <channel>
        <title>Silly Test of RSS</title>
        <link>http://www.example.com/rss.xml</link>
        <description>Use every RSS element at least once.</description>
        <language>en-us</language>
        <copyright>Copyright 2006 by Steve R. Hastings.</copyright>
        <managingEditor>editor@example.com</managingEditor>
        <webMaster>webmaster@example.com</webMaster>
        <pubDate>Tue, 21 Mar 2006 01:23:12 GMT</pubDate>
        <lastBuildDate>Tue, 21 Mar 2006 01:20:03 GMT</lastBuildDate>
        <category>Examples</category>
        <generator>PyFeed -- feed.rss module</generator>
        <docs>http://blogs.law.harvard.edu/tech/rss</docs>
        <cloud
                domain="rpc.sys.com"
                port="80"
                path="/RPC2"
                registerProcedure="pingMe"
                protocol="soap"/>
        <ttl>60</ttl>
        <image>
            <url>http://example.com/image.jpg</url>
            <title>Example Image</title>
            <link>http://example.com</link>
            <width>64</width>
            <height>32</height>
            <description>Silly Image Example</description>
        </image>
        <rating>(this is not a valid PICS rating string)</rating>
        <textInput>
            <title>My Text Input Box</title>
            <description>Silly input box</description>
            <name>Fred</name>
            <link>http://example.com/</link>
        </textInput>
        <skipHours>
            <hour>0</hour>
            <hour>1</hour>
            <hour>22</hour>
            <hour>23</hour>
        </skipHours>
        <skipDays>
            <day>Friday</day>
            <day>Saturday</day>
            <day>Sunday</day>
        </skipDays>
        <item>
            <title>Example Blog First Entry!</title>
            <link>http://www.example.com/blog/0</link>
            <description>The official blog of example.com has begun.\
</description>
            <author>blogger@example.com</author>
            <category>Blog Entries</category>
            <comments>blogger@example.com</comments>
            <enclosure>
                <url>http://example.com/podcast/0.ogg</url>
                <length>8115596</length>
                <type>audio/ogg</type>
            </enclosure>
            <guid isPermalink="false">0xDECAFBADDEADBEEFC0FFEE</guid>
            <pubDate>Tue, 21 Mar 2006 01:06:53 GMT</pubDate>
            <source url="http://slashdot.org/">Slashdot</source>
        </item>
    </channel>
</rss>"""

    rss = RSS()
    channel = Channel()
    rss.channel = channel

    channel.title = "Silly Test of RSS"
    channel.link = "http://www.example.com/rss.xml"
    channel.description = "Use every RSS element at least once."
    channel.language = "en-us"
    channel.copyright = "Copyright 2006 by Steve R. Hastings."
    channel.managing_editor = "editor@example.com"
    channel.web_master = "webmaster@example.com"
    channel.pub_date = 1142904192.0
    channel.last_build_date = "21 Mar 2006 01:20:03 GMT"
    channel.categories.append(Category("Examples"))
    channel.generator = "PyFeed -- feed.rss module"
    channel.cloud = Cloud("rpc.sys.com", 80, "/RPC2", "pingMe", "soap")
    channel.ttl = 60
    channel.image = Image(url="http://example.com/image.jpg",
             title="Example Image", link="http://example.com",
             width=64, height=32, description="Silly Image Example")
    channel.rating = "(this is not a valid PICS rating string)"

    channel.skip_hours.append(Hour(0))
    channel.skip_hours.append(Hour(23))
    channel.skip_hours.append(Hour(22))
    channel.skip_hours.append(Hour(1))

    friday = Day().import_xml("<day>Friday</day>")
    channel.skip_days.append(friday)
    channel.skip_days.append(Day(6))
    channel.skip_days.append(Day(6))
    channel.skip_days.append(Day(6))
    channel.skip_days.append(Day(6))
    channel.skip_days.append(Day("Saturday"))

    channel.text_input = TextInput("My Text Input Box",
            "Silly input box", "Fred", "http://example.com/")

    item = Item()
    channel.items.append(item)

    item.title = "Example Blog First Entry!"
    item.link = "http://www.example.com/blog/0"
    item.description = "The official blog of example.com has begun."
    item.author = "blogger@example.com"
    item.categories.append(Category("Blog Entries"))
    item.comments = "blogger@example.com"
    item.enclosure = Enclosure("http://example.com/podcast/0.ogg",
            8115596, "audio/ogg")
    item.guid = "0xDECAFBADDEADBEEFC0FFEE"
    item.guid.attrs["isPermalink"] = "false"
    item.pub_date = "21 Mar 2006 01:06:53 GMT"
    item.source = "Slashdot"
    item.source.attrs["url"] = "http://slashdot.org/"


    result = str(rss)
    self_test_diff("generate test feed 0")


    # Test: verify that rss.Validate() succeeds

    if not rss.Validate():
        failed_tests += 1
        print "test case failed:"
        print "rss.Validate() failed."


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
