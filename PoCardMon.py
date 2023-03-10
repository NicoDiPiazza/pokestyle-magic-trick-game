import pygame
import random
import numpy as np
import gridMovement
import NPCs
import HUDs

from math import floor
pygame.init()
pygame.font.init()

pigcake_sprite_1 = pygame.image.load('pigcake_sprite_1.png')
#rato is 1472/2849 (x / y)
pigcake_sprite_1 = pygame.transform.scale(pigcake_sprite_1, (200, 200*(2849/1472)))

screenWidth = 1000
screenHeight = 750
screen = pygame.display.set_mode([screenWidth, screenHeight])
pygame.event.get()
keys = pygame.key.get_pressed()

## class definitions

class Enemy():
    def __init__(self, HP:int, loot:int, level:int):
        self.HP = HP
        self.loot = loot
        self.level = level

class Boss(Enemy):
    def __init__(self, name:str, moveset:list):
        self.name = name
        self.moveset = moveset

class Trick():
    def __init__(self, name:str, level:str, strength:int, type:str, needsPrep:bool, description:str):
        #name: what the trick is called
        #level: common, rare, super rare, legendary
        #strength: is multipled by character level to produce total strength
        #type: sleight(attack), gimmick(defense), flourish(nerf), selfWorking(buff)
        #needsPrep: whether or not the trick requires a prepared deck
        self.name = name
        self.level = level
        self.strength = strength
        self.tye = type
        self.needsPrep = needsPrep
        self.description = description
        


#refresh rate of the screen
dt = 5
#size of each square of the invisible grid that everything is on
gridSize = 50
# the pixel offsets in the x an y letting the environment know where to be in relation to the player
offsetX = 0
offsetY = 0
# where to position the player on the screen
playerX = screenWidth / 2
playerY = screenHeight / 2
# where the player is on the invisible grid
playerMatrixPos = [9, 7]
#whether to coast right or left, up or down when the player lets go of the keys
snapX = 1
snapY = 1

# level design layout matrix (columns and rows are flipped, frustratingly. so what looks vertical is horizontal)
# key: 0: open space
#       1: player
#       2: wall
#       3: NPC
#       4: interact location
# there must be walls at least one grid space within the ounds so that the movement checks don't break
designM = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 4, 2, 2, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 2, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

# font initialization
main_font = pygame.font.SysFont('arial', 25)
writeMessage = False
currentText = ''

#what state the game is in
stocking = False
fighting = False
inventory = False
fightPhase = 0
enemyTrickNum = 0
playerTrickNum = 0
playerTricks = [0, 0, 0]
selectedTrick = 0
actionChosen = False
possibilitiesSet = False
onAction = 0
damageDealt = True
timer = 0

# player resource values
playerHPBase = 100
playerAP = 100
playerLevel = 1
playerMoney = 0
playerHP = playerHPBase * playerLevel

# List of all tricks
    #legendary tricks
acan = Trick('acan', 'legendary', 10, 'sleight', False, 'You find their chosen card at their chosen number.')
threeCardMonteClip = Trick('three card monte with a clip', 'legendary', 9, 'sleight', False, 'Like three card monte, but this time the ace has a clip on it.')
primeShadowSpring = Trick('prime shadow spring', 'legendary', 9, 'sleight', False, 'You bring the selected card to any spot in the deck.')
    #rare tricks
threeCardMonte = Trick('three card monte', 'rare', 7, 'sleight', False, 'You only have three cards, but the ace is never where they think.')
movingHole = Trick('moving hole', 'rare', 7, 'gimmick', False, 'You move a hole in a card to different places on the card.')
disappearingBox = Trick('disappearing box', 'rare', 6, 'gimmick', False, 'A card box in your palm vanishes.')
backInOrder = Trick('back in order', 'rare', 5, 'sleight', True, 'You shuffle and cut the deck several times, but it ends up in perfect order.')
anacondaDribble = Trick('anaconda dribble', 'rare', 7, 'flourish', False, 'You dribble the cards from one hand across your body to the other.')
faroShuffle = Trick('Faro shuffle', 'rare', 6, 'flourish', False, 'You perfectly interlace the cards just by pushing the halves toward each other.')
appearingAces = Trick('appearing aces', 'rare', 8, 'sleight', False, 'The aces appear on the table one by one.')
sstKS = Trick('673 King Street', 'rare', 7, 'sleight', True, 'You tell a story where the next card alwasy matches the next story beat, despite shuffles and cuts.')
toPocket = Trick('card to pocket', 'rare', 8, 'self working', False, 'Their card appears in their own pocket.')
colorChangingDeck = Trick('color changing deck', 'rare', 6, 'sleight', True, 'The deck changes color.')
    #common tricks
dealARoyalFlush = Trick('deal a royal flush', 'common', 5, 'self working', True, 'In 1V1 poker, they deal you a royal flush without knowing it.')
instantJump = Trick('instant jump', 'common', 3, 'sleight', False, 'Their card is shuffled into the middle, but you bring it to the top.')
cutAces = Trick('cut the aces', 'common', 2, 'sleight', True, 'You cut the deck four times, each time finding an ace.')
levitatingCard = Trick('levitating card', 'common', 4, 'gimmick', False, 'You levitate a card between your hands without touching it.')
vernonsTriumph = Trick("Vernon's triumph", 'common', 3, 'self working', False, 'The cards alternate face up and down, but when spread, are all face up.')
countToCard = Trick('count to the card', 'common', 6, 'sleight', False, 'you count to their selected card based on the number of cards they cut off.')
russianPyramid = Trick('russian pyramid', 'common', 5, 'flourish', False, 'You cut the cards among your hands till they make a tiered pyramid.')
sybilCut = Trick('Sybil cut', 'common', 4, 'flourish', False, 'You cut the cards around your hands, extending toward them, before closing.')
tornAndRestored = Trick('torn & restored', 'common', 5, 'gimmick', False, 'You restore a torn corner of a card.')
predictionCard = Trick('prediction card', 'common', 6, 'sleight', False, 'The card in the envelope matches the selected card.')
oilAndWater = Trick('oil & water', 'common', 4, 'sleight', False, 'no matter how much you mix the black and red cards, they always separate.')
invisiblePalm = Trick('invisible palm', 'common', 5, 'sleight', False, 'You showed a palmed a card, then it goes invisible, before appearing with the rest.')
throw = Trick('throw', 'common', 6, 'flourish', False, 'You throw a card like Gambit from the X-Men.')
xrayVis = Trick('X-ray vision', 'common', 3, 'self working', False, 'You manage to accurately guess all three of the top cards from 2 cuts.')
instantSpell = Trick('instant spell', 'common', 4, 'self working', False, 'you count to their card using the name of the top card of the deck.')
cardiniChange = Trick('cardini change', 'common', 4, 'sleight', False, 'You change the card on top of the deck to another card.')
    #simple tricks
keyCard = Trick('key card', 'simple', 1, 'self working', True, 'you find their card after it is cut into the deck.')
theyCutAces = Trick('they cut the aces', 'simple', 3, 'self working', True, 'They cut to the four aces without knowing it.')
charlierCut = Trick('Charlier cut', 'simple', 2, 'flourish', False, 'you cut the cards one-handed')
fiveMinds = Trick('read 5 minds at once', 'simple', 3, 'self working', False, 'You find five different cards in the order they were chosen.')
pythagRule = Trick('pythagorean rule', 'simple', 1, 'self working', True,  'The suit of one selected card and the value of the other always make the third.')
lazyMagician = Trick('lazy magician', 'simple', 3, 'self working', True, 'They put their card in the deck and cut it, but you know how many cards from the top it is.')
flickChange = Trick('flick change', 'simple', 2, 'sleight', False, 'You flick a card and it changes to another.')
orbit = Trick('orbit', 'simple', 1, 'flourish', False, 'you obit the top card around the deck using one hand.')
jimmyWoo = Trick('James E. Woo production', 'simple', 1, 'sleight', False, 'You pull a card out of the air.')
trap = Trick('trap', 'simple', 2, 'self working', False, 'Their cards jump out of the deck, despite a rubber band keeping them in.')
faceUp = Trick('face up', 'simple', 2, 'self working', False, 'Only their card is face up in the deck.')
walletPrediction = Trick('wallet prediction', 'simple', 2, 'self working', False, 'the prediction in the wallet matches the selected card.')
cutCorners = Trick('cut corners', 'simple', 2, 'gimmick', False, 'You cut to their card after it is shuffled into the deck.')
pbEffect = Trick('P. B. effect', 'simple', 7, 'flourish', False, 'You go through many elaborate steps only to completely guess the wrong card.')
mindMelter = Trick('mind-melter', 'simple', 3, 'self working', False, 'You find their card after many cuts and shuffles.')

allTricks = [acan, threeCardMonteClip, primeShadowSpring, threeCardMonte, movingHole, disappearingBox, backInOrder, anacondaDribble, faroShuffle, appearingAces, sstKS,\
             toPocket, colorChangingDeck, dealARoyalFlush, instantJump, cutAces, levitatingCard, vernonsTriumph, countToCard, russianPyramid, sybilCut, tornAndRestored,\
                predictionCard, oilAndWater, invisiblePalm, throw, xrayVis, instantSpell, cardiniChange, keyCard, theyCutAces, charlierCut, fiveMinds, pythagRule, lazyMagician,\
                    flickChange, orbit, jimmyWoo, trap, faceUp, walletPrediction, cutCorners, pbEffect, mindMelter]

legendaryTricks = [acan, threeCardMonteClip, primeShadowSpring]
rareTricks = [threeCardMonte, movingHole, disappearingBox, backInOrder, anacondaDribble, faroShuffle, appearingAces, sstKS, toPocket, colorChangingDeck]
commonTricks = [dealARoyalFlush, instantJump, cutAces, levitatingCard, vernonsTriumph, countToCard, russianPyramid, sybilCut, tornAndRestored, predictionCard,\
                 oilAndWater, invisiblePalm, throw, xrayVis, instantSpell, cardiniChange]
simpleTricks = [keyCard, theyCutAces, charlierCut, fiveMinds, pythagRule, lazyMagician, flickChange, orbit, jimmyWoo, trap, faceUp, walletPrediction, cutCorners,\
                 pbEffect, mindMelter]

knownTricks = np.zeros((len(allTricks),), dtype = int)

# main game loop
while (keys[pygame.K_q] != True):
    #refreshing the screen and text every frame
    screen.fill([200, 200, 200])
    writeMessage = False
    currentText = ''
    #taking the player input
    pygame.event.get()
    keys = pygame.key.get_pressed()
    
    #this is the loop for when one is just wandering around
    if stocking != True and fighting != True and inventory != True:
        canRight = designM[playerMatrixPos[0]+1][playerMatrixPos[1]] == 0
        canLeft = designM[playerMatrixPos[0] - 1][playerMatrixPos[1]] == 0
        canUp = designM[playerMatrixPos[0]][playerMatrixPos[1] - 1] == 0
        if snapY == 1:
            canDown = designM[playerMatrixPos[0]][playerMatrixPos[1] + 1] == 0
        else:
            canDown = designM[playerMatrixPos[0]][playerMatrixPos[1] + 2] == 0 and designM[playerMatrixPos[0]][playerMatrixPos[1] + 1] == 0

        offsetX = offsetX + gridMovement.gridMvmnt(keys[pygame.K_d], keys[pygame.K_a], offsetX, gridSize, snapX, canRight, canLeft)
        snapX = snapX + gridMovement.snap(keys[pygame.K_d], keys[pygame.K_a], snapX)

        offsetY = offsetY + gridMovement.gridMvmnt(keys[pygame.K_s], keys[pygame.K_w], offsetY, gridSize, snapY, canDown, canUp)
        snapY = snapY + gridMovement.snap(keys[pygame.K_s], keys[pygame.K_w], snapY)

        # calculating the player new position
        
        playerMatrixPos = [floor((-offsetX + (0.5 * screenWidth) + gridSize/2)/gridSize) - 1, floor((-offsetY + 0.5 * screenHeight + gridSize/2)/gridSize) - 1]
        

        # putting in the objects in the level
        for i in range(len(designM)):
            for j in range(len(designM[i])):
                if designM[i][j] == 2:
                    pygame.draw.rect(screen, [250, 250, 0], [(gridSize * (i + 0.5)) + offsetX, (gridSize * j) + offsetY, gridSize, gridSize])
                if designM[i][j] == 3:
                    pygame.draw.rect(screen, [0, 250, 0], [(gridSize * (i + 0.5)) + offsetX, (gridSize * j) + offsetY, gridSize, gridSize])
                    
                    if (playerMatrixPos[0] + 1 == i and playerMatrixPos[1] == j) or (playerMatrixPos[0] - 1 == i and playerMatrixPos[1] == j) or (playerMatrixPos[1] + 1 == j and playerMatrixPos[0] == i) or (playerMatrixPos[1] - 1 == j and playerMatrixPos[0] == i):
                        writeMessage = True
                        currentText = NPCs.NPS_says("I'm an NPC! Fight me? (y/n)", main_font)
                        fighting = NPCs.interactPrompt(keys[pygame.K_y], keys[pygame.K_n], fighting)
                        if fighting:
                            currentEnemy = Enemy(10, 10, 1)
                if designM[i][j] == 4:
                    pygame.draw.rect(screen, [0, 0, 250,], [(gridSize * (i + 0.5)) + offsetX, (gridSize * j) + offsetY, gridSize, gridSize])
                    
                    if (playerMatrixPos[0] + 1 == i and playerMatrixPos[1] == j) or (playerMatrixPos[0] - 1 == i and playerMatrixPos[1] == j) or (playerMatrixPos[1] + 1 == j and playerMatrixPos[0] == i) or (playerMatrixPos[1] - 1 == j and playerMatrixPos[0] == i):
                        writeMessage = True
                        currentText = NPCs.NPS_says("Enter de sh0p (y/n)", main_font)
                        stocking = NPCs.interactPrompt(keys[pygame.K_y], keys[pygame.K_n], stocking)

        #drawing the player onto the scene                
        pygame.draw.circle(screen, [255, 0, 0], [playerX, playerY], gridSize/2)

        #letting the player open inventory whenever
        inventory = NPCs.interactPrompt(keys[pygame.K_i], False, inventory)

        #the heads up display for just wandering around
        HUDs.townHUD(screen, screenWidth, screenHeight, main_font, playerMoney)

        #monitoring the grid location of the player (not neccessary)
        print(playerMatrixPos)

    elif stocking and True != inventory:
        
        
        writeMessage = True
        currentText = NPCs.NPS_says("Continue shopping or leave? (c/l)", main_font)
        stocking = NPCs.interactPrompt(keys[pygame.K_c], keys[pygame.K_l], stocking)
        inventory = NPCs.interactPrompt(keys[pygame.K_i], False, inventory)

    elif fighting and True != inventory:
        
        fighting = NPCs.interactPrompt(keys[pygame.K_k], keys[pygame.K_r], fighting)
        selectedTrick = playerTricks[0]
        if fightPhase == 0:
            if possibilitiesSet == False:
                #making the matrix of tricks for the player, and choosing one for the enemy
                for i in range(len(playerTricks)):
                    playerTricks[i] = allTricks[random.randint(0, len(allTricks) - 1)]
                    enemyTrick = allTricks[random.randint(0, len(allTricks) - 1)]
                possibilitiesSet = True
                #selecting your Trick
            if keys[pygame.K_a]:
                onAction = 0
            elif keys[pygame.K_s]:
                onAction = 1
            elif keys[pygame.K_d]:
                onAction = 2
            #moving to the next phase and finalizing things from the last one. Also resetting stuff so it's ready to go again next round
            if keys[pygame.K_w]:
                possibilitiesSet = False
                playerTrickNum = onAction
                fightPhase = fightPhase + 1
        elif fightPhase == 1:
            if timer >= dt * 40:
                fightPhase = fightPhase + 1
                damageDealt = False
                timer = 0
            else:
                timer = timer + 1
        elif fightPhase == 2:
            #resolving the effects of all the actions
            if damageDealt != True:
                playerHP = playerHP - enemyTrick.strength
                currentEnemy.HP = currentEnemy.HP - selectedTrick.strength
                playerAP = playerAP - 1
            damageDealt = True
            if timer >= dt * 40:
                fightPhase = 0
                timer = 0
            else:
                timer = timer + 1

        selectedTrick = playerTricks[playerTrickNum]
        #if the player wins the battle...
        if currentEnemy.HP <= 0:
            fighting = False
            fightPhase = 0
            playerMoney = playerMoney + currentEnemy.loot

        # if the player loses the battle...
        if playerHP <= 0:
            fighting = False
            fightPhase = 0
            offsetX = 0
            offsetY = 0
            playerHP = playerHPBase * playerLevel
        #making sure the player can still access the inventory, even in battle
        inventory = NPCs.interactPrompt(keys[pygame.K_i], False, inventory)
        screen.blit(pigcake_sprite_1, (screenWidth * 0.65, screenHeight * 0.15))
        HUDs.battleHUD(screen, screenWidth, screenHeight, main_font, playerHP, playerAP, fightPhase, enemyTrick.name, enemyTrick.strength, selectedTrick.description, selectedTrick.strength, playerTricks, onAction)
    
    elif inventory:
        
        writeMessage = True
        currentText = NPCs.NPS_says("ready to go? (y/n)", main_font)
        inventory = NPCs.interactPrompt(keys[pygame.K_n], keys[pygame.K_y], inventory)



# popup messages
    if writeMessage:
        pygame.draw.rect(screen, [128,128,128], [screenWidth * 0.1, screenHeight * 0.8, screenWidth * 0.7, screenHeight * 0.5])
        screen.blit(currentText, [screenWidth * 0.3, screenHeight * 0.85])
    pygame.time.delay(dt)
    pygame.display.update()

