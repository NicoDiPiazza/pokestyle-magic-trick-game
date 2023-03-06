import pygame


def townHUD  (surfc, surfcW, surfcH, font):
    pygame.draw.rect(surfc, [128,150,200], [0, 0, surfcW * 0.2, surfcH * 0.1])
    smallFont = pygame.font.SysFont('arial', 17)
    inventory_message = smallFont.render('press i for inventory', True, [250, 250, 250])
    surfc.blit(inventory_message, [surfcW * 0.02, surfcH * 0.03])


def battleHUD  (surfc, surfcW, surfcH, font, selfHP:int, selfAP:int):
    pygame.draw.rect(surfc, [128,150,200], [0, 0, surfcW * 0.2, surfcH * 0.1])
    smallFont = pygame.font.SysFont('arial', 17)
    inventory_message = smallFont.render('press i for inventory', True, [250, 250, 250])
    surfc.blit(inventory_message, [surfcW * 0.02, surfcH * 0.03])

    #bottom display
    pygame.draw.rect(surfc, [200,200,200], [surfcW * 0.1, surfcH * 0.8, surfcW * 0.8, surfcH * 0.2])
    #HP and AP meter
        # HP
    pygame.draw.rect(surfc, [100,100,100], [surfcW * 0.15, surfcH * 0.85, surfcW * 0.30, surfcH * 0.03])
    pygame.draw.rect(surfc, [200, 0, 0], [surfcW * 0.16, surfcH * 0.855, surfcW * 0.28 * (selfHP/100), surfcH * 0.020])

        #AP
    pygame.draw.rect(surfc, [100,100,100], [surfcW * 0.55, surfcH * 0.85, surfcW * 0.30, surfcH * 0.03])
    pygame.draw.rect(surfc, [0, 0, 200], [surfcW * 0.56, surfcH * 0.855, surfcW * 0.28 * (selfAP/100), surfcH * 0.020])

    leave_message = smallFont.render("keep at it or run? (k/r)", True, [250, 250, 250])
    surfc.blit(leave_message, [surfcW * 0.2, surfcH * 0.95])
