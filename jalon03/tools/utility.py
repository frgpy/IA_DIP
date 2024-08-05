#!/usr/bin/env python3

__date__ = "26.01.24 16:30"
__update__ = "19.02.24 17:15"

def probability_vector(v1:float, v2:float, v3:float=0, v4:float=0) -> tuple:
    """ requires v_i in {-1} U [0,1]
        v1: probabilty of C given last my_action
        v2: probabilty of C given last adv_action
        v3: probabilty of R given last my_action
        v4: probabilty of R given last adv_action

       provides a 3 tuple (proba_C, proba_D, proba_R) with sum close to 1
    """
    def find_value(a:float, b:float) -> float:
        """ given two values decides what is the result """
        # no knowledge
        if a < 0 and b < 0: c = -1 # unable to find C probability
        # one is know, so take it
        elif a < 0: c = b
        elif b < 0: c = a
        else: c = a + b - a * b # both are known so p(Event1 and Event2)
        return c
    #1st find the C probability
    pC = find_value(v1, v2)
    # 2nd fix the R probability same approach
    pR = find_value(v3, v4)

    if v3 == 0 and v4 == 0: # no Renouncement available
        _rep = (.5, .5, 0) if pC == -1 else (pC, 1-pC, 0)
    else:
        if pC == -1 and pR == -1: _rep = (1/3, 1/3, 1/3)
        elif pC == -1: _rep = (1 - pR)/2, (1 -pR)/2, pR
        elif pR == -1: _rep = pC, (1 -pC)/2, (1 -pC)/2
        else: # pC is known, pR also we set pR assuming C is prior choice
            pR *= (1 -pC)
            _rep = pC, 1 - pC -pR, pR

    assert abs(round(sum(_rep), 7) -1) < 1e-5, f"bad vector {_rep}"
    return _rep

def update_storage(my_memory:str, reward:str, sz:int=2) -> str:
    """ Helper for 'Motif'
        given a current memory_word (my_memory), a new reward (reward) and
        a limited size (sz)
        return the new memory of len sz
    """
    return (my_memory+reward)[-sz:] if sz>0 else (my_memory+reward)

def backward_search(ze_memory:str) -> tuple:
    """ Helper for 'Motif'
        search the longuest pattern similar to ze_memory
        Iterative search
        1/ search those with the same last reward
        2/ there are more than one instance, look for one more letter

        provides a list of position and the size of the pattern

        the positions have same value as ze_memory[-1]
        the next position is the reward to check by adv_action
        the size helps to assert the quality of similarity
    """
    match = 0
    if len(ze_memory) < 2: return [], 0
    # memory is long enough to have patterns
    _idx = [ _ for _ in range(len(ze_memory)-1)
             if ze_memory[_] == ze_memory[-1] ]
    if _idx == []: return [], 0
    _szp = 1
    while len(_idx) > 1 and _szp < len(ze_memory):
        # select pattern similar with len _szp+1
        _old = _idx[:] # keep a safe copy
        _idx = [_ for _ in _old
                if _-_szp >=0 and ze_memory[_ - _szp] == ze_memory[-_szp -1]]
        _szp += 1

    if len(_idx) == 1: return (_idx, _szp)
    return _old, _szp-1 # faster than if _idx![]: _szp += 1

def adv_memory(ze_memory:str) -> str:
    """
    given our memory, provides the supposed memory of adv
    ensures len(adv_memory) == len(ze_memory)
    """
    return ''.join([{'T': 'S', 'S':'T'}.get(x, x)
                    for x in ze_memory])

if __name__ == '__main__':
    for meth in (probability_vector, update_storage, backward_search):
        print(f"{'='*7} {meth.__name__} {'='*7}")
        print(meth.__doc__)
        print(f"{'-'*77}")
