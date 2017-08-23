# -*- coding: utf8 -*-
from tokenizer import Tokenizer
from tags import CloseTag
from error import UnbalancedError


class HtmlHelper(Exception):

    @classmethod
    def truncate(cls, value, target_len=200, ellipsis='...'):
        """Returns a copy of str truncated to target_len characters,
        preserving HTML markup (which does not count towards the length).
        Any tags that would be left open by truncation will be closed at
        the end of the returned string.  Optionally append ellipsis if
        the string was truncated."""
        # open tags are pushed on here, then popped when
        # the matching close tag is found
        stack = []
        # string to be returned
        retval = []
        # number of characters (not counting markup) placed in retval so far
        length = 0
        tokens = Tokenizer(value)
        tok = tokens.next_token()
        while tok != tokens.token_end:
            if not length < target_len:
                retval.append(ellipsis)
                break
            if tok.__class__.__name__ == 'OpenTag':
                stack.append(tok)
                retval.append(tok.as_string())
            elif tok.__class__.__name__ == 'CloseTag':
                if stack[-1].tag == tok.tag:
                    stack.pop()
                    retval.append(tok.as_string())
                else:
                    raise UnbalancedError(tok.as_string())
            elif tok.__class__.__name__ == 'SelfClosingTag':
                retval.append(tok.as_string())
            else:
                retval.append(tok)
                length += 1
            tok = tokens.next_token()
        while len(stack) > 0:
            tok = CloseTag(stack.pop().tag)
            retval.append(tok.as_string())
        return ''.join(retval)
