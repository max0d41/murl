import re

from urllib import quote, quote_plus
from urlparse import parse_qs


all_url_regex_1_str = r"(?P<url>(?P<scheme>\w[\w\d\-]+?):((?P<scheme_delim>//)?((?P<username>[^\@\/\s\"\'\:]*(@[^\@\/\s\"\'\:]*)?)(:(?P<password>[^\@\/\s\"\']*))?@)?(?P<host>[^\?\/\:\s\"\']*)(:(?P<port>\d+))?(?P<path>/[^\s\?\#\"\']*)?(\?(?P<query>[^\s\#\"\']*))?(\#(?P<fragment>[^\s\"\']*))?)?)\s*"
all_url_regex_2_str = r"(?P<url>(?P<scheme>\w[\w\d\-]+?):((?P<scheme_delim>//)?((?P<username>[^\@\/\s\:]*(@[^\@\/\s\:]*)?)(:(?P<password>[^\@\/\s]*))?@)?(?P<host>[^\?\/\:\s]*)(:(?P<port>\d+))?(?P<path>/[^\s\?\#]*)?(\?(?P<query>[^\s\#]*))?(\#(?P<fragment>[^\s]*))?)?)\s*"
all_url_regex_1 = re.compile(all_url_regex_1_str)
all_url_regex_2 = re.compile(all_url_regex_2_str)


class Url(object):
    scheme = None
    scheme_delim = '://'
    username = None
    password = None
    host = None
    port = None
    path = None
    path_prefix = ''
    query = None
    query_string = None
    fragment = None

    __serialize__ = ('scheme', 'scheme_delim', 'username', 'password', 'host', 'port', 'path', 'path_prefix', 'query', 'query_string', 'fragment')

    def __init__(self, url, fulltext=True):
        """query_string is ignored on to_string function
        """
        self.original_url = url
        if fulltext:
            m = all_url_regex_1.match(url)
        else:
            m = all_url_regex_2.match(url)
        if m is None:
            raise ValueError('failed matching url {}'.format(url))
        for key, value in m.groupdict().iteritems():
            setattr(self, key, value)
        if self.port is not None:
            self.port = int(self.port)
        # win32 path fix
        if self.path is not None and re.match('^/[a-zA-Z]:\\\\', self.path):
            self.path = self.path[1:]
            self.path_prefix = '/'
        if self.query is not None:
            self.query_string = self.query
            self.query = {k: v[0] for k, v in parse_qs(self.query, True).iteritems()}
        else:
            self.query_string = None
            self.query = dict()

    def to_string(self, hide_password=False):
        result = ''
        if self.scheme is not None:
            result += self.scheme + ':' + (self.scheme_delim or '')
        if self.username is not None or self.password is not None:
            result += (self.username or '') + ((':' + ('***' if hide_password else self.password)) if self.password else '') + '@'
        if self.host is not None:
            result += self.host
            if self.port is not None:
                result += ':' + str(self.port)
        if self.path is not None:
            result += quote(self.path_prefix + self.path)
        if self.query:
            query = list()
            for key, value in self.query.iteritems():
                if value:
                    query.append('%s=%s' % (quote_plus(key), quote_plus(value)))
                else:
                    query.append(quote_plus(key))
            result += '?' + '&'.join(query)
        if self.fragment is not None:
            result += '#' + quote_plus(self.fragment)
        return result

    def __str__(self):
        return self.to_string()
