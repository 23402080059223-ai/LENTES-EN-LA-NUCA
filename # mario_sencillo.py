# mario_sencillo.py
import pygame
import sys

# ────────────────────────────────────────────────
# 1. Configuración inicial
# ────────────────────────────────────────────────
pygame.init()

ANCHO = 800
ALTO  = 600
FPS   = 60

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Mini Mario Bros - Tutorial")
reloj = pygame.time.Clock()

# Colores
ROJO = (255, 255, 255)
AZUL   = (135, 206, 235)
VERDE  = (100, 230, 100)
ROJO   = (220, 20, 60)
AMARILLO = (255, 215, 0)

fuente = pygame.font.SysFont("arial", 28)

# ────────────────────────────────────────────────
# 2. Clase Jugador (Mario)
# ────────────────────────────────────────────────
class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill((255, 100, 100))           # Mario rojo temporal
        pygame.draw.circle(self.image, (255,200,150), (20,20), 15)  # cara
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = ALTO - 200
        
        # Física
        self.vel_x = 0
        self.vel_y = 0
        self.en_suelo = False
        self.vida = 3
        self.puntos = 0

    def update(self, plataformas):
        # Gravedad
        self.vel_y += 0.8          # gravedad
        if self.vel_y > 12:
            self.vel_y = 12

        # Movimiento horizontal
        self.rect.x += self.vel_x

        # Colisión horizontal con plataformas
        for plat in plataformas:
            if self.rect.colliderect(plat.rect):
                if self.vel_x > 0:
                    self.rect.right = plat.rect.left
                if self.vel_x < 0:
                    self.rect.left = plat.rect.right

        # Movimiento vertical
        self.rect.y += self.vel_y

        # Colisión vertical
        self.en_suelo = False
        for plat in plataformas:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0:   # cayendo
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.en_suelo = True
                if self.vel_y < 0:   # subiendo y choca techo
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0

    def saltar(self):
        if self.en_suelo:
            self.vel_y = -14
            self.en_suelo = False


# ────────────────────────────────────────────────
# 3. Plataforma simple
# ────────────────────────────────────────────────
class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, ancho, alto):
        super().__init__()
        self.image = pygame.Surface((ancho, alto))
        self.image.fill(VERDE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# ────────────────────────────────────────────────
# 4. Moneda
# ────────────────────────────────────────────────
class Moneda(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(self.image, AMARILLO, (12,12), 12)
        pygame.draw.circle(self.image, (255,180,0), (12,12), 8)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


# ────────────────────────────────────────────────
# 5. Grupos de sprites
# ────────────────────────────────────────────────
todos_sprites = pygame.sprite.Group()
plataformas   = pygame.sprite.Group()
monedas       = pygame.sprite.Group()

jugador = Jugador()
todos_sprites.add(jugador)

# Creamos algunas plataformas
suelo = Plataforma(0, ALTO-40, ANCHO*3, 40)          # suelo largo
plat1 = Plataforma(280, 420, 180, 30)
plat2 = Plataforma(580, 320, 140, 30)
plat3 = Plataforma(900, 380, 200, 30)

for p in [suelo, plat1, plat2, plat3]:
    todos_sprites.add(p)
    plataformas.add(p)

# Algunas monedas
for x in [340, 380, 420, 640, 680, 950, 980, 1010]:
    moneda = Moneda(x, 300 if x < 500 else 250)
    todos_sprites.add(moneda)
    monedas.add(moneda)


# ────────────────────────────────────────────────
# 6. Variables del juego
# ────────────────────────────────────────────────
camara_x = 0
velocidad_juego = 5

# ────────────────────────────────────────────────
# 7. Bucle principal
# ────────────────────────────────────────────────
corriendo = True

while corriendo:
    reloj.tick(FPS)

    # ── Eventos ────────────────────────────────
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                jugador.saltar()

    # ── Teclas presionadas ─────────────────────
    teclas = pygame.key.get_pressed()
    jugador.vel_x = 0

    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        jugador.vel_x = velocidad_juego
    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        jugador.vel_x = -velocidad_juego

    # ── Actualizar ─────────────────────────────
    jugador.update(plataformas)

    # Recolectar monedas
    recolectadas = pygame.sprite.spritecollide(jugador, monedas, True)
    jugador.puntos += len(recolectadas) * 100

    # Cámara sigue al jugador (scrolling)
    if jugador.rect.x - camara_x > ANCHO * 0.6:
        camara_x = jugador.rect.x - ANCHO * 0.6
    if jugador.rect.x - camara_x < ANCHO * 0.4:
        camara_x = jugador.rect.x - ANCHO * 0.4

    camara_x = max(0, camara_x)   # no retroceder más allá del inicio

    # ── Dibujar ────────────────────────────────
    pantalla.fill(AZUL)  # cielo

    # Dibujamos todo con offset de cámara
    for sprite in todos_sprites:
        pantalla.blit(sprite.image, (sprite.rect.x - camara_x, sprite.rect.y))

    # HUD
    texto_puntos = fuente.render(f"Puntos: {jugador.puntos}", True, ROJO)
    pantalla.blit(texto_puntos, (20, 20))

    pygame.display.flip()

pygame.quit()
sys.exit()