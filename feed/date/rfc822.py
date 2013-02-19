# feed.date.rfc822 -- conversion functions for RFC 822 timestamps

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
Conversion functions to handle RFC 822 timestamp format.

These functions actually handle the extended RFC 822 format used in
RSS 2.0; four-digit years are permitted (and are the default).

"tf" is short for "time float", a float being used as a time value
(seconds since the epoch).  Always store tf values as UTC values, not
local time values.  A TF of 0.0 means the epoch in UTC.


Please send questions, comments, and bug reports to: pyfeed@langri.com

"""



import re
import time

from calendar import timegm
from feed.date.tools import tf_utc
from feed.date.tools import parse_time_offset



module_name = "feed.date.rfc822"
module_version = "0.7.4"
module_banner = "%s version %s" % (module_name, module_version)



# NOTES ON TIME CONVERSIONS
#
# Most of the time, the tf values will be UTC (aka GMT or Zulu time)
# values.  Timestamp strings come complete with time offset specifiers,
# so when you convert a timestamp to a tf, the time offset will cause an
# adjustment to the tf to make it a UTC value.
#
# Then, we use Python's time conversion functions that work on UTC
# values, so we don't get any adjustments for local time.
#
# Finally, when actually formatting the timestamp string for output, we
# calculate the adjustment for the offset value.  If you print a
# timestamp value with a "Z" offset value, you get no adjustment; if you
# use "-0800", you get an 8 hour adjustment; and so on.
#
# These two timestamps both represent the same time:
#
# Wed, 31 Dec 1969 16:00:01 -0800
# Thu, 01 Jan 1970 00:00:01 GMT
#
# They are both a tf of 1.0.



def cleanup_time_offset(time_offset):
    """
    Given a time offset, return a time offset in a consistent format.

    If the offset is for UTC, always return a "GMT".

    Otherwise, return offset in this format: "(+|-)hh:mm"
    """
    secs = parse_time_offset(time_offset)

    if secs == 0:
        return "GMT"

    return s_time_offset_from_secs(secs)



_s_format_rfc822 = "%a, %d %b %Y %H:%M:%S"

def timestamp_from_tf(tf, time_offset=None):
    """
    Take a tf and return a timestamp string.

    Arguments:
        tf
            a floating-point UTC time value, seconds since the epoch.
        time_offset
            a string specifying an offset from UTC.  Examples:
            z or Z -- offset is 0 ("Zulu" time, UTC, aka GMT)
            PST -- 8 hours earlier than UTC (Pacific Standard Time)
            -0800 -- 8 hours earlier than UTC
            "" -- empty string is technically not legal, but may work

    Notes:
        Returned string is extended RFC 822 with 4-digit year.

        Example: "Tue, 10 Jun 2003 09:41:01 GMT"
    """

    if tf is None:
        return ""

    if time_offset is None:
        time_offset = s_offset_default


    # converting from tf to timestamp so *add* time offset
    tf += parse_time_offset(time_offset)

    try:
        s = time.strftime(_s_format_rfc822, time.gmtime(tf))
    except ValueError:
        return "<!-- date out of range; tf is %.1f -->" % tf

    return "%s %s" % (s, time_offset)



# date recognition pattern

# This is *extremely* permissive as to what it accepts!
# Long form regular expression with lots of comments.

_pat_rfc822 = re.compile(r"""
(\d\d?)  # match one or two digits: the date
\W*  # any non-alpha, or even nothing (example: 06Jan)
(\w\w\w)\w*  # match multiple alpha (example: Jan)
\s*  # any whitespace, or even nothing (example: Jan2006)
(\d\d|\d\d\d\d)  # two or four digits: the year
\D+  # any non-digit, at least one
(\d\d)\D(\d\d)\D(\d\d)  # hours, mins, secs, separated by any non-digit
([.,]\d+)?  # optional fractional seconds (American decimal or Euro ",")
\s*  # optional whitespace
(\S+)  # at least one non-whitespace: the timezone offset
""", re.X)

_s_date_parse_format = "%d %b %Y %H:%M:%S"

def tf_from_timestamp(s_timestamp):
    """
    Take a RFC 882 timestamp string and return a time float value.

    timestamp example: "Tue, 10 Jun 2003 09:41:01 GMT"
    timestamp example: "10 Jun 2003 01:41:01 -0800"

    Note: according to RFC 822, weekday is optional.  This function
    ignores the weekday value if present.  The weekday can't change the
    date anyway.
    """

    # We want to be able to accept inputs that might be a little sloppy.
    #
    # strptime() has a rather fragile parser.  So, we will first clean
    # up and reformat the input string so that it is in exactly the
    # correct format to make strptime() happy.

    s_timestamp = s_timestamp.lstrip().rstrip()

    try:
        m = _pat_rfc822.search(s_timestamp)

        s_mday = m.group(1)
        s_mon = m.group(2)
        s_year = m.group(3)
        s_hour = m.group(4)
        s_min = m.group(5)
        s_sec = m.group(6)
        s_zone_offset = m.group(8)

        # convert two-digit year to four digits
        if len(s_year) == 2:
            y = int(s_year)
            if 32 <= y <= 99:
                s_year = "19" + s_year
            else:
                s_year = "20" + s_year

        # build string in perfect format
        s_date = "%s %s %s %s:%s:%s" % \
            (s_mday, s_mon, s_year, s_hour, s_min, s_sec)
        tup = time.strptime(s_date, _s_date_parse_format)

        # calendar.timegm() is like time.mktime() but doesn't adjust
        # from local to UTC; it just converts to a tf.
        tf = timegm(tup)

        # Use time offset from timestamp to adjust from UTC to correct.
        # If s_zone_offset is "GMT", "UTC", or "Z", offset is 0.

        # converting from timestamp to tf so *subtract* time offset
        tf -= parse_time_offset(s_zone_offset)
    except:
        return None

    return float(tf)



def s_time_offset_from_secs(secs):
    """
    Return a string with offset from UTC in RFC 882 format, from secs.

    """

    if secs > 0:
        sign = "+"
    else:
        sign = "-"
        secs = abs(secs)

    offset_hour = secs // (60 * 60)
    offset_min = (secs // 60) % 60
    return "%s%02d%02d" % (sign, offset_hour, offset_min)


def local_time_offset():
    """
    Return a string with local offset from UTC in RFC 882 format.
    """

    # If tf is set to local time in seconds since the epoch, then...
    # ...offset is the value you add to tf to get UTC.  This is the
    # reverse of time.timezone or time.altzone.

    if time.daylight:
        secs_offset = -(time.altzone)
    else:
        secs_offset = -(time.timezone)

    return s_time_offset_from_secs(secs_offset)

s_offset_local = local_time_offset()

offset_default = 0
s_offset_default = ""

def set_default_time_offset(s):
    global offset_default
    global s_offset_default
    offset_default = parse_time_offset(s)
    s_offset_default = s

set_default_time_offset(s_offset_local)



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

    # The default is to make time stamps in local time with appropriate
    # offset; for the tests, we want a "GMT" offset default instead.
    set_default_time_offset("GMT")


    # Test: convert current time into a timestamp string and back

    tf_now = tf_utc()
    # timestamp format does not allow fractional seconds
    correct = float(int(tf_now))  # truncate any fractional seconds
    s = timestamp_from_tf(correct)

    result = tf_from_timestamp(s)
    self_test("convert tf to timestamp and back 0")


    # Test: convert a timestamp string to a time value and back

    correct = "Tue, 10 Jun 2003 04:00:00 GMT"
    tf = tf_from_timestamp(correct)
    result = timestamp_from_tf(tf)
    self_test("convert timestamp to tf and back 0")


    # Test: convert a timestamp string to a time value and back

    s_test = "Tue, 10 Jun 2003 00:00:00-0800"
    tf = tf_from_timestamp(s_test)
    result = timestamp_from_tf(tf)
    correct = "Tue, 10 Jun 2003 08:00:00 GMT"
    self_test("convert timestamp to tf and back 1")


    # Test: convert a timestamp string to a time value and back

    correct = "Wed, 08 Mar 2006 13:30:56 PST"
    tf = tf_from_timestamp(correct)
    result = timestamp_from_tf(tf, "PST")
    self_test("convert timestamp to tf and back 2")


    # Test: convert a timestamp string to a time value and back

    correct = "Wed, 14 Jun 2006 13:30:56 PDT"
    tf = tf_from_timestamp(correct)
    result = timestamp_from_tf(tf, "PDT")
    self_test("convert timestamp to tf and back 3")


    # Test: convert a timestamp string to a time value and back

    correct = "Wed, 07 Jun 2006 13:30:56 PDT"
    s_test = "Wed,7 Jun 06 13:30:56 PDT"
    tf = tf_from_timestamp(s_test)
    result = timestamp_from_tf(tf, "PDT")
    self_test("convert timestamp to tf and back 4")


    # Test: convert a timestamp string to a time value and back

    correct = "Fri, 08 Mar 1996 13:30:56 PDT"
    s_test = "8 Mar 96 13:30:56 PDT"
    tf = tf_from_timestamp(s_test)
    result = timestamp_from_tf(tf, "PDT")
    self_test("convert timestamp to tf and back 5")


    # Test: convert a timestamp string to a time value and back

    correct = "Fri, 08 Mar 1996 13:30:56 PDT"
    s_test = "8 Mar 96 13:30:56.00 PDT"
    tf = tf_from_timestamp(s_test)
    result = timestamp_from_tf(tf, "PDT")
    self_test("convert timestamp to tf and back 6: fractional seconds")


    # Test: convert a timestamp string to a time value and back

    correct = "Fri, 08 Mar 1996 13:30:56 PDT"
    s_test = "8   Mar\t96\v13:30:56.00PDT"
    tf = tf_from_timestamp(s_test)
    result = timestamp_from_tf(tf, "PDT")
    self_test("convert timestamp to tf and back 7: bizarre whitespace")


    # Test: convert a tf to a a timestamp string

    correct = "Fri, 07 Apr 2006 11:38:34 -0700"
    result = timestamp_from_tf(1144435114, "-0700")
    self_test("convert tf to timestamp 0")



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
