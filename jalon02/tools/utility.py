#!/usr/bin/env python3

__date__ = "26.01.24 16:30"

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
