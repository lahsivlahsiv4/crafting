from typing import List, Any

import LoxCallable
import LoxInstance

class LoxClass(LoxCallable.LoxCallable):
    name : str

    def __init__(self, name, methods):
        self.name = name
        self.methods = methods
    
    def __str__(self) -> str:
        return self.name
    
    def call(self, interpreter, arguments : List[Any]) -> Any:
        instance = LoxInstance.LoxInstance(self)
        
        initializer = self.find_method("init")
        if initializer != None:
            initializer.bind(instance).call(interpreter, arguments)

        return instance
    
    def find_method(self, name : str):
        if name in self.methods:
            return self.methods.get(name)

        return None

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer == None:
            return 0
        else:
            return initializer.arity()
