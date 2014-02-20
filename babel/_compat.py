import sys

PY2 = sys.version_info[0] == 2

_identity = lambda x: x


if not PY2:
    text_type = str
    string_types = (str,)
    integer_types = (int, )
    chr = chr

    text_to_native = lambda s, enc: s

    iterkeys = lambda d: iter(list(d.keys()))
    itervalues = lambda d: iter(list(d.values()))
    iteritems = lambda d: iter(list(d.items()))

    from io import StringIO, BytesIO
    import pickle

    izip = zip
    imap = map
    range_type = range

    cmp = lambda a, b: (a > b) - (a < b)

else:
    text_type = str
    string_types = (str, str)
    integer_types = (int, int)

    text_to_native = lambda s, enc: s.encode(enc)
    chr = chr

    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())

    from io import StringIO as BytesIO
    from io import StringIO
    import pickle as pickle

    
    range_type = xrange

    cmp = cmp


number_types = integer_types + (float,)
