from typing import List

import Token
import lox

KEYWORDS = {
    "and"    : Token.TokenType.AND,
    "class"  : Token.TokenType.CLASS,
    "else"   : Token.TokenType.ELSE,
    "false"  : Token.TokenType.FALSE,
    "for"    : Token.TokenType.FOR,
    "fun"    : Token.TokenType.FUN,
    "if"     : Token.TokenType.IF,
    "nil"    : Token.TokenType.NIL,
    "or"     : Token.TokenType.OR,
    "print"  : Token.TokenType.PRINT,
    "return" : Token.TokenType.RETURN,
    "super"  : Token.TokenType.SUPER,
    "this"   : Token.TokenType.THIS,
    "true"   : Token.TokenType.TRUE,
    "var"    : Token.TokenType.VAR,
    "while"  : Token.TokenType.WHILE
}

class Scanner:
    source  : str
    tokens  : List[Token.Token]

    start   : int
    current : int
    line    : int

    def __init__(self, source : str):
        self.source  = source
        self.tokens  = []
        self.start   = 0
        self.current = 0
        self.line    = 1

    def scan_tokens(self) -> List[Token.Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_Token()

        self.tokens.append(Token.Token(Token.TokenType.EOF, "", None, self.line))
        
        return self.tokens
    
    def is_at_end(self) -> bool:
        return self.current >= len(self.source)
    
    def scan_Token(self) -> None:
        char = self.advance()

        if   char == "(":
            self.add_Token(Token.TokenType.LEFT_PAREN)
        elif char == ")":
            self.add_Token(Token.TokenType.RIGHT_PAREN)
        elif char == "{":
            self.add_Token(Token.TokenType.LEFT_BRACE)
        elif char == "}":
            self.add_Token(Token.TokenType.RIGHT_BRACE)
        elif char == ",":
            self.add_Token(Token.TokenType.COMMA)
        elif char == ".":
            self.add_Token(Token.TokenType.DOT)
        elif char == "-":
            self.add_Token(Token.TokenType.MINUS)
        elif char == "+":
            self.add_Token(Token.TokenType.PLUS)
        elif char == ";":
            self.add_Token(Token.TokenType.SEMICOLON)
        elif char == "*":
            self.add_Token(Token.TokenType.STAR)
        elif char == "!":
            if self.match("="):
                self.add_Token(Token.TokenType.BANG_EQUAL)
            else:
                self.add_Token(Token.TokenType.BANG)   
        elif char == "=":
            if self.match("="):
                self.add_Token(Token.TokenType.EQUAL_EQUAL)
            else:
                self.add_Token(Token.TokenType.EQUAL)
        elif char == "<":
            if self.match("="):
                self.add_Token(Token.TokenType.LESS_EQUAL)
            else:
                self.add_Token(Token.TokenType.LESS)
        elif char == ">":
            if self.match("="):
                self.add_Token(Token.TokenType.GREATER_EQUAL)
            else:
                self.add_Token(Token.TokenType.GREATER)
        
        elif char == "/":
            if self.match("/"): # It's a comment
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            else:
                self.add_Token(Token.TokenType.SLASH)
        
        elif char in " \r\t":
            pass
        elif char == "\n":
            self.line += 1

        elif char == "\"":
            self.string()
        
        elif char.isdigit():
            self.number()
        elif self.is_alpha(char):
            self.identifier()

        else:
            lox.error(self.line, "Unexpected character")
    
    def advance(self):
        self.current += 1
        return self.source[self.current - 1]
    
    def add_Token(self, Token_type : Token.TokenType, literal : object = None):
        text = self.source[self.start : self.current]
        self.tokens.append(Token.Token(Token_type, text, literal, self.line))
    
    def match(self, expected : str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True
    
    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        else:
            return self.source[self.current]
    
    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        else:
            return self.source[self.current + 1]
    
    def string(self):
        while self.peek() != "\"" and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()
        
        if self.is_at_end():
            lox.error(self.line, "Unterminated string.")
            return
        
        # The closing ".
        self.advance()

        # Trim the surrounding quotes.
        value = self.source[self.start + 1 : self.current - 1]
        self.add_Token(Token.TokenType.STRING, value)
    
    def number(self):
        while self.peek().isdigit():
            self.advance()
        
        # Look for a fractional part.
        if self.peek() == "." and self.peek_next().isdigit():
            self.advance() # Consume the "."

            while self.peek().isdigit():
                self.advance()
        
        self.add_Token(
            Token.TokenType.NUMBER,
            float(self.source[self.start : self.current])
        )
    
    # Can't use isalpha because it needs to include underscores
    def is_alpha(self, char : str) -> bool:
        return char.isalpha() or char == "_"
    
    def is_alphanumeric(self, char : str) -> bool:
        return char.isalnum() or char == "_"

    def identifier(self):
        while self.is_alphanumeric(self.peek()):
            self.advance()

        text = self.source[self.start : self.current]

        if text in KEYWORDS:
            self.add_Token(KEYWORDS[text])
        else:
            self.add_Token(Token.TokenType.IDENTIFIER)
