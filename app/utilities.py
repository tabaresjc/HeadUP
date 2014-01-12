import sys
from flask import request, json, Response, flash, redirect
from flask.ext.babel import gettext, format_datetime, format_timedelta

END = -1


class UnbalancedError(Exception):
    pass


class OpenTag:
    def __init__(self, tag, rest=''):
        self.tag = tag
        self.rest = rest

    def as_string(self):
        return '<' + self.tag + self.rest + '>'


class CloseTag(OpenTag):
    def as_string(self):
        return '</' + self.tag + '>'


class SelfClosingTag(OpenTag):
    pass


class Tokenizer:
    def __init__(self, input):
        self.input = input
        self.counter = 0  # points at the next unconsumed character of the input

    def __next_char(self):
        self.counter += 1
        return self.input[self.counter]

    def next_token(self):
        try:
            char = self.input[self.counter]
            self.counter += 1
            if char == '&':
                return self.__entity()
            elif char != '<':
                return char
            elif self.input[self.counter] == '/':
                self.counter += 1
                return self.__close_tag()
            else:
                return self.__open_tag()
        except IndexError:
            return END

    def __entity(self):
        """Return a token representing an HTML character entity.
        Precondition: self.counter points at the charcter after the &
        Postcondition: self.counter points at the character after the ;
        """
        char = self.input[self.counter]
        entity = ['&']
        while char != ';':
            entity.append(char)
            char = self.__next_char()
        entity.append(';')
        self.counter += 1
        return ''.join(entity)

    def __open_tag(self):
        """Return an open/close tag token.
        Precondition: self.counter points at the first character of the tag name
        Postcondition: self.counter points at the character after the <tag>
        """
        char = self.input[self.counter]
        tag = []
        rest = []
        while char != '>' and char != ' ':
            tag.append(char)
            char = self.__next_char()
        while char != '>':
            rest.append(char)
            char = self.__next_char()
        if self.input[self.counter - 1] == '/':
            self.counter += 1
            return SelfClosingTag(''.join(tag), ''.join(rest))
        else:
            self.counter += 1
            return OpenTag(''.join(tag), ''.join(rest))

    def __close_tag(self):
        """Return an open/close tag token.
        Precondition: self.counter points at the first character of the tag name
        Postcondition: self.counter points at the character after the <tag>
        """
        char = self.input[self.counter]
        tag = []
        while char != '>':
            tag.append(char)
            char = self.__next_char()
        self.counter += 1
        return CloseTag(''.join(tag))


def truncate(str, target_len, ellipsis=''):
    """Returns a copy of str truncated to target_len characters,
    preserving HTML markup (which does not count towards the length).
    Any tags that would be left open by truncation will be closed at
    the end of the returned string.  Optionally append ellipsis if
    the string was truncated."""
    stack = []   # open tags are pushed on here, then popped when the matching close tag is found
    retval = []  # string to be returned
    length = 0   # number of characters (not counting markup) placed in retval so far
    tokens = Tokenizer(str)
    tok = tokens.next_token()
    while tok != END:
        if not length < target_len:
            retval.append(ellipsis)
            break
        if tok.__class__.__name__ == 'OpenTag':
            stack.append(tok)
            retval.append( tok.as_string() )
        elif tok.__class__.__name__ == 'CloseTag':
            if stack[-1].tag == tok.tag:
                stack.pop()
                retval.append( tok.as_string() )
            else:
                raise UnbalancedError( tok.as_string() )
        elif tok.__class__.__name__ == 'SelfClosingTag':
            retval.append( tok.as_string() )
        else:
            retval.append(tok)
            length += 1
        tok = tokens.next_token()
    while len(stack) > 0:
        tok = CloseTag( stack.pop().tag )
        retval.append( tok.as_string() )
    return ''.join(retval)

if __name__ == "__main__":
    try:
        while True:
            print(truncate(raw_input("> "), int(sys.argv[1])))
    except EOFError:
        sys.exit(0)


class Utilities(object):
    @staticmethod
    def redirect_json_or_html(url, type, message=''):
        if request.is_xhr:
            if message:
                js = [{"result": "error", "message": message, "type": "category", "redirect": url}]
            else:
                js = [{"result": "ok", "type": "category", "redirect": url}]
            return Response(json.dumps(js), mimetype='application/json')
        else:
            if message:
                flash(message, 'error')
            return redirect(url)

    @staticmethod
    def datetimeformat(value, format='EEE, d MMM yyyy H:mm:ss'):
        return format_datetime(value, format)

    @staticmethod
    def humanformat(value):
        #return human(value, precision=1)
        return gettext('Posted %(ago)s ago', ago=format_timedelta(value, granularity='second'))

    @staticmethod
    def htmltruncate(value, target_len=200, ellipsis='...'):
        return truncate(value, target_len, ellipsis)

    @staticmethod
    def get_navigation_bar(value, sorted=True):
        d = dict([
            (0, {
                'name': 'Dashboard',
                'url': 'dashboard',
                'icon': 'icon-home',
                'pattern': 'dashboard'
            }),
            (1, {
                'name': 'Posts',
                'url': '',
                'icon': 'icon-edit',
                'pattern': 'PostsView',
                'sub-menu': {
                    'index': {
                        'name': 'Post List',
                        'url': 'PostsView:index'
                    },
                    'new': {
                        'name': 'New Post',
                        'url': 'PostsView:post_0'
                    }
                }
            }),
            (2, {
                'name': 'Comments',
                'url': 'CommentsView:index',
                'icon': 'icon-comments-alt',
                'pattern': 'CommentsView'
            }),
            (3, {
                'name': 'Categories',
                'url': 'CategoriesView:index',
                'icon': 'icon-bookmark',
                'pattern': 'CategoriesView'
            }),
            (4, {
                'name': 'Users',
                'url': '',
                'icon': 'icon-user',
                'pattern': 'UsersView',
                'sub-menu': {
                    'index': {
                        'name': 'User List',
                        'url': 'UsersView:index'
                    },
                    'new': {
                        'name': 'New User',
                        'url': 'UsersView:post_0'
                    }
                }
            })
        ])
        return d
