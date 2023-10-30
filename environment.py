from typing import Dict, Any, Union

import Token
import interpreter

class Environment:
    values : Dict[str, Any]

    def __init__(self, enclosing = None):
        self.values = {}
        self.enclosing = enclosing
    
    def define(self, name : str, value : Any):
        self.values[name] = value
    
    def get(self, name : Token.Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing != None:
            return self.enclosing.get(name)

        raise interpreter.RuntimeError(
            name, 
            f"Undefined variable '{name.lexeme}'.'"
        )
    
    def assign(self, name : Token.Token, value : Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing != None:
            self.enclosing.assign(name, value)
            return

        raise interpreter.RuntimeError(
            name,
            f"Undefined variable '{name.lexeme}'."
        )