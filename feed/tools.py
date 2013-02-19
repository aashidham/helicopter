# feed.tools -- library functions useful in making syndication feeds

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
Miscellaneous functions useful in making syndication feeds.

Please send questions, comments, and bug reports to: pyfeed@langri.com
"""



import re
import time



module_name = "feed.tools"
module_version = "0.7.1"
module_banner = "%s version %s" % (module_name, module_version)



_pat_nbsp = re.compile(r'&nbsp;')
def entities_to_ws(s):
    """
    Return a copy of s with HTML whitespace entities replaced by a space.

    Currently just gets rid of HTML non-breaking spaces ("&nbsp;").
    """
    if not s:
        return s

    s = re.sub(_pat_nbsp, " ", s)
    return s



def normalize_ws(s):
    """
    Return a copy of string s with each run of whitespace replaced by one space.
    >>> s = "and    now\n\n\nfor \t  something\v   completely\r\n  different"
    >>> print normalize_ws(s)
    and now for something completely different
    >>>
    """
    lst = s.split()
    s = " ".join(lst)
    return s
    


def escape_html(s):
    """
    Return a copy of string s with HTML codes escaped.

    This is useful when you want HTML tags printed literally, rather than
    interpreted.

    >>> print escape_html("<head>")
    &lt;head&gt;
    >>> print escape_html("&nbsp;")
    &amp;nbsp;
    """
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    return s



def unescape_html(s):
    """
    Return a copy of string s with HTML codes unescaped.

    Replaces HTML entities for ">", "<", and "&" with those characters.

    This is the reverse of escape_html().

    >>> print unescape_html("&lt;head&gt;")
    <head>
    >>> print unescape_html("&amp;nbsp;")
    &nbsp;
    """
    s = s.replace("&gt;", ">")
    s = s.replace("&lt;", "<")
    s = s.replace("&amp;", "&")
    return s



s_copyright_multiyear = "Copyright %s %d-%d by %s."
s_copyright_oneyear = "Copyright %s %d by %s."
def s_copyright(s_owner, s_csym="(C)", end_year=None, start_year=None):
    """
    Return a string with a copyright notice.

    s_owner
        string with copyright owner's name.
    s_csym
        string with copyright symbol. (An HTML entity might be good here.)
    end_year
        last year of the copyright.  Default is the current year.
    start_year
        first year of the copyright.

    If only end_year is specified, only print one year; if both end_year and
    start_year are specified, print a range.

    To localize the entire copyright message into another language, change
    the global variables with the copyright template:
        s_copyright_multiyear: for a year range
        s_copyright_oneyear: for a single year
    """
    if not end_year:
        end_year = time.localtime().tm_year

    if start_year:
        return s_copyright_multiyear % (s_csym, start_year, end_year, s_owner)

    return s_copyright_oneyear % (s_csym, end_year, s_owner)



def create_guid(tf, domain_name, uri=""):
    """
    Create globally unique ID using Mark Pilgrim's algorithm.

    Algorithm taken from here:
    http://diveintomark.org/archives/2004/05/28/howto-atom-id
    """

    tup = time.localtime(tf)

    # ymd (year-month-day) example: 2003-12-13
    ymd = time.strftime("%Y-%m-%d", tup)

    if uri == "":
        # mush (all mushed together) example: 20031213083000
        mush = time.strftime("%Y%m%d%H%M%S", tup)
        uri = "/weblog/" + mush

    s = "tag:%s,%s:%s" % (domain_name, ymd, uri)

    s = s.replace("#", "/")

    return s



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

    result = entities_to_ws("nudge&nbsp;nudge&nbsp;say no more")
    correct = "nudge nudge say no more"
    self_test("entites_to_ws() test 0")

    s = "and    now\n\n\nfor \t  something\v   completely\r\n  different"
    result = normalize_ws(s)
    correct = "and now for something completely different"
    self_test("normalize_ws() test 0")

    result = s_copyright("J. Random Guy", "(C)", 1999, 1990)
    correct = "Copyright (C) 1990-1999 by J. Random Guy."
    self_test("s_copyright() test 0")

    s = """<body><a href="http://www.example.com/">Cool&nbsp;example</a>"""
    result = escape_html(s)
    correct = """&lt;body&gt;&lt;a href="http://www.example.com/"&gt;Cool&amp;nbsp;example&lt;/a&gt;"""
    self_test("escape_html() test 0")

    s = """&lt;body&gt;&lt;a href="http://www.example.com/"&gt;Cool&amp;nbsp;example&lt;/a&gt;"""
    correct = """<body><a href="http://www.example.com/">Cool&nbsp;example</a>"""
    result = unescape_html(s)
    self_test("unescape_html() test 0")

    correct = """<body><a href="http://www.example.com/">Cool&nbsp;example</a>"""
    result = unescape_html(escape_html(correct))
    self_test("escape_html() test 1")

    tf = 1141607495
    result = create_guid(tf, "www.example.com")
    correct = "tag:www.example.com,2006-03-05:/weblog/20060305171135"
    self_test("create_guid() test 0")



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
