''' validate-keyml.py -- ''' 

from lxml import etree
import sys, os

with file('keyml.dtd') as f:
    dtd = etree.DTD(f)

directory = sys.argv[1]

okay = True

for filename in os.listdir(directory):
    if filename[0] in '0123456789':
        path = directory + '/' + filename
        with file(path) as f:
            try:
                doc = etree.XML(f.read(), etree.XMLParser(dtd_validation=True))
                if not dtd.validate(doc):
                    print >> sys.stderr, path
                    print >> sys.stderr, dtd.error_log.filter_from_errors()[0]
                    print >> sys.stderr
                    okay = False
            except etree.XMLSyntaxError, e:
                print >> sys.stderr, path
                print >> sys.stderr, str(e)
                print >> sys.stderr
                okay = False

if not okay:
    sys.exit(1)
