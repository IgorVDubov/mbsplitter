import collections
def middle(vars):
    '''
    бегущее среднее из MAX_VALUES значений
    STORED
        deque
    '''
    if vars.resultIn==None:
        vars.resultIn=0
    if not vars.deque:
        vars.deque=collections.deque([vars.resultIn for r in range(vars.MAX_VALUES)],vars.MAX_VALUES)
        
    vars.deque.append(vars.resultIn)
    vars.resultOut=sum(vars.deque)/vars.MAX_VALUES