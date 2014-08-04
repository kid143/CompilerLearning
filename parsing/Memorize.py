__author__ = 'huang'


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
    Memorized backtrack parser
    """
    def __init__(self, input_lexer):
        self.lexer = input_lexer
        self.markers = []
        self.lookahead = []
        self.p = 0
        self.sync(1)

    def consume(self):
        self.p += 1
        if self.p == len(self.lookahead) and not self.isSpeculating:
            self.p = 0
            self.lookahead.clear()
            self.clearMemo()

        self.sync(1)

    def sync(self, i):
        if self.p + i - 1 > (len(self.lookahead) - 1):
            n = (self.p + i - 1) - (len(self.lookahead) - 1)
            self.fill(n)

    def fill(self, n):
        ex = [self.lexer.next_token() for x in range(n)]
        self.lookahead.extend(ex)

    def lt(self, i):
        self.sync(i)
        return self.lookahead[self.p + i - 1]

    def la(self, i):
        return self.lt(i).token_type

    def match(self, x):
        if self.la(1) == x:
            self.consume()
        else:
            raise ParseError('expecting {ex} found {fnd}'.format(ex=TOKEN_NAMES[x], fnd=self.lt(1)))

    def mark(self):
        self.markers.append(self.p)
        return self.p

    def release(self):
        marker = self.markers[len(self.markers) - 1]
        self.markers.pop()
        self.seek(marker)

    def seek(self, index):
        self.p = index

    @property
    def isSpeculating(self):
        return len(self.markers) > 0

    def alreadyParsedRule(self, memoization):
        memoI = memoization.get(self.p)
        if not memoI:
            return False

        print('parsed list before at index: {idx}; skip ahead to token index: {idxx}'.format(
            idx=self.p,
            idxx=self.lookahead[memoI].string))

        if memoI == MEMO_FAILED:
            raise ParseError('Previous Parse Failed')

        self.seek(memoI)
        return True

    def memoize(self, memoization, startTokenIndex, failed):
        stopTokenIndex =  MEMO_FAILED if failed else self.p
        memoization[startTokenIndex] = stopTokenIndex

    def clearMemo(self):
        raise NotImplementedError


class MemoBacktrackParser(Parser):
    """
    List parser
    """
    def __init__(self, input_lexer):
        Parser.__init__(self, input_lexer)
        self.list_memo = {}

    def clearMemo(self):
        self.list_memo.clear()

    def stat(self):
        if self.speculate_stat_alt1:
            print('predict alternative 1')
            self.list()
            self.match(EOF)
        elif self.speculate_stat_alt2:
            print('predict alternative 2')
            self.assign()
            self.match(EOF)
        else:
            raise ParseError('expecting stat found {fnd}'.format(fnd=self.lt(1)))

    @property
    def speculate_stat_alt1(self):
        print('attempt alternative 1')
        success = True
        self.mark()
        try:
            self.list()
            self.match(EOF)
        except ParseError:
            success = False

        self.release()
        return success

    @property
    def speculate_stat_alt2(self):
        print('attempt alternative 2')
        success = True
        self.mark()
        try:
            self.assign()
            self.match(EOF)
        except ParseError:
            success = False

        self.release()
        return success

    def _list(self):
        self.match(LSQRTBRACKET)
        self.elements()
        self.match(RSQRTBRACKET)

    def assign(self):
        self.list()
        self.match(EQUALS)
        self.list()

    def list(self):
        failed = False
        startTokenIndex = self.p
        if self.isSpeculating and self.alreadyParsedRule(self.list_memo):
            return

        try:
            self._list()
        except ParseError:
            failed = True
            raise
        finally:
            if self.isSpeculating:
                self.memoize(self.list_memo, startTokenIndex, failed)

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
            raise ParseError('expecting element found {fnd}'.format(fnd=self.lt(1)))


if __name__ == '__main__':
    lexer1 = ListLexer('[a,b,c=d,e,f]')
    parser1 = MemoBacktrackParser(lexer1)
    parser1.stat()

    lexer2 = ListLexer('[a,b,c] = [d,e,f]')
    parser2 = MemoBacktrackParser(lexer2)
    parser2.stat()
