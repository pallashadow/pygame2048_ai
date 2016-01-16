'''
written by pallashadow

based on pygame
http://www.pygame.org

algorithm inspired by
http://stackoverflow.com/questions/22342854/what-is-the-optimal-algorithm-for-the-game-2048
'''

#Import Modules
import os, pygame
from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'


import random
import copy
import math

def M2L(M):
    L=[]
    for r in range(4):
        L+=M[r]
    return L

def init():
    """
    initialize a 4*4 matrix of game state representation. 
    """
    
    M = [[0,0,0,0] for n in range(4)]
    r1 = random.randint(0,15)
    n1 = r1 / 4
    n2 = r1 % 4
    M[n1][n2] = 1
    return M

def genr(M):
    """
    add a 2 or 4 randomly to an empty tilt 
    """
    num = 1
    if random.random()<=0.1:
        num = 2
    L=M2L(M)
    I=[]
    for n in range(16):
        if L[n]==0:
            I.append(n)
    t1 = random.randint(0,len(I)-1)
    ins = I[t1]
    L[ins] = num
    for r in range(4):
        M[r] = [L[n] for n in range(0+4*r,4+4*r)]
    return M
        

def submove(MC):
    """
    move all of the rectangles to the left side of matrix
    if 2 tilt with same number met, they emerge and become a new tilt. 
    """
    S=[]
    M=[]
    for r in range(4):
        MC2=[]
        MC3=[]
        k=0
        for c in range(4):            
            if MC[r][c]!=0:
                MC2.append(MC[r][c])
                MC3.append([c,k,0])
                k+=1
        n=0
        align=0
        while n<len(MC2)-1:
            if MC2[n]==MC2[n+1]:                
                MC2[n]+=1
                MC2.pop(n+1)
                for k in range(n+1,len(MC3)):
                    MC3[k][1]-=1
            n+=1
        while len(MC2)<4:
            MC2.append(0)
        M.append(MC2)
        for i in MC3:
            S.append([r,i[0],i[0]-i[1]])
    return (M,S)


    

def up(M):
    MC = [[M[r][c] for r in range(4)] for c in range(4)]
    (MC,S) = submove(MC)
    M = [[MC[r][c] for r in range(4)] for c in range(4)]
    S2=[]
    for i in S:
        S2.append([i[1],i[0],i[2]])
        ## S2 is every movement of the rectangle.
        ## it is a list [x, y, distance_of_move]
        ## for example [1,2,1] means rectangle on row 1, collum 2, should move 1 tilt.
        ## this list S2 would only be used in pygame GUI
    return (M,S2)
                
def left(M):
    (M,S2) = submove(M)
    return (M,S2)

def right(M):
    MC = [[M[r][c] for c in [3,2,1,0]] for r in range(4)]
    (MC,S) = submove(MC)
    M = [[MC[r][c] for c in [3,2,1,0]] for r in range(4)]
    S2=[]
    for i in S:
        S2.append([i[0],3-i[1],i[2]])
    return (M,S2)

def down(M):
    MC = [[M[r][c] for r in [3,2,1,0]] for c in range(4)]
    (MC,S) = submove(MC)
    M = [[MC[r][c] for r in range(4)] for c in [3,2,1,0]]
    S2=[]
    for i in S:
        S2.append([3-i[1],i[0],i[2]])
    return (M,S2)

def move(M,r1):
    if r1==0:
        (M,S2)=up(M)
    elif r1==1:
        (M,S2)=down(M)
    elif r1==2:
        (M,S2)=left(M)
    elif r1==3:
        (M,S2)=right(M)
    return (M,S2)

def score_estimate(M):
    cost = 16
    L=M2L(M)
    score = 0
    for n in L:
        score+= (se.index(n)-1)*n
    return score



#########################################################





### ai


def ai_submove(MC):
    '''
    this funtion is a brief version of 'submove()'
    it does not calculate list S
    '''
    for r in range(4):
        MC2=[]
        for c in range(4):
            if MC[r][c]!=0:
                MC2.append(MC[r][c])
        n=0
        while n<len(MC2)-1:
            if MC2[n]==MC2[n+1]:
                MC2[n]+=1
                MC2.pop(n+1)
            n+=1
        while len(MC2)<4:
            MC2.append(0)
        MC[r]=MC2
    return MC


def ai_up(M):
    MC = [[M[r][c] for r in range(4)] for c in range(4)]
    MC = ai_submove(MC)
    M = [[MC[r][c] for r in range(4)] for c in range(4)]
    return M
                
def ai_left(M):
    M = ai_submove(M)
    return M

def ai_right(M):
    MC = [[M[r][c] for c in [3,2,1,0]] for r in range(4)]
    MC = ai_submove(MC)
    M = [[MC[r][c] for c in [3,2,1,0]] for r in range(4)]
    return M

def ai_down(M):
    MC = [[M[r][c] for r in [3,2,1,0]] for c in range(4)]
    MC = ai_submove(MC)
    M = [[MC[r][c] for r in range(4)] for c in [3,2,1,0]]
    return M

def ai_move(M,r1):
    if r1==0:
        M=ai_up(M)
    elif r1==1:
        M=ai_down(M)
    elif r1==2:
        M=ai_left(M)
    elif r1==3:
        M=ai_right(M)
    return M



def cascade(M):
    """
    as part of the cost function, 
    """
    
    cl=0
    cr=0
    cu=0
    cd=0
    even=0
    cost_diff=0
    for row in M:        
        for n in range(3):
            diff = row[n]-row[n+1]
            if diff>1:
                cl+=1
            elif diff<1:
                cr+=1
    MC = [[M[r][c] for r in range(4)] for c in range(4)]
    for row in MC: # collum in M
        for n in range(3):
            diff = row[n]-row[n+1]
            if diff>1:
                cu+=1
            elif diff<1:
                cd+=1
    cost_cluster = min(cl,cr)+min(cu,cd)
    cost_not_even = -even
    return (cost_cluster,cost_diff)

def neib(p1):
    #x=p1/4
    #y=p1%4
    N=[]
    if p1%4>=1:
        N.append(p1-1)
    if p1%4<=2:
        N.append(p1+1)
    if p1/4>=1:
        N.append(p1-4)
    if p1/4<=2:
        N.append(p1+4)
    return N

def cost_neib(M):
    L=M2L(M)
    K=[]
    cost_diff=0
    for i in range(16):
        K.append([L[i],i])
    K.sort(reverse=True)
    for n in range(5):
        p = K[n][1]
        diff = []
        for p1 in neib(p):
            if L[p1]<L[p]:
                diff.append(L[p]-L[p1])
        if diff:
            cost_diff+=min(diff)**2
        else:
            cost_diff = 3
    return cost_diff
                    

def cost_max_number_movement_penalty(M):
    L=M2L(M)
    maxpos = L.index(max(L))
    maxrow = maxpos%4
    maxcol = maxpos/4
    P= [0,0,0,0]
    if maxrow >1:
        P[2] = 1000
    else:
        P[3] = 1000
    if maxcol >1:
        P[0] = 1000
    else:
        P[1]= 1000
    return P
        
def cost(nextM):
    ## cost value of a state
    ## cost = non-empty + geography
    C=24
    M_cost=0
    L=M2L(nextM)
    ##L2=L[:]
    ##L2.sort()
    for n in L:
        M_cost+=n**2
    (cost1,cost2)=cascade(nextM)
    cost3 = cost_neib(nextM)
    C+=cost1+cost3+M_cost
        
    for n in range(len(L)):
        if L[n]!=0:
            C+=10
    if 2048 in L:
        C = 0            
    return C

def cost2(preM,m):
    C= 0
    nextM = copy.deepcopy(ai_move(preM,m))
    C+=cost(nextM)
    L1=M2L(preM)
    maxpos_pre = L1.index(max(L1))
    L2=M2L(nextM)
    maxpos_post = L2.index(max(L2))
    if maxpos_pre != maxpos_post:
        max_penalty=cost_max_number_movement_penalty(preM)
        C+=max_penalty[m]
    return C
    


def local_search1(M):
    predM1=[]
    for m in range(4):
        nextM = copy.deepcopy(ai_move(M,m)) # 4 next posible states
        #nextM = genr(nextM)
        predM1.append([m,nextM,cost2(M,m)]) # 4 states costs
    C=[]
    search_depth = 2
    for n in range(search_depth):
        predM2=[]
        for currentL3 in predM1:
            for m in range(4):
                prevai_move = currentL3[0]
                currentM = currentL3[1]
                baseline_cost = currentL3[2]
                nextM = copy.deepcopy(ai_move(currentM, m))
                #nextM = genr(nextM)
                
                nextcost = cost2(currentM,m) + baseline_cost
                predM2.append([m,nextM,nextcost])
                if n == search_depth-1:
                    C.append(nextcost)
        predM1=predM2
    t1 = C.index(min(C))
    themove = t1/4**search_depth
    #tree = copy.deepcopy(predM3[themove])
    return themove






###



#functions to create our resources
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

class Rect1(pygame.sprite.Sprite):
    def __init__(self, index, num):
        pos = (120,120)
        pos0= (200,70)
        self.index = index
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image(os.getcwd()+'/img/'+str(num)+'.png', -1)
        self.rect.midtop = ((index%4)*pos[0]+pos0[0],(index/4)*pos[1]+pos0[1])

    def update(self,S):
        "move the fist based on the mouse position"
        pos = self.rect.midtop
        index = self.index
        mx=0
        my=0
        for s in S:
            if s[0]==index:
                mx = s[1][0]
                my = s[1][1]
        self.rect.move_ip(mx,my)
        





def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
#Initialize Everything
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('hehe')
    pygame.mouse.set_visible(0)

#Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

#Put Text On The Background, Centered
    if pygame.font:
        font = pygame.font.Font(None, 36)
        text = font.render("2048 game, press 'a' for AI move", 1, (10, 10, 10))
        textpos = text.get_rect(centerx=background.get_width()/2)
        background.blit(text, textpos)

#Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

#Prepare Game Objects
    pygame.time.wait(200)
    M = init()
    M = [[1,2,3,4],[2,2,3,4],[0,0,0,0],[0,0,0,0]]
    L=[]
    for i in range(4):
        L+=M[i]
    clock = pygame.time.Clock()
    Rects = pygame.sprite.Group()
    for i in range(16):
        if L[i]!=0:
            Rects.add(Rect1(i,L[i]))

#Main Loop
    j=0
    dist = 3
    S2=[]
    mv = 5
    
    while 1:
        #clock.tick(60)
        j+=1
    #Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                keys = (0,0)*(324/2)
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_LEFT or event.key == K_RIGHT or event.key ==K_UP or event.key == K_DOWN:    
                    keys = pygame.key.get_pressed()
                    if keys[K_LEFT]:
                        mv=2
                    elif keys[K_RIGHT]:
                        mv=3
                    elif keys[K_UP]:
                        mv=0
                    elif keys[K_DOWN]:
                        mv=1
                elif event.key == K_a:
                    M1=copy.deepcopy(M)
                    mv = local_search1(M)
                    M=M1

                        
                if mv==2:
                    (M,S2)=left(M)
                    dirct= (-1,0)
                elif mv==3:
                    (M,S2)=right(M)
                    dirct = (1,0)
                elif mv==0:
                    (M,S2)=up(M)
                    dirct = (0,-1)
                elif mv==1:
                    (M,S2)=down(M)
                    dirct = (0,1)
                movelist = []
                for s in S2:
                    dirct1 = (s[2]*dirct[0]*dist,s[2]*dirct[1]*dist)
                    movelist.append([s[0]*4+s[1],dirct1])
        # move
                for i in range(120/dist):
                    Rects.update(movelist)
                    #pygame.time.wait(1)
                    screen.blit(background, (0, 0))
                    Rects.draw(screen)
                    pygame.display.update()
        # Reload
                pygame.time.wait(100)
                try:
                    M = genr(M)
                except:
                    print 'gameover'
                    return
                Rects = pygame.sprite.Group()
                L=M2L(M)
                for i in range(16):
                    if L[i]!=0:
                        Rects.add(Rect1(i,L[i]))
                screen.blit(background, (0, 0))
                Rects.draw(screen)
                pygame.display.update()
                

#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()



        
