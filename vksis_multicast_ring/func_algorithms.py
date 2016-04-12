def find_if(iterable,predicate):
    for el in iterable:
        if predicate(el) == True:
            return el
    return None

def find_if_not(iterable,predicate):
    for el in iterable:
        if not predicate(el) == True:
            return el
    return None 

def find_end_if(iterable,predicate):
    for el in reversed(iterable):
        if predicate(el) == True:
           return el
    return None

def find_end_if_not(iterable,predicate):
    for el in reversed(iterable):
        if not predicate(el) == True:
           return el
    return None

def for_each(iterable,func):
    for el in iterable:
        func(el)

    