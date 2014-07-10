from parsing.RecursiveDescendant import ListLexer

__author__ = 'huang'


"""This is a simple recursive down list parser demo with multiple lookaheads
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


class ListMultiLexer(Lexer):
    """
    ListMultiLexer
    """
    COMMA = 2
    LBRACKET = 3
    RBRACKET = 4
    NAME = 5
    EQUALS = 6
    token_names = ['n/a', '<EOF>', 'COMMA', 'LBRACKET', 'RBRACKET', 'NAME', 'EQUALS']

    def __init__(self, input_string):
        Lexer.__init__(self, input_string)

    def is_letter(self):
        return 'a' <= self.c <= 'z' or 'A' <= self.c <= 'Z'

    def letter(self):
        if self.is_letter():
            self.consume()

    def ws(self):
        while self.c in (' ', '\t', '\r', '\n'):
            self.advance()

    def next_token(self):
        def comma():
            self.consume()
            return Token(self.COMMA, ',')

        def lbracket():
            self.consume()
            return Token(self.LBRACKET, '[')

        def rbracket():
            self.consume()
            return Token(self.RBRACKET, ']')

        def equals():
            self.consume()
            return Token(self.EQUALS, '=')

        case_dict = {
            ' ': self.ws,
            '\t': self.ws,
            '\r': self.ws,
            '\n': self.ws,
            ',': comma,
            '[': lbracket,
            ']': rbracket,
            '=': equals
        }

        def name_token():
            s = self.c
            while self.is_letter():
                self.consume()
                s = ''.join([s, self.c])

            return Token(self.NAME, s)

        while self.c is not None:
            try:
                token_func = case_dict[self.c]
            except KeyError:
                token_func = name_token

            if token_func == self.ws:
                self.ws()
                continue
            else:
                return token_func()

        return Token(1, ListLexer.token_names[1])


class Parser:
    """
    Parser class
    """
    def __init__(self, input_lexer, k):
        self.lexer = input_lexer
        self.lookahead = []
        self.k = k
        self.p = 0
        for i in range(k):
            self.consume()

    def match(self, x):
        if self.la(1) == x:
            self.consume()
        else:
            raise ParseError('Expect {expect}; found: {found}'.format(expect=x, found=self.la(1)))

    def lt(self, i):
        return self.lookahead[(self.p + i - 1) % self.k]

    def la(self, i):
        return self.lt(i).token_type

    def consume(self):
        if len(self.lookahead) > self.p:
            self.lookahead[self.p] = self.lexer.next_token()
        else:
            self.lookahead.append(self.lexer.next_token())
        self.p = (self.p + 1) % self.k


class ListMultiParser(Parser):
    """
    ListMultiParser
    """
    def __init__(self, input_lexer, k):
        Parser.__init__(self, input_lexer, k)

    def list(self):
        self.match(ListMultiLexer.LBRACKET)
        self.elements()
        self.match(ListMultiLexer.RBRACKET)

    def elements(self):
        self.element()
        while self.la(1) == ListMultiLexer.COMMA:
            self.consume()
            self.element()

    def element(self):
        if self.la(1) == ListMultiLexer.NAME and self.la(2) == ListMultiLexer.EQUALS:
            self.match(ListMultiLexer.NAME)
            self.match(ListMultiLexer.EQUALS)
            self.match(ListMultiLexer.NAME)
        elif self.la(1) == ListMultiLexer.NAME:
            self.match(ListMultiLexer.NAME)
        elif self.la(1) == ListMultiLexer.LBRACKET:
            self.list()
        else:
            raise ParseError('Expect NAME or list; found {fnd}'.format(fnd=str(self.la(1))))


if __name__ == '__main__':
    lexer = ListMultiLexer('[a, b=c, d, efg]')
    parser = ListMultiParser(lexer, 2)
    parser.list()
