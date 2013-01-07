#!c:\\python27\python.exe
# -*- coding: utf-8 -*-
#
#  main.py
#
#  Copyright 2012 Arthur Gerkis <ax330d@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import sys
import random
import string
import codecs
import getopt
import re

# Chunks in this array will be reused both for text and regexp generation
textArray = []

# Python aliases for encodings
# Firefox html parser doesn't like u32, utf32
# utf7 breaks most of regexps, dbcs returns ???
pythonEncs = ["utf",  "u16",  "utf8", "utf16", "utf8_ucs4", "utf8_ucs2"]

smallCrapNums = [
    -1, 0, 1, 1, 2, 0,
    1.01, 1000, 2, 99.9,
    # https://bugzilla.mozilla.org/show_bug.cgi?id=782141
    256,
    # Secure Coding in C and C++, p158
    8, -127, -128, 127, 255
];

bigCrapNums = [
    1e6, -1e6, 1e-6,
    100000000,
    # https://bugzilla.mozilla.org/show_bug.cgi?id=782141
    2147483392, -2147483648, 2147483648,
    # https://bugzilla.mozilla.org/show_bug.cgi?id=265084
    2147483646.5, -2147483647.5, 2147483520,
    # https://bugzilla.mozilla.org/show_bug.cgi?id=748257
    10000000, -10000000,
    # https://bugzilla.mozilla.org/show_bug.cgi?id=183986
    1073741952, 65535,
    # https://bugzilla.mozilla.org/show_bug.cgi?id=552412
    17895698,
    # Secure Coding in C and C++, p158
    -32767, -32768,
    32767, 4294967295, 2147483647,
    3507521020
];

crapNumbers = [];
crapNumbers.extend(smallCrapNums);
crapNumbers.extend(bigCrapNums);


def R(num):
    if num <= 0: 
        return 0
    random.seed()
    return random.randint(0, num-1)


def Rc():
    return oneOf(crapNumbers)


def oneOf(ary):
    return ary[ R(len(ary)) ]


def oneOfGroups(ary, joiner):
    buff = []
    for item in ary:
        buff.append(oneOf(item))
        continue

    return joiner.join(buff)


def escapeJSRegexp(text):
    text = text.replace('+', "\\+")
    text = text.replace('.', "\\.")
    text = text.replace('*', "\\*")
    text = text.replace('|', "\\|")
    text = text.replace('^', "\\^")
    text = text.replace('?', "\\?")
    return text


def escapeJS(text):
    text = text.replace("'", "\\'")
    text = text.replace('"', '\\"')
    text = text.replace("\n", "")
    text = text.replace("\t", '')
    return text


def writeSample(sampleName, sample, enc='utf8'):
    try:
        sample += u"<!-- %s -->" % enc
        with codecs.open(sampleName, "w", encoding=enc) as f:
            f.write(sample)
        sys.stdout.write("Writing file %s  \r" % (sampleName) )
        f.close()
    except:
        print "Error:", sys.exc_info()[0]
        raise
    return


def generateRegex(maxRounds=10):
    """ 
    Simple and ugly regular expression generator. Creates correct as well 
    deliberately incorrect regexps. References for generator: 
    - http://codereview.chromium.org/141042/patch/6/1003
    - https://bugzilla.mozilla.org/show_bug.cgi?id=346090
    - https://bugzilla.mozilla.org/show_bug.cgi?id=346794
    - http://list.opera.com/pipermail/opera-users/2003-February/017073.html
    - https://bugzilla.mozilla.org/show_bug.cgi?id=288688
    - https://bugzilla.mozilla.org/show_bug.cgi?id=684815

    - https://developer.mozilla.org/en-US/docs/JavaScript/Reference/Global_Objects/RegExp
    - https://developer.mozilla.org/en-US/docs/JavaScript/Guide/Regular_Expressions
    - http://www.w3schools.com/jsref/jsref_obj_regexp.asp
    """

    chars = ['+', '.', '*', '|', '^', '?', '*?', '+?']
    cond = ['?:', '?=', '?!']
    UC = map(chr, range(65, 91))
    LC = map(chr, range(97, 123))
    NC = map(chr, range(45, 65))
    syms = [
        'b', 'B', 'd', 'D', 'f', 'n', 'r', 's', 'S', 't', 'v', 'w', 'W',
        "%s" % Rc(), generateUnicode(), 'c%s' % oneOf(UC)
    ]

    regex = ''
    openPar = False
    openSqBracket = False
    emptyPar = True
    startChar = False

    brCount = 0
    sqbrCount = 0

    if R(2):
        regex += '^'

    if not R(2):
        for ii in xrange(0, R(15)):
            regex += generateText(2)
            startChar = True
        emptyPar = False

    for it in xrange(0, R(maxRounds)+1):

        if not R(2):
            if not R(2):
                for ii in xrange(0, R(15)):
                    regex += generateText(2)
            else:
                if startChar:
                    regex += oneOf(chars)
            emptyPar = False

        if not R(5) and not openSqBracket:
            regex += '['
            openSqBracket = True
            sqbrCount += 1
            for xit in xrange(0, R(2)+1):
                if not R(4): regex += '\\' + oneOf(syms)
                if not R(5): regex += "%s-%s" % ( oneOf(UC), oneOf(UC) )
                if not R(5): regex += "%s-%s" % ( oneOf(LC), oneOf(LC) )
                if not R(5): regex += "%s-%s" % ( oneOf(NC), oneOf(NC) )
                if not R(3): regex += "%s-%s" % ( generateChar(), generateChar() )
                if not R(3): regex += '%s-%s' % ( Rc(), Rc() )
                regex += ','
            emptyPar = False

        if not R(5) and openSqBracket:
            regex += ']'
            openSqBracket = False
            sqbrCount -= 1
            r = R(3)
            if r == 0: regex += "{%s}" % Rc()
            if r == 1: regex += "{%s,}" % Rc()
            if r == 2: regex += "{%s,%s}" % ( Rc(), Rc() )
            emptyPar = False

        if not R(3) and not openSqBracket:
            regex += '('
            openPar = True
            emptyPar = True
            brCount += 1

            if not R(3):
                regex += oneOf(cond)

        if not R(4) and openPar and not emptyPar and not openSqBracket:
            regex += ')'
            openPar = False
            brCount -= 1
            r = R(3)
            if r == 0: regex += "{%s}" % Rc()
            if r == 1: regex += "{%s,}" % Rc()
            if r == 2: regex += "{%s,%s}" % ( Rc(), Rc() )


    # Keep brackets balanced
    if brCount > 0:
        for it in xrange(0, brCount):
            regex += ')'

    if sqbrCount > 0:
        for it in xrange(0, sqbrCount):
            regex += ']'

    if R(2):
        regex += '$'

    return regex


# http://www.unicode.org/Public/UNIDATA/Blocks.txt
def encodingRanges():
    a = {
        '0001..007F' : 'Basic Latin',
        '0080..00FF' : 'Latin-1 Supplement',
        '0100..017F' : 'Latin Extended-A',
        '0180..024F' : 'Latin Extended-B',
        '0250..02AF' : 'IPA Extensions',
        '02B0..02FF' : 'Spacing Modifier Letters',
        '0300..036F' : 'Combining Diacritical Marks',
        '0370..03FF' : 'Greek and Coptic',
        '0400..04FF' : 'Cyrillic',
        '0500..052F' : 'Cyrillic Supplement',
        '0530..058F' : 'Armenian',
        '0590..05FF' : 'Hebrew',
        '0600..06FF' : 'Arabic',
        '0700..074F' : 'Syriac',
        '0750..077F' : 'Arabic Supplement',
        '0780..07BF' : 'Thaana',
        '07C0..07FF' : 'NKo',
        '0800..083F' : 'Samaritan',
        '0840..085F' : 'Mandaic',
        '08A0..08FF' : 'Arabic Extended-A',
        '0900..097F' : 'Devanagari',
        '0980..09FF' : 'Bengali',
        '0A00..0A7F' : 'Gurmukhi',
        '0A80..0AFF' : 'Gujarati',
        '0B00..0B7F' : 'Oriya',
        '0B80..0BFF' : 'Tamil',
        '0C00..0C7F' : 'Telugu',
        '0C80..0CFF' : 'Kannada',
        '0D00..0D7F' : 'Malayalam',
        '0D80..0DFF' : 'Sinhala',
        '0E00..0E7F' : 'Thai',
        '0E80..0EFF' : 'Lao',
        '0F00..0FFF' : 'Tibetan',
        '1000..109F' : 'Myanmar',
        '10A0..10FF' : 'Georgian',
        '1100..11FF' : 'Hangul Jamo',
        '1200..137F' : 'Ethiopic',
        '1380..139F' : 'Ethiopic Supplement',
        '13A0..13FF' : 'Cherokee',
        '1400..167F' : 'Unified Canadian Aboriginal Syllabics',
        '1680..169F' : 'Ogham',
        '16A0..16FF' : 'Runic',
        '1700..171F' : 'Tagalog',
        '1720..173F' : 'Hanunoo',
        '1740..175F' : 'Buhid',
        '1760..177F' : 'Tagbanwa',
        '1780..17FF' : 'Khmer',
        '1800..18AF' : 'Mongolian',
        '18B0..18FF' : 'Unified Canadian Aboriginal Syllabics Extended',
        '1900..194F' : 'Limbu',
        '1950..197F' : 'Tai Le',
        '1980..19DF' : 'New Tai Lue',
        '19E0..19FF' : 'Khmer Symbols',
        '1A00..1A1F' : 'Buginese',
        '1A20..1AAF' : 'Tai Tham',
        '1B00..1B7F' : 'Balinese',
        '1B80..1BBF' : 'Sundanese',
        '1BC0..1BFF' : 'Batak',
        '1C00..1C4F' : 'Lepcha',
        '1C50..1C7F' : 'Ol Chiki',
        '1CC0..1CCF' : 'Sundanese Supplement',
        '1CD0..1CFF' : 'Vedic Extensions',
        '1D00..1D7F' : 'Phonetic Extensions',
        '1D80..1DBF' : 'Phonetic Extensions Supplement',
        '1DC0..1DFF' : 'Combining Diacritical Marks Supplement',
        '1E00..1EFF' : 'Latin Extended Additional',
        '1F00..1FFF' : 'Greek Extended',
        '2000..206F' : 'General Punctuation',
        '2070..209F' : 'Superscripts and Subscripts',
        '20A0..20CF' : 'Currency Symbols',
        '20D0..20FF' : 'Combining Diacritical Marks for Symbols',
        '2100..214F' : 'Letterlike Symbols',
        '2150..218F' : 'Number Forms',
        '2190..21FF' : 'Arrows',
        '2200..22FF' : 'Mathematical Operators',
        '2300..23FF' : 'Miscellaneous Technical',
        '2400..243F' : 'Control Pictures',
        '2440..245F' : 'Optical Character Recognition',
        '2460..24FF' : 'Enclosed Alphanumerics',
        '2500..257F' : 'Box Drawing',
        '2580..259F' : 'Block Elements',
        '25A0..25FF' : 'Geometric Shapes',
        '2600..26FF' : 'Miscellaneous Symbols',
        '2700..27BF' : 'Dingbats',
        '27C0..27EF' : 'Miscellaneous Mathematical Symbols-A',
        '27F0..27FF' : 'Supplemental Arrows-A',
        '2800..28FF' : 'Braille Patterns',
        '2900..297F' : 'Supplemental Arrows-B',
        '2980..29FF' : 'Miscellaneous Mathematical Symbols-B',
        '2A00..2AFF' : 'Supplemental Mathematical Operators',
        '2B00..2BFF' : 'Miscellaneous Symbols and Arrows',
        '2C00..2C5F' : 'Glagolitic',
        '2C60..2C7F' : 'Latin Extended-C',
        '2C80..2CFF' : 'Coptic',
        '2D00..2D2F' : 'Georgian Supplement',
        '2D30..2D7F' : 'Tifinagh',
        '2D80..2DDF' : 'Ethiopic Extended',
        '2DE0..2DFF' : 'Cyrillic Extended-A',
        '2E00..2E7F' : 'Supplemental Punctuation',
        '2E80..2EFF' : 'CJK Radicals Supplement',
        '2F00..2FDF' : 'Kangxi Radicals',
        '2FF0..2FFF' : 'Ideographic Description Characters',
        '3000..303F' : 'CJK Symbols and Punctuation',
        '3040..309F' : 'Hiragana',
        '30A0..30FF' : 'Katakana',
        '3100..312F' : 'Bopomofo',
        '3130..318F' : 'Hangul Compatibility Jamo',
        '3190..319F' : 'Kanbun',
        '31A0..31BF' : 'Bopomofo Extended',
        '31C0..31EF' : 'CJK Strokes',
        '31F0..31FF' : 'Katakana Phonetic Extensions',
        '3200..32FF' : 'Enclosed CJK Letters and Months',
        '3300..33FF' : 'CJK Compatibility',
        '3400..4DBF' : 'CJK Unified Ideographs Extension A',
        '4DC0..4DFF' : 'Yijing Hexagram Symbols',
        '4E00..9FFF' : 'CJK Unified Ideographs',
        'A000..A48F' : 'Yi Syllables',
        'A490..A4CF' : 'Yi Radicals',
        'A4D0..A4FF' : 'Lisu',
        'A500..A63F' : 'Vai',
        'A640..A69F' : 'Cyrillic Extended-B',
        'A6A0..A6FF' : 'Bamum',
        'A700..A71F' : 'Modifier Tone Letters',
        'A720..A7FF' : 'Latin Extended-D',
        'A800..A82F' : 'Syloti Nagri',
        'A830..A83F' : 'Common Indic Number Forms',
        'A840..A87F' : 'Phags-pa',
        'A880..A8DF' : 'Saurashtra',
        'A8E0..A8FF' : 'Devanagari Extended',
        'A900..A92F' : 'Kayah Li',
        'A930..A95F' : 'Rejang',
        'A960..A97F' : 'Hangul Jamo Extended-A',
        'A980..A9DF' : 'Javanese',
        'AA00..AA5F' : 'Cham',
        'AA60..AA7F' : 'Myanmar Extended-A',
        'AA80..AADF' : 'Tai Viet',
        'AAE0..AAFF' : 'Meetei Mayek Extensions',
        'AB00..AB2F' : 'Ethiopic Extended-A',
        'ABC0..ABFF' : 'Meetei Mayek',
        'AC00..D7AF' : 'Hangul Syllables',
        'D7B0..D7FF' : 'Hangul Jamo Extended-B',
        'D800..DB7F' : 'High Surrogates',
        'DB80..DBFF' : 'High Private Use Surrogates',
        'DC00..DFFF' : 'Low Surrogates',
        'E000..F8FF' : 'Private Use Area',
        'F900..FAFF' : 'CJK Compatibility Ideographs',
        'FB00..FB4F' : 'Alphabetic Presentation Forms',
        'FB50..FDFF' : 'Arabic Presentation Forms-A',
        'FE00..FE0F' : 'Variation Selectors',
        'FE10..FE1F' : 'Vertical Forms',
        'FE20..FE2F' : 'Combining Half Marks',
        'FE30..FE4F' : 'CJK Compatibility Forms',
        'FE50..FE6F' : 'Small Form Variants',
        'FE70..FEFF' : 'Arabic Presentation Forms-B',
        'FF00..FFEF' : 'Halfwidth and Fullwidth Forms',
        'FFF0..FFFF' : 'Specials'
        # For more ranges "wide" Python build is required
    }

    index = oneOf(a.keys() )
    return [index, a[index]]


def generateUnicode():

    (key, value) = encodingRanges()
    (rangeStart, rangeEnd) = key.split('..')
    rangeStart = int(rangeStart, 16)
    rangeEnd = int(rangeEnd, 16)
    
    return "u%04x" % random.choice(xrange(rangeStart, rangeEnd))


def generateChar():
    """ 
    Generate single character from Unicode ranges.
    """ 
    randChar = oneOf(textArray)
    try:
        char = escapeJSRegexp(unichr(randChar))
    except:
        char = genUnicodeHexHTML()
        pass

    char = escapeJS(char)
    return char


def genUnicodeHexHTML():
    a = "%04x" % R(65536 + 1)
    return "&#x%s;" % a


def generateText(length=64):

    buff = u""

    for it in xrange(0, R(length)):
        c = oneOf(textArray)
        try:
            buff += escapeJSRegexp(unichr(c))
        except:
            buff += genUnicodeHexHTML()
            pass

        if len(buff) >= length:
            break

    buff = escapeJS(buff)
    return buff


def initTextArray():
    """ 
    Create an array of character chunks to reuse them later.
    """
    global textArray

    (key, value) = encodingRanges()
    (rangeStart, rangeEnd) = key.split('..')
    rangeStart = int(rangeStart, 16)
    rangeEnd = int(rangeEnd, 16)
    
    textArray = []
    for item in xrange(0, R(10) + 3):
        tmp = random.choice(xrange(rangeStart, rangeEnd))
        if not R(3):
            tmp += random.choice(xrange(rangeStart, rangeEnd))
        if not R(3):
            tmp += random.choice(xrange(rangeStart, rangeEnd))
        textArray.append(tmp)


def generateHTML(it, regexPattern, regexDatabase, regexJavascript):
    """
    Generate HTML out of template containing at least one of chosen fuzzing 
    options - patterns, JavaScript, database.
    """

    nextFilename = "regex-%d.html" % (it+1)
    HTML = u""

    HTML += """
<!DOCTYPE html>
<html>
    <head>
        <title>Regular expression fuzzer</title>
        <meta http-equiv="refresh" content="1;URL=%s">
        <script>
            var h = window.top.window.location.href.split('#');
            h[1] = " %s";
            window.top.window.location.href = h.join('#');
            window.onload = function() {
                setTimeout("location.href='%s'", 20);
            }
        </script>
    </head>
    <body>
        <img src="../log.php?req=regex-%d.html"/>
    """ % (nextFilename, "regex-%d.html" % it, nextFilename, it)

    if regexPattern == True:
        HTML += """
        <form>
        <input type="text" pattern="%s" id="i1" value=""/><br/>
        <input type="text" pattern="%s" id="i2" value=""/><br/>
        <input type="text" pattern="%s" id="i3" value=""/><br/>
        <input type="submit" id="button" />
        </form>
        """ % (escapeJS(generateRegex(3)), escapeJS(generateRegex(3)), escapeJS(generateRegex(4)))
        
        HTML += """
        <script>
            document.getElementById("i1").value = "%s";
            document.getElementById("i2").value = "%s";
            document.getElementById("i3").value = "%s";
            document.getElementById("button").click();
        </script>
        """ % (escapeJS(generateText()), escapeJS(generateText()), escapeJS(generateText()))


    if regexDatabase == True:
        HTML += """
        <script>
            try {
                var db = openDatabase('test_db', '1.0', 'Test database', 1 * 1024);

                db.transaction(function(tx) {
                    tx.executeSql('CREATE TABLE IF NOT EXISTS test_table (text)');
                    tx.executeSql('INSERT INTO test_table VALUES ("%s")');
                });

                db.transaction(function(tx) {
                    tx.executeSql('SELECT * FROM test_table WHERE text REGEXP "%s"');
                });
            } catch(e) {}

            try {
                db.transaction(function(tx) {
                    tx.executeSql('DROP TABLE test_table');
                });
            } catch(e) {}
        </script>
        """ % (escapeJS(generateText(10)), escapeJS(generateRegex()))


    if regexJavascript == True:
        HTML += """
        <script>
            var re;
            try {
                re = new RegExp("%s", "%s");
            } catch(e) {
                //alert(e)
            }  

            re.lastIndex = %s;
            var rSrc = re.source;
            re.compile();
            retTest = re.test("%s");
            retExec = re.exec("%s");
            var rstr = re.toString();

            try {
                tr = "%s";
                "%s".replace(tr, "%s");
                "%s".replace(tr, "$&");
                "%s".replace(tr, "$`");
                "%s".replace(tr, "$'");
                "%s".replace(tr, "$%d");
                eval(rstr);
            } catch(e) {
            }
        </script>
        """ % ( escapeJS(generateRegex(5)), oneOfGroups(['i', 'g', 'm'], ''), 
                Rc(), 
                escapeJS(generateText()), escapeJS(generateText()),
                
                escapeJS(generateRegex(4)),
                escapeJS(generateText()), escapeJS(generateText()),
                escapeJS(generateText()),
                escapeJS(generateText()),
                escapeJS(generateText()),
                escapeJS(generateText()), Rc()
            )

    HTML += """
    </body>
</html>
    """
    
    return HTML


def help():

    print """
    Options:
        -n      amount of samples to generate
        -p      fuzz pattern attibute for input tag
        -d      fuzz database (if available for browser)
        -j      fuzz JavaScript regex
        -e      preferred encoding

    At least one of fuzzing options (p,d,j) must be specified.
    """


def main(argv):

    regexPattern = False
    regexDatabase = False
    regexJavascript = False
    prefEnc = None
    amount = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], "n:pdje:")
    except getopt.GetoptError:
        help()

    for opt, arg in opts:
        if opt == "-n":
            amount = int(arg)
        elif opt == "-p":
            regexPattern = True
        elif opt == "-d":
            regexDatabase = True
        elif opt == "-j":
            regexJavascript = True
        elif opt == "-e":
            prefEnc = arg

    if amount == 0:
        help()
        sys.exit(1)

    if regexPattern == False and regexDatabase == False and regexJavascript == False:
        help()
        sys.exit(1)

    for it in xrange(0, amount):

        initTextArray()

        if not prefEnc:
            prefEnc = oneOf(pythonEncs)
        writeSample("samples/regex-%d.html" % \
            it, 
            generateHTML(it, regexPattern, regexDatabase, regexJavascript),
            prefEnc
        )


if __name__ == '__main__':
    main(sys.argv)
