
def gridMvmnt(dec:bool, inc:bool, total:int, scale:int, snapSide:int, candec:bool, caninc:bool):

    #the bigger the scalar, the slower he glides
    slideRate = scale/150

    if inc and caninc:
        return scale/50
    elif dec and candec:
        return -scale/50
    elif total % scale > scale/25 or total % scale < -scale/25:
        if snapSide == 1:
            return (1 - ((total % scale)/scale))/slideRate
        else:
            return - ((total % scale)/scale)/slideRate
        
    elif total % scale != 0:

        if snapSide == 1:
            return scale - (total % scale)
        else:
            return - (total % scale)

    else:
        return 0
   

def snap(up:bool, down:bool, value:int):
    if up and value > 0:
        return -2
    elif down and value < 0:
        return 2
    else:
        return 0