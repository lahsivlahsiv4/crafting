from typing import List

import Token
import expr
import lox
import stmt

class ParseError(Exception):
    pass

class Parser:
    tokens : List[Token.Token]
    current : int

    def __init__(self, tokens : List[Token.Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        
        return statements

    def declaration(self) -> stmt.Stmt:
        try:
            if self.match(Token.TokenType.CLASS):
                return self.class_declaration()
            elif self.match(Token.TokenType.FUN):
                return self.function("function")
            elif self.match(Token.TokenType.VAR):
                return self.var_declaration()
            else:
                return self.statement()
        except ParseError:
            self.synchronize()
            return None
        
    
    def class_declaration(self) -> stmt.Stmt:
        name = self.consume(Token.TokenType.IDENTIFIER, "Expect class name.")
        
        superclass = None
        
        if self.match(Token.TokenType.LESS):
            self.consume(Token.TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = expr.Variable(self.previous())
        
        self.consume(Token.TokenType.LEFT_BRACE, "Expect '{' before class body.")
        
        methods = []

        while not self.check(Token.TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))
        
        self.consume(Token.TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return stmt.Class(name, superclass, methods)
    
    def function(self, kind : str) -> stmt.Function:
        name = self.consume(Token.TokenType.IDENTIFIER, f"Expect {kind} name.")
        parameters = []

        self.consume(Token.TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")

        if not self.check(Token.TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Cannot have more than 255 parameters.")
                
                parameters.append(self.consume(Token.TokenType.IDENTIFIER, "Expect parameter name."))

                if not self.match(Token.TokenType.COMMA):
                    break
        
        self.consume(Token.TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        self.consume(Token.TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()

        return stmt.Function(name, parameters, body)

    def var_declaration(self) -> stmt.Stmt:
        name = self.consume(Token.TokenType.IDENTIFIER, "Expect variable name.")
        
        initializer = None
        if self.match(Token.TokenType.EQUAL):
            initializer = self.expression()
        
        self.consume(Token.TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return stmt.Var(name, initializer)
    
    def statement(self) -> stmt.Stmt:
        if self.match(Token.TokenType.FOR):
            return self.for_statement()

        if self.match(Token.TokenType.IF):
            return self.if_statement()

        if self.match(Token.TokenType.PRINT):
            return self.print_statement()

        if self.match(Token.TokenType.RETURN):
            return self.return_statement()

        if self.match(Token.TokenType.WHILE):
            return self.while_statement()
        
        if self.match(Token.TokenType.LEFT_BRACE):
            return stmt.Block(self.block())

        return self.expression_statement()

    def return_statement(self) -> stmt.Stmt:
        keyword = self.previous()
        value = None

        if not self.check(Token.TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(Token.TokenType.SEMICOLON, "Expect ';' after return value.")
        return stmt.Return(keyword, value)

    def for_statement(self) -> stmt.Stmt:
        self.consume(Token.TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer = None
        if self.match(Token.TokenType.SEMICOLON):
            initializer = None
        elif self.match(Token.TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        
        condition = None
        if not self.check(Token.TokenType.SEMICOLON):
            condition = self.expression()
        
        self.consume(Token.TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.check(Token.TokenType.RIGHT_PAREN):
            increment = self.expression()
        
        self.consume(Token.TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self.statement()

        if increment != None:
            body = stmt.Block([body, stmt.Expression(increment)])
        
        if condition == None:
            condition = expr.Literal(True)
        
        body = stmt.While(condition, body)

        if initializer != None:
            body = stmt.Block([initializer, body])

        return body



    def while_statement(self) -> stmt.Stmt:
        self.consume(Token.TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(Token.TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()

        return stmt.While(condition, body)

    def if_statement(self) -> stmt.Stmt:
        self.consume(Token.TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(Token.TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch = self.statement()
        else_branch = None

        if self.match(Token.TokenType.ELSE):
            else_branch = self.statement()
        
        return stmt.If(condition, then_branch, else_branch)

    def block(self) -> List[stmt.Stmt]:
        statements = []

        while not self.check(Token.TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        
        self.consume(Token.TokenType.RIGHT_BRACE, "Expect '}' after block.")

        return statements

    def print_statement(self) -> stmt.Stmt:
        value = self.expression()
        self.consume(Token.TokenType.SEMICOLON, "Expect ';' after value.")
        return stmt.Print(value)
    
    def expression_statement(self) -> stmt.Stmt:
        expr = self.expression()
        self.consume(Token.TokenType.SEMICOLON, "Expect ';' after expression.")
        return stmt.Expression(expr)
    
    def assignment(self) -> expr.Expr:
        expression = self._or()

        if self.match(Token.TokenType.EQUAL):
            equals = self.previous()
            value  = self.assignment()

            if type(expression) == expr.Variable:
                name = expression.name
                return expr.Assign(name, value)
            elif type(expression) == expr.Get:
                get = expression
                return expr.Set(get._object, get.name, value)
            else:
                self.error(equals, "Invalid assignment target")
        
        return expression

    def _or(self) -> expr.Expr:
        expression = self._and()

        while self.match(Token.TokenType.OR):
            operator = self.previous()
            right = self._and()
            expression = expr.Logical(expression, operator, right)

        return expression
    
    def _and(self) -> expr.Expr:
        expression = self.equality()

        while self.match(Token.TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expression = expr.Logical(expression, operator, right)

        return expression

    def expression(self) -> expr.Expr:
        return self.assignment()
    
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
            return self.call()
    
    def call(self) -> expr.Expr:
        expression = self.primary()

        while True:
            if self.match(Token.TokenType.LEFT_PAREN):
                expression = self.finish_call(expression)
            elif self.match(Token.TokenType.DOT):
                name = self.consume(Token.TokenType.IDENTIFIER, "Expect property name after '.'.")
                expression = expr.Get(expression, name)
            else:
                break
        
        return expression
    
    def finish_call(self, callee : expr.Expr) -> expr.Expr:
        arguments = []
        if not self.check(Token.TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Cannot have more than 255 arguments.")

                arguments.append(self.expression())
                
                if not self.match(Token.TokenType.COMMA):
                    break
        
        paren = self.consume(Token.TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return expr.Call(callee, paren, arguments)

    
    def primary(self) -> expr.Expr:
        if self.match(Token.TokenType.FALSE):
            return expr.Literal(False)
        if self.match(Token.TokenType.TRUE):
            return expr.Literal(True)
        if self.match(Token.TokenType.NIL):
            return expr.Literal(None)
        
        if self.match(Token.TokenType.NUMBER, Token.TokenType.STRING):
            return expr.Literal(self.previous().literal)
        
        if self.match(Token.TokenType.SUPER):
            keyword = self.previous()

            self.consume(Token.TokenType.DOT, "Expect '.' after 'super'.")
            method = self.consume(Token.TokenType.IDENTIFIER, "Expect superclass method name.")
            return expr.Super(keyword, method)

        if self.match(Token.TokenType.THIS):
            return expr.This(self.previous())

        if (self.match(Token.TokenType.IDENTIFIER)):
            return expr.Variable(self.previous())
        
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