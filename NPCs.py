
def NPS_says (words:str, font):
    return font.render(words, True, [250, 250, 250])

def interactPrompt (yes:bool, no:bool, ogVal:bool):
    if no:
        return False
    elif yes:
        return True
    else:
        return ogVal