''' validate-keyml.py -- validate an XML file against a KeyML DTD ''' 

from lxml import etree
from lxml.etree import XMLSyntaxError
import sys, os

dtdfile   = sys.argv[1]
directory = sys.argv[2]

okay = True

def error(t, s):
    global okay
    print >> sys.stderr, path
    print >> sys.stderr, '%s: %s' % (t, s)
    print >> sys.stderr
    okay = False
    
with file(dtdfile) as f: dtd = etree.DTD(f)

for filename in os.listdir(directory):
    if filename[0] in '0123456789':
        path = directory + '/' + filename
        with file(path) as f:
            text = f.read()
            try:
                doc = etree.XML(text, etree.XMLParser(resolve_entities=False))
                if not dtd.validate(doc):
                    error('KeyML DTD', `dtd.error_log.filter_from_errors()`)
            except XMLSyntaxError, e:
                error('XML', str(e))


if not okay:
    sys.exit(1)
