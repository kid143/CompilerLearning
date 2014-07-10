#! /usr/bin/env python3

__author__ = 'huang'


"""This is a simple recursive down list parser demo
   :author  kid143
   :version 0.1
"""


class ParseError(Exception):
    pass


class Token:
    """
    Token object
    """
    def __init__(self, token_type, string):
        self.token_type = token_type
        self.string = string

    def __str__(self):
        return "<Token type: {type}, string: '{string}'>".format(type=ListLexer.token_names[self.token_type],
                                                                 string=self.string)


class Lexer:
    """
    Lexer base class
    """
    def __init__(self, input_string):
        self.input_string = input_string
        self.p = 0
        self.c = self.input_string[self.p]

    def consume(self):
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


class ListLexer(Lexer):
    """
    ListLexer class
    """
    COMMA = 2
    LBRACKET = 3
    RBRACKET = 4
    NAME = 5
    token_names = ['n/a', '<EOF>', 'COMMA', 'LBRACKET', 'RBRACKET', 'NAME']

    def __init__(self, input_string):
        Lexer.__init__(self, input_string)

    def next_token(self):
        def ws():
            while self.c == ' ' or self.c == '\t' or self.c == '\r' or self.c == '\n':
                self.consume()

        def comma():
            self.consume()
            return Token(self.COMMA, ',')

        def lbracket():
            self.consume()
            return Token(self.LBRACKET, '[')

        def rbracket():
            self.consume()
            return Token(self.RBRACKET, ']')

        case_dict = {
            ' ': ws,
            '\t': ws,
            '\r': ws,
            '\n': ws,
            ',': comma,
            '[': lbracket,
            ']': rbracket
        }

        def name_token():
            s = self.c
            while self.c not in case_dict:
                self.consume()
                ''.join([s, self.c])

            return Token(self.NAME, s)
        while self.c is not None:
            try:
                token_func = case_dict[self.c]
            except KeyError:
                token_func = name_token

            if token_func == ws:
                token_func()
                continue
            else:
                return token_func()

        return Token(1, ListLexer.token_names[1])


class Parser:
    """
    Parser class
    """
    def __init__(self, input_lexer):
        self.lexer = input_lexer
        self.lookahead = None
        self.consume()

    def match(self, x):
        if self.lookahead.token_type == x:
            self.consume()
        else:
            raise ParseError('Expect {expect}; found: {found}'.format(expect=x, found=self.lookahead.token_type))

    def consume(self):
        self.lookahead = self.lexer.next_token()


class ListParser(Parser):
    """
    ListParser
    """
    def __init__(self, input_lexer):
        Parser.__init__(self, input_lexer)

    def list(self):
        self.match(ListLexer.LBRACKET)
        self.elements()
        self.match(ListLexer.RBRACKET)

    def elements(self):
        self.element()
        while self.lookahead.token_type == ListLexer.COMMA:
            self.consume()
            self.element()

    def element(self):
        if self.lookahead.token_type == ListLexer.LBRACKET:
            self.list()
        elif self.lookahead.token_type == ListLexer.NAME:
            self.match(ListLexer.NAME)
        else:
            raise ParseError('Expect NAME or list; found {found}'.format(found=str(self.lookahead)))


class DictLexer(Lexer):
    """
    Dict Lexer
    """
    COMMA = 2
    LBRACKET = 3
    RBRACKET = 4
    NAME = 5
    COLON = 6
    token_names = ['n/a', '<EOF>', 'COMMA', 'LBRACKET', 'RBRACKET', 'NAME', 'COLON']

    def __init__(self, input_string):
        Lexer.__init__(self, input_string)

    def next_token(self):
        def ws():
            while self.c == ' ' or self.c == '\t' or self.c == '\r' or self.c == '\n':
                self.consume()

        def comma():
            self.consume()
            return Token(self.COMMA, ',')

        def lbracket():
            self.consume()
            return Token(self.LBRACKET, '{')

        def rbracket():
            self.consume()
            return Token(self.RBRACKET, '}')

        def colon():
            self.consume()
            return Token(self.COLON, ':')

        case_dict = {
            ' ': ws,
            '\t': ws,
            '\r': ws,
            '\n': ws,
            ',': comma,
            '{': lbracket,
            '}': rbracket,
            ':': colon
        }

        def name_token():
            s = self.c
            while self.c not in case_dict:
                self.consume()
                ''.join([s, self.c])

            return Token(self.NAME, s)

        while self.c is not None:
            try:
                token_func = case_dict[self.c]
            except KeyError:
                token_func = name_token

            if token_func == ws:
                token_func()
                continue
            else:
                return token_func()

        return Token(1, ListLexer.token_names[1])


class DictParser(Parser):
    """
    DictParser
    """
    def __init__(self, input_lexer):
        Parser.__init__(self, input_lexer)

    def dict(self):
        self.match(DictLexer.LBRACKET)
        self.pairs()
        self.match(DictLexer.RBRACKET)

    def pairs(self):
        self.pair()
        while self.lookahead.token_type == DictLexer.COMMA:
            self.consume()
            self.pair()

    def pair(self):
        self.key()
        self.match(DictLexer.COLON)
        self.value()

    def key(self):
        if self.lookahead.token_type == DictLexer.NAME:
            self.consume()
        else:
            raise ParseError('Key must be NAME; found: {found}'.format(found=str(self.lookahead)))

    def value(self):
        if self.lookahead.token_type == DictLexer.NAME:
            self.consume()
        elif self.lookahead.token_type == DictLexer.LBRACKET:
            self.dict()
        else:
            raise ParseError('Expect NAME or dict; found: {found}'.format(found=str(self.lookahead)))


if __name__ == '__main__':
    lexer = ListLexer('[a, b,[e,f]   , c, d]')
    parser = ListParser(lexer)
    parser.list()

    lexer2 = DictLexer('{a: b, c: d, e: {f: g}}')
    parser2 = DictParser(lexer2)
    parser2.dict()
