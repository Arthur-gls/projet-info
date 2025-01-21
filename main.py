import pygame as pg

pg.init()
screen = pg.display.set_mode((400, 400))
clock = pg.time.Clock()

# CONSTANTES

width = 40 # largeur du rectangle en pixels
height = 40 # hauteur du rectangle en pixels
white = (255, 255, 255) # couleur blanche
black=(0,0,0)
l,L=10,10
size=40


def act_event(running,event):
    # chaque évênement à un type qui décrit la nature de l'évênement
    # un type de pg.QUIT signifie que l'on a cliqué sur la "croix" de la fenêtre
    if event.type == pg.QUIT:
        running = False
    # un type de pg.KEYDOWN signifie que l'on a appuyé une touche du clavier
    elif event.type == pg.KEYDOWN:
        if event.key == pg.K_q:
            running = False
    return running

def damier(w,h,color,size,l,L):
    for x in range(l):
        if x%2==0:
            for y in range(L//2+1):
                x2=x*size
                y2=y*size*2
                rect = pg.Rect(x2, y2, w, h)
                pg.draw.rect(screen, color, rect)
        else:
            for y in range(L//2+1):
                x2=x*size
                y2=y*size*2+size
                rect = pg.Rect(x2, y2, w, h)
                pg.draw.rect(screen, color, rect)



# on rajoute une condition à la boucle: si on la passe à False le programme s'arrête
running = True

while running :
    screen.fill(white)
    clock.tick(1)


    # on itère sur tous les évênements qui ont eu lieu depuis le précédent appel
    # ici donc tous les évènements survenus durant 0.2 seconde précédente

    for event in pg.event.get():
        running=act_event(running,event)

    # on construit le damier

    damier(width,height,black,size,l,L)

    pg.display.update()




# Enfin on rajoute un appel à pg.quit()
# Cet appel va permettre à Pygame de "bien s'éteindre" et éviter des bugs sous Windows

pg.quit()
