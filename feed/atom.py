# feed.atom -- Atom feed creation library module

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
Module to make it really easy to work with Atom syndication feeds.

You might want to start with the test cases at the end; see how they
work, and then go back and look at the code in the module.

Please send questions, comments, and bug reports to: pyfeed@langri.com
"""



from xe import *



module_name = "feed.atom"
module_version = "0.7.4"
module_banner = "%s version %s" % (module_name, module_version)



# string constants
# These string values are used in more than one place.

s_href = "href"
s_lang = "xml:lang"
s_link = "link"
s_term = "term"
s_type = "type"



class AtomText(TextElement):
    def __init__(self, tag_name, text=""):
        # legal values of type: "text", "html", "xhtml"
        # REVIEW: should add checker for values of "type"
        TextElement.__init__(self, tag_name, text, attr_names=[s_type])

class Title(AtomText):
    def __init__(self, text=""):
        AtomText.__init__(self, "title")
        self.text = text
        
class Subtitle(AtomText):
    def __init__(self, text=""):
        AtomText.__init__(self, "subtitle")
        self.text = text
        
class Content(AtomText):
    def __init__(self, text=""):
        AtomText.__init__(self, "content")
        self.text = text
        
class Summary(AtomText):
    def __init__(self, text=""):
        AtomText.__init__(self, "summary")
        self.text = text
        
class Rights(AtomText):
    def __init__(self, text=""):
        AtomText.__init__(self, "rights")
        self.text = text
        
class Id(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "id", text)
        
class Generator(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "generator", text,
                attr_names=["uri", "version"])
        
class Category(TextElement):
    def __init__(self, term_val=""):
        attr_names = [s_term, "scheme", "label"]
        TextElement.__init__(self, "category", "",
                s_term, term_val, attr_names)

class Link(TextElement):
    def __init__(self, href_val=""):
        attr_names = [
                s_href, "rel", "type", "hreflang", "title", "length", s_lang]
        TextElement.__init__(self, "link", "",
                s_href, href_val, attr_names)

class Icon(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "icon", text)

class Logo(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "logo", text)

class Name(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "name", text)

class Email(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "email", text)

class Uri(TextElement):
    def __init__(self, text=""):
        TextElement.__init__(self, "uri", text)



class BasicAuthor(NestElement):
    def __init__(self, tag_name, name):
        NestElement.__init__(self, tag_name)
        self.name = Name(name)
        self.email = Email()
        self.uri = Uri()

class Author(BasicAuthor):
    def __init__(self, name=""):
        BasicAuthor.__init__(self, "author", name)

class Contributor(BasicAuthor):
    def __init__(self, name=""):
        BasicAuthor.__init__(self, "contributor", name)



import feed.date.rfc3339 as rfc3339
from feed.date.rfc3339 import set_default_time_offset

class Timestamp(CustomTimestampElement):
    def __init__(self, tag_name, tf=None, time_offset=None):
        CustomTimestampElement.__init__(self, tag_name, tf, time_offset,
                rfc3339.s_offset_default,
                rfc3339.timestamp_from_tf,
                rfc3339.tf_from_timestamp,
                rfc3339.cleanup_time_offset)

class Updated(Timestamp):
    def __init__(self, tf=None):
        Timestamp.__init__(self, "updated", tf)

class Published(Timestamp):
    def __init__(self, tf=None):
        Timestamp.__init__(self, "published", tf)



class FeedElement(NestElement):
    def __init__(self, tag_name):
        NestElement.__init__(self, tag_name)

        self.title = Title("")
        self.id = Id("")
        self.updated = Updated()
        self.authors = Collection(Author)
        self.links = Collection(Link)

        self.subtitle = Subtitle("")
        self.categories = Collection(Category)
        self.contributors = Collection(Contributor)
        self.generator = Generator()
        self.icon = Icon()
        self.logo = Logo()
        self.rights = Rights("")

class Feed(FeedElement):
    def __init__(self):
        FeedElement.__init__(self, "feed")
        self.attrs["xmlns"] = "http://www.w3.org/2005/Atom"
        self.title.text = "Title of Feed Goes Here"
        self.id.text = "ID of Feed Goes Here"
        self.entries = Collection(Entry)

class Source(FeedElement):
    def __init__(self):
        FeedElement.__init__(self, "source")



class Entry(NestElement):
    def __init__(self):
        NestElement.__init__(self, "entry")
        self.title = Title("Title of Entry Goes Here")
        self.id = Id("ID of Entry Goes Here")
        self.updated = Updated()
        self.authors = Collection(Author)
        self.links = Collection(Link)

        self.content = Content("")
        self.summary = Summary("")
        self.categories = Collection(Category)
        self.contributors = Collection(Contributor)
        self.published = Published()
        self.rights = Rights("")
        self.source = Source()



def new_xmldoc_feed():
    """
    Creates a new XMLDoc() with a Feed() in it.  Returns both as a tuple.

    Return a tuple: (xmldoc, feed)
    """
    xmldoc = XMLDoc()
    feed = Feed()
    feed.generator = module_banner
    xmldoc.root_element = feed
    return (xmldoc, feed)







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
    set_default_time_offset("Z")


    # Test: generate the "Atom-Powered Robots Run Amok" example
    #
    # Note: the original had some of the XML declarations in
    # a different order than atomfeed puts them.  I swapped around
    # the lines here so they would match the atomfeed order.  Other
    # than that, this is the example from:
    #
    # http://www.atomenabled.org/developers/syndication/#sampleFeed

    correct = """\
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>Example Feed</title>
    <id>urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6</id>
    <updated>2003-12-13T18:30:02Z</updated>
    <author>
        <name>John Doe</name>
    </author>
    <link href="http://example.org/"/>
    <entry>
        <title>Atom-Powered Robots Run Amok</title>
        <id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>
        <updated>2003-12-13T18:30:02Z</updated>
        <link href="http://example.org/2003/12/13/atom03"/>
        <summary>Some text.</summary>
    </entry>
</feed>"""

    xmldoc = XMLDoc()
    feed = Feed()
    xmldoc.root_element = feed

    feed.title = "Example Feed"
    feed.id = "urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6"
    feed.updated = "2003-12-13T18:30:02Z"

    link = Link("http://example.org/")
    feed.links.append(link)

    author = Author("John Doe")
    feed.authors.append(author)


    entry = Entry()
    feed.entries.append(entry)
    entry.id = "urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a"
    entry.title = "Atom-Powered Robots Run Amok"
    entry.updated = "2003-12-13T18:30:02Z"
    entry.summary = "Some text."

    link = Link("http://example.org/2003/12/13/atom03")
    entry.links.append(link)


    result = str(xmldoc)
    self_test_diff("generate test feed 0")


    # Test: verify that xmldoc.Validate() succeeds

    if not xmldoc.Validate():
        failed_tests += 1
        print "test case failed:"
        print "xmldoc.Validate() failed."


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
