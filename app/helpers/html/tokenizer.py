# -*- coding: utf8 -*-
from tags import CloseTag, OpenTag, SelfClosingTag


class Tokenizer:

    token_end = -1

    def __init__(self, input):
        self.input = input
        # points at the next unconsumed character of the input
        self.counter = 0

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
            return self.token_end

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
        Precondition: self.counter points at the first character of
        the tag name
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
        Precondition: self.counter points at the first character of
        the tag name
        Postcondition: self.counter points at the character after the <tag>
        """
        char = self.input[self.counter]
        tag = []
        while char != '>':
            tag.append(char)
            char = self.__next_char()
        self.counter += 1
        return CloseTag(''.join(tag))
