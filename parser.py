from typing import List

import Token
import expr
import lox

class ParseError(Exception):
    pass

class Parser:
    tokens : List[Token.Token]
    current : int

    def __init__(self, tokens : List[Token.Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self):
        try:
            return self.expression()
        except ParseError:
            return None
    
    def expression(self) -> expr.Expr:
        return self.equality()
    
    def equality(self) -> expr.Expr:
        expression = self.comparison()

        while self.match(Token.TokenType.BANG_EQUAL, Token.TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expression = expr.Binary(expression, operator, right)
        
        return expression
    
    def match(self, *types) -> bool:
        for _type in types:
            if self.check(_type):
                self.advance()
                return True
        else:
            return False
        
    def check(self, _type : Token.TokenType) -> True:
        if self.is_at_end():
            return False
        return self.peek().token_type == _type
    
    def advance(self) -> Token.Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        return self.peek().token_type == Token.TokenType.EOF
    
    def peek(self) -> Token.Token:
        return self.tokens[self.current]

    def previous(self) -> Token.Token:
        return self.tokens[self.current - 1]
    
    def comparison(self) -> expr.Expr:
        expression = self.addition()
        while self.match(Token.TokenType.GREATER, 
                         Token.TokenType.GREATER_EQUAL,
                         Token.TokenType.LESS,
                         Token.TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.addition()
            expression = expr.Binary(expression, operator, right)
        
        return expression

    
    def addition(self) -> expr.Expr:
        expression = self.multiplication()
        while self.match(Token.TokenType.MINUS, Token.TokenType.PLUS):
            operator = self.previous()
            right = self.multiplication()
            expression = expr.Binary(expression, operator, right)
        
        return expression
    
    def multiplication(self) -> expr.Expr:
        expression = self.unary()
        while self.match(Token.TokenType.SLASH, Token.TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expression = expr.Binary(expression, operator, right)
        
        return expression
    
    def unary(self) -> expr.Expr:
        if self.match(Token.TokenType.BANG, Token.TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return expr.Unary(operator, right)
        else:
            return self.primary()
    
    def primary(self) -> expr.Expr:
        if self.match(Token.TokenType.FALSE):
            return expr.Literal(False)
        if self.match(Token.TokenType.TRUE):
            return expr.Literal(True)
        if self.match(Token.TokenType.NIL):
            return expr.Literal(None)
        
        if self.match(Token.TokenType.NUMBER, Token.TokenType.STRING):
            return expr.Literal(self.previous().literal)
        
        if self.match(Token.TokenType.LEFT_PAREN):
            expression = self.expression()
            self.consume(Token.TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expr.Grouping(expression)
        
        raise self.error(self.peek(), "Expect expression.")
        
    def consume(self, _type : Token.TokenType, message : str) -> Token.Token:
        if self.check(_type):
            return self.advance()
        else:
            raise self.error(self.peek(), message)

    def error(self, _token : Token.Token, message : str) -> ParseError:
        lox.error(_token, message)
        return ParseError()
    
    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().token_type == Token.TokenType.SEMICOLON:
                return
            
            if self.peek().token_type in (
                Token.TokenType.CLASS,
                Token.TokenType.FUN,
                Token.TokenType.VAR,
                Token.TokenType.FOR,
                Token.TokenType.IF,
                Token.TokenType.WHILE,
                Token.TokenType.PRINT,
                Token.TokenType.RETURN
            ):
                return
            
            self.advance()