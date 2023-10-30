from typing import List

import token
import expr
import lox

class ParseError(Exception):
    pass

class Parser:
    tokens : List[token.Token]
    current : int

    def __init__(self, tokens : List[token.Token]):
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

        while self.match(token.TokenType.BANG_EQUAL, token.TokenType.EQUAL_EQUAL):
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
        
    def check(self, _type : token.TokenType) -> True:
        if self.is_at_end():
            return False
        return self.peek().token_type == _type
    
    def advance(self) -> token.Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        return self.peek().token_type == token.TokenType.EOF
    
    def peek(self) -> token.Token:
        return self.tokens[self.current]

    def previous(self) -> token.Token:
        return self.tokens[self.current - 1]
    
    def comparison(self) -> expr.Expr:
        expression = self.addition()
        while self.match(token.TokenType.GREATER, 
                         token.TokenType.GREATER_EQUAL,
                         token.TokenType.LESS,
                         token.TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.addition()
            expression = expr.Binary(expression, operator, right)
        
        return expression

    
    def addition(self) -> expr.Expr:
        expression = self.multiplication()
        while self.match(token.TokenType.MINUS, token.TokenType.PLUS):
            operator = self.previous()
            right = self.multiplication()
            expression = expr.Binary(expression, operator, right)
        
        return expression
    
    def multiplication(self) -> expr.Expr:
        expression = self.unary()
        while self.match(token.TokenType.SLASH, token.TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expression = expr.Binary(expression, operator, right)
        
        return expression
    
    def unary(self) -> expr.Expr:
        if self.match(token.TokenType.BANG, token.TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return expr.Unary(operator, right)
        else:
            return self.primary()
    
    def primary(self) -> expr.Expr:
        if self.match(token.TokenType.FALSE):
            return expr.Literal(False)
        if self.match(token.TokenType.TRUE):
            return expr.Literal(True)
        if self.match(token.TokenType.NIL):
            return expr.Literal(None)
        
        if self.match(token.TokenType.NUMBER, token.TokenType.STRING):
            return expr.Literal(self.previous().literal)
        
        if self.match(token.TokenType.LEFT_PAREN):
            expression = self.expression()
            self.consume(token.TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expr.Grouping(expression)
        
        raise self.error(self.peek(), "Expect expression.")
        
    def consume(self, _type : token.TokenType, message : str) -> token.Token:
        if self.check(_type):
            return self.advance()
        else:
            raise self.error(self.peek(), message)

    def error(self, _token : token.Token, message : str) -> ParseError:
        lox.error(_token, message)
        return ParseError()
    
    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().token_type == token.TokenType.SEMICOLON:
                return
            
            if self.peek().token_type in (
                token.TokenType.CLASS,
                token.TokenType.FUN,
                token.TokenType.VAR,
                token.TokenType.FOR,
                token.TokenType.IF,
                token.TokenType.WHILE,
                token.TokenType.PRINT,
                token.TokenType.RETURN
            ):
                return
            
            self.advance()