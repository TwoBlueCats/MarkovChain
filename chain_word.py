import random
class Chain_word:
    __model_ = dict()
    __context_count_ = dict()
    
    def __init__(self, n):
        self.__n = n
        
    def learn(self, s):
        context = '.' * self.__n
        for c in s:
            self.__model_[context] = self.__model_.get(context, dict())
            self.__model_[context][c] = self.__model_[context].get(c, 0) + 1
            self.__context_count_[context] = self.__context_count_.get(context, 0) + 1
            context += c
            context = context[1:]
    
    def __add__(self, s):
        if not isinstance(s, str):
            return NotImplemented
        else:
            self.learn(s)
            return self
    
    def __iadd__(self, s):
        if not isinstance(s, str):
            return NotImplemented
        else:
            self.learn(s)    
        return self
    
    def __radd__(self, s):
        if not isinstance(s, str):
            return NotImplemented
        else:
            self.learn(s)            
        return self
            
    def generate(self, ln):
        result = ""
        context = "." * self.__n
        for i in range(ln):
            context_size = self.__context_count_[context]
            #print(type(context_size))
            if context_size == 0:
                return result
            
            next_symbol_index = random.randint(0, context_size)
            for symbol_and_weight in self.__model_[context]:
                #print(symbol_and_weight, type(symbol_and_weight))
                symbol = symbol_and_weight
                weight = self.__model_[context][symbol]
                if next_symbol_index < weight:
                    result += symbol
                    context += symbol
                    context = context[1:]
                    break
                else:
                    next_symbol_index -= weight
        return result
        
    
    def __str__(self):
        return self.generate(8)