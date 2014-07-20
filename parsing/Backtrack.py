__author__ = 'kid143'


from base import *


class ListLexer(Lexer):
    """
    ListLexer
    """
    def __init__(self, input_string):
        Lexer.__init__(self, input_string)

    def ws(self):
        while self.c in EMPTY:
            self.advance()

    def is_letter(self):
        return 'a' <= self.c <= 'z' or 'A' <= self.c <= 'Z'

    def letter(self):
        if self.is_letter():
            self.consume()

    def next_token(self):
        def comma():
            self.consume()
            return Token(COMMA, ',')

        def lbracket():
            self.consume()
            return Token(LSQRTBRACKET, '[')

        def rbracket():
            self.consume()
            return Token(RSQRTBRACKET, ']')

        def equals():
            self.consume()
            return Token(EQUALS, '=')

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

            return Token(NAME, s)

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

        return Token(EOF, TOKEN_NAMES[EOF])


class Parser(object):
    """
    Parser
    """
    def __init__(self, input_lexer):
        self.lexer = input_lexer
        self.lookahead = []
        self.markers = []
        self.p = 0

    def lt(self, i):
        self.sync(i)
        return self.lookahead[self.p+i-1]

    def la(self, i):
        return self.lt(i).token_type

    def match(self, x):
        if self.la(1) == x:
            self.consume()
        else:
            raise ParseError('expecting {exp} found {fnd} at {pos}'.format(
                exp=TOKEN_NAMES[x],
                fnd=self.lt(1),
                pos=self.lexer.p)
            )

    def sync(self, i):
        if self.p + i - 1 > (len(self.lookahead) - 1):
            n = self.p + i - 1 - (len(self.lookahead) - 1)
            self.fill(n)

    def fill(self, n):
        ex = [self.lexer.next_token() for x in range(n)]
        self.lookahead.extend(ex)

    def consume(self):
        self.p += 1
        if self.p == len(self.lookahead) and not self.is_speculating:
            self.p = 0
            self.lookahead.clear()

        self.sync(1)

    def mark(self):
        self.markers.append(self.p)
        return self.p

    def release(self):
        marker = self.markers[len(self.markers)-1]
        self.markers.pop()
        self.seek(marker)

    def seek(self, index):
        self.p = index

    @property
    def is_speculating(self):
        return len(self.markers) > 0


class BacktrackParser(Parser):
    """
    Backtrack Parser
    """
    def __init__(self, input_lexer):
        Parser.__init__(self, input_lexer)

    def stat(self):
        if self.speculate_stat_alt1():
            self.list()
            self.match(EOF)
        elif self.speculate_stat_alt2():
            self.assign()
            self.match(EOF)
        else:
            raise ParseError('expecting stat found {fnd} at {pos}'.format(fnd=self.lt(1), pos=self.lexer.p))

    def speculate_stat_alt1(self):
        success = True
        self.mark()
        try:
            self.list()
            self.match(EOF)
        except ParseError:

            success = False

        self.release()
        return success

    def speculate_stat_alt2(self):
        success = True
        self.mark()
        try:
            self.assign()
            self.match(EOF)
        except ParseError:
            success = False

        self.release()
        return success

    def list(self):
        self.match(LSQRTBRACKET)
        self.elements()
        self.match(RSQRTBRACKET)

    def elements(self):
        self.element()
        while self.la(1) == COMMA:
            self.match(COMMA)
            self.element()

    def element(self):
        if self.la(1) == NAME and self.la(2) == EQUALS:
            self.match(NAME)
            self.match(EQUALS)
            self.match(NAME)
        elif self.la(1) == NAME:
            self.match(NAME)
        elif self.la(1) == LSQRTBRACKET:
            self.list()
        else:
            raise ParseError('expecting assign, NAME or list found {fnd}'.format(fnd=self.lt(1)))

    def assign(self):
        self.list()
        self.match(EQUALS)
        self.list()


if __name__ == '__main__':
    lexer = ListLexer('[a, b=c, r, efg]')
    parser = BacktrackParser(lexer)
    parser.stat()

    lexer2 = ListLexer('[a,b]=[c,d]')
    parser2 = BacktrackParser(lexer2)
    parser2.stat()
