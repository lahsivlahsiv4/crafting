from typing import List, Any

import LoxCallable
import LoxInstance

class LoxClass(LoxCallable.LoxCallable):
    name : str

    def __init__(self, name, superclass, methods):
        self.name = name
        self.methods = methods
        self.superclass = superclass
    
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
        
        if self.superclass != None:
            return self.superclass.find_method(name)

        return None

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer == None:
            return 0
        else:
            return initializer.arity()
