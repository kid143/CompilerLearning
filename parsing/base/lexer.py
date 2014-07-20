#! /usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = 'kid143'


"""This is base components
"""

from .constants import TOKEN_NAMES


class ParseError(Exception):
    pass


class Token(object):
    """
    Token object
    """
    def __init__(self, token_type, string):
        self.token_type = token_type
        self.string = string

    def __str__(self):
        return "<Token type: {type}, string: '{string}'>".format(type=TOKEN_NAMES[self.token_type],
                                                                 string=self.string)


class Lexer(object):
    """
    Lexer base class
    """
    def __init__(self, input_string):
        self.input_string = input_string
        self.p = 0
        self.c = self.input_string[self.p]

    def consume(self):
        self.advance()
        self.ws()

    def advance(self):
        self.p += 1
        try:
            self.c = self.input_string[self.p]
        except IndexError:
            self.c = None

    def match(self, x):
        """This method is used to ensure x is the next character in the input stream.
           Currently it is not called.
        """
        if self.c == x:
            self.consume()
        else:
            raise ParseError('Expect {expect}; found:{found}'.format(expect=x, found=self.c))

    def next_token(self):
        raise NotImplementedError

    def ws(self):
        raise NotImplementedError