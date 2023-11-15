from typing import Dict, Any

import Token
import interpreter as Interpreter
class LoxInstance:
    fields : Dict[str, Any]

    def __init__(self, klass):
        self.klass = klass
        self.fields= {}
    
    def get(self, name : Token.Token) -> Any:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        
        method = self.klass.find_method(name.lexeme)
        if method != None:
            return method.bind(self)

        raise Interpreter.RuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def _set(self, name : Token.Token, value):
        self.fields[name.lexeme] = value

    def __str__(self) -> str:
        return self.klass.name + " instance"