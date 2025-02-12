import sys, pygame, os, math
from pygame.locals import *
import cards
import random
from openai import OpenAI

pygame.init()

ANCHO, ALTO = 1920, 1080
ANCHO_CARTA, ALTO_CARTA = 120, 180
RADIO = 400

tamanio = ANCHO, ALTO
pantalla = pygame.display.set_mode(tamanio, pygame.FULLSCREEN)
pygame.display.set_caption("Solitario del Reloj 0.1 beta")

BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# Ajusta el centro del reloj para que esté más centrado verticalmente
CENTRO_X, CENTRO_Y = ANCHO // 2, ALTO // 2 - 100

# Desplaza las posiciones una a la derecha
posicion_hora = [
    (
        CENTRO_X + RADIO * math.cos((i + 1) * (2 * math.pi / 12) - math.pi / 2),
        CENTRO_Y + RADIO * math.sin((i + 1) * (2 * math.pi / 12) - math.pi / 2)
    )
    for i in range(12)
]
posicion_hora.append((CENTRO_X, CENTRO_Y))

imagen_fondo = pygame.image.load(os.path.join("Sprites", "fondo.jpg"))
imagen_fondo = pygame.transform.scale(imagen_fondo, (ANCHO, ALTO))

lista_horas = {simbolo: i for i, simbolo in
               enumerate(['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'])}


pygame.mixer.init()
sonido_barajear = pygame.mixer.Sound("Sprites/sounds/shuffling-cards-2.wav")
sonido_repartir = pygame.mixer.Sound("Sprites/sounds/repartir.mp3")

pygame.mixer.music.load("Sprites/sounds/musica_fondo.mp3")
pygame.mixer.music.play(-1)  # -1 para que la música se reproduzca en bucle
pygame.mixer.music.set_volume(0.2)  # Ajusta el volumen al 50%

def cargar_imagenes_cartas():
    dir_sprites = "Sprites"
    for nombre_archivo in os.listdir(dir_sprites):
        if nombre_archivo.endswith(".png"):
            nombre, _ = nombre_archivo.split(".")
            imagen = pygame.image.load(os.path.join(dir_sprites, nombre_archivo))
            cards.imagenes_cartas[nombre] = pygame.transform.scale(imagen, (ANCHO_CARTA, ALTO_CARTA))

    cards.carta_atras = cards.imagenes_cartas.get("atras", pygame.Surface((ANCHO_CARTA, ALTO_CARTA)))
    if "atras" not in cards.imagenes_cartas:
        cards.carta_atras.fill(NEGRO)


cargar_imagenes_cartas()


def animar_barajeo(mazo, duracion=2000):
    reloj = pygame.time.Clock()
    tiempo_inicial = pygame.time.get_ticks()
    pos_centro_arriba = (CENTRO_X, ALTO // 4)
    pos_centro_abajo = (CENTRO_X, ALTO - ALTO_CARTA // 2)
    mitad = len(mazo) // 2
    izquierda = mazo[:mitad]
    derecha = mazo[mitad:]

    # Reproducir sonido de barajear
    sonido_barajear.play()

    while True:
        tiempo_actual = pygame.time.get_ticks()
        tiempo_transcurrido = tiempo_actual - tiempo_inicial
        if tiempo_transcurrido >= duracion:
            break
        t = tiempo_transcurrido / duracion
        pantalla.blit(imagen_fondo, (0, 0))

        # Animar las cartas del montículo izquierdo
        for i, carta in enumerate(izquierda):
            x = pos_centro_arriba[0] - 50 * (1 - t) + (random.random() - 0.5) * 20
            y = pos_centro_arriba[1] + (pos_centro_abajo[1] - pos_centro_arriba[1]) * t + (random.random() - 0.5) * 20
            pantalla.blit(carta.carta, (x, y))

        # Animar las cartas del montículo derecho
        for i, carta in enumerate(derecha):
            x = pos_centro_arriba[0] + 50 * (1 - t) + (random.random() - 0.5) * 20
            y = pos_centro_arriba[1] + (pos_centro_abajo[1] - pos_centro_arriba[1]) * t + (random.random() - 0.5) * 20
            pantalla.blit(carta.carta, (x, y))

        pygame.display.flip()
        reloj.tick(60)

    # Dibujar las cartas en el centro al final de la animación de barajear
    pantalla.blit(imagen_fondo, (0, 0))
    for carta in mazo:
        pantalla.blit(carta.carta, pos_centro_abajo)
    pygame.display.flip()

def repartir_cartas(mazo, duracion=250):
    global reloj
    reloj = [[] for _ in range(13)]  # Reinicia las pilas del reloj
    pos_centro_abajo = (CENTRO_X, ALTO - ALTO_CARTA // 2)

    # Dibujar las cartas en el centro antes de comenzar la animación de repartir
    pantalla.blit(imagen_fondo, (0, 0))
    for carta in mazo:
        pantalla.blit(carta.carta, pos_centro_abajo)
    pygame.display.flip()

    for i, carta in enumerate(mazo):
        pila_destino = i % 13  # Calcula a cuál pila pertenece la carta
        pos_final = posicion_hora[pila_destino]

        # Anima el movimiento de la carta desde el centro hacia su posición final
        animar_movimiento(carta, pos_centro_abajo, pos_final, duracion=duracion)

        # Reproducir sonido de repartir
        sonido_repartir.play()

        # Agrega la carta a la pila correspondiente
        reloj[pila_destino].append(carta)
        carta.ocultar()  # Oculta la carta inicialmente

    # Muestra la carta superior en la posición 12
    if reloj[12]:
        reloj[12][0].mostrar()

def animar_movimiento(carta, pos_inicial, pos_final, duracion=250):
    reloj = pygame.time.Clock()
    tiempo_inicial = pygame.time.get_ticks()
    while True:
        tiempo_actual = pygame.time.get_ticks()
        tiempo_transcurrido = tiempo_actual - tiempo_inicial
        if tiempo_transcurrido >= duracion:
            break
        t = tiempo_transcurrido / duracion
        x = pos_inicial[0] + t * (pos_final[0] - pos_inicial[0])
        y = pos_inicial[1] + t * (pos_final[1] - pos_inicial[1])

        pantalla.blit(imagen_fondo, (0, 0))  # Redibuja el fondo
        dibujar_tablero()  # Redibuja el tablero con las cartas actuales
        pantalla.blit(carta.carta, (x, y))  # Dibuja la carta en su posición actual
        pygame.display.flip()
        reloj.tick(60)

def dibujar_cartas(ancho, alto, hora):
    # Dibuja todas las cartas excepto la última
    for carta in reversed(reloj[hora][1:]):
        superficie_carta = carta.carta
        rect_carta = superficie_carta.get_rect()
        rect_mitad = pygame.Rect(0, 0, min(cards.carta_atras.get_width(), rect_carta.width),
                                 min(cards.carta_atras.get_height(), rect_carta.height))
        pantalla.blit(superficie_carta.subsurface(rect_mitad), (ancho, alto))
        ancho += 12  # Cambia el desplazamiento horizontal a positivo
        alto -= 5  # Cambia el desplazamiento vertical a negativo

    # Dibuja la última carta (la carta superior) al final
    if reloj[hora]:
        pantalla.blit(reloj[hora][0].carta, (ancho, alto))


def dibujar_tablero():
    for i in range(13):
        dibujar_cartas(posicion_hora[i][0], posicion_hora[i][1], i)


def barajeo_americano(mazo):
    mitad = len(mazo) // 2
    izquierda = mazo[:mitad]
    derecha = mazo[mitad:]
    mazo_barajeado = []

    while izquierda or derecha:
        for _ in range(random.randint(1, 5)):
            if izquierda:
                mazo_barajeado.append(izquierda.pop(0))
        for _ in range(random.randint(1, 5)):
            if derecha:
                mazo_barajeado.append(derecha.pop(0))

    return mazo_barajeado


def barajar_cartas():
    global reloj
    reloj = [[] for _ in range(13)]  # Inicializa las pilas del reloj
    animar_barajeo(cards.talia)  # Anima el barajeo inicial
    for _ in range(10):  # Realizar el barajeo americano 10 veces
        cards.talia = barajeo_americano(cards.talia)

    for i, carta in enumerate(cards.talia):
        reloj[i // 4].append(carta)
        carta.ocultar()
    reloj[12][0].mostrar()

    # Reparte las cartas con animación
    repartir_cartas(cards.talia)

    # Inicializa las pilas como no llenas
    global hora_llena
    hora_llena = [False] * 13


def verificar_si_lleno(ite):
    if ite != 12:
        hora_llena[ite] = len(reloj[ite]) == 4 and all(not carta.oculta for carta in reloj[ite])
    else:
        hora_llena[ite] = len(reloj[ite]) == 4 and all(
            not carta.oculta and carta.simbolo == "K" for carta in reloj[ite])


def mostrar_interfaz_resultado(resultado, estado, fondo):
    pantalla.fill(NEGRO)

    imagen_fondo_resultado = pygame.image.load(fondo)
    imagen_fondo_resultado = pygame.transform.scale(imagen_fondo_resultado, (ANCHO, ALTO))
    pantalla.blit(imagen_fondo_resultado, (0, 0))

    fuente_resultado = pygame.font.Font("Sprites/Fonts/Casino3DFilledMarquee.ttf", 80)
    texto_resultado = fuente_resultado.render(resultado, True, BLANCO)
    rect_texto_resultado = texto_resultado.get_rect(center=(ANCHO // 2, ALTO // 2 - 50))
    pantalla.blit(texto_resultado, rect_texto_resultado)
    # respuesta = generar_respuesta(pregunta, estado)
    respuesta = "respuesta"
    fuente_respuesta = pygame.font.Font("Sprites/Fonts/Casino3DFilledMarquee.ttf", 36)
    if pregunta:
        texto_respuesta = fuente_respuesta.render(f"{respuesta}", True, BLANCO)
    else:
        texto_respuesta = fuente_respuesta.render(respuesta, True, BLANCO)
    rect_texto_respuesta = texto_respuesta.get_rect(center=(ANCHO // 2, ALTO // 2 + 50))
    pantalla.blit(texto_respuesta, rect_texto_respuesta)

    pygame.display.flip()
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == K_x:
                    pygame.quit()
                    sys.exit()
                if evento.key == K_r:
                    mostrar_menu_principal()

def ganar():
    mostrar_interfaz_resultado("¡Has ganado!", "positiva","Sprites/gano.png")

def perder():
    mostrar_interfaz_resultado("¡Has perdido!", "negativa", "Sprites/perdio.png")

def bucle_principal():
    barajar_cartas()
    perdido = False
    atrapado = False
    Objetivo = None
    pos_temp = None
    movimientos = 0
    fuente = pygame.font.SysFont(None, 36)
    global switch_automatico
    duracion_automatica = 1000  # Adjust this value to change the speed of the transitions
    if switch_automatico:
        while True:
            pantalla.blit(imagen_fondo, (0, 0))
            tecla = pygame.key.get_pressed()

            if not perdido:
                dibujar_tablero()
            else:
                perder()
                break  # Salir del bucle si se ha perdido

            if all(hora_llena):
                ganar()
                break  # Salir del bucle si se ha ganado

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if not atrapado:
                for ite in range(13):
                    if not reloj[ite][0].oculta and not hora_llena[ite]:
                        if ite == 12 and len(reloj[12]) >= 3 and all(carta.simbolo == "K" for carta in reloj[12]):
                            continue
                        Objetivo = reloj[ite].pop(0)
                        pos_temp = ite
                        verificar_si_lleno(ite)
                        for j in range(13):
                            if lista_horas[Objetivo.simbolo] == j:
                                pos_inicial = (posicion_hora[ite][0], posicion_hora[ite][1])
                                pos_final = (posicion_hora[j][0], posicion_hora[j][1])
                                animar_movimiento(Objetivo, pos_inicial, pos_final, duracion=duracion_automatica)
                                reloj[j].append(Objetivo)
                                reloj[j][0].mostrar()
                                verificar_si_lleno(j)
                                movimientos += 1
                                if hora_llena[j] and j != 12:
                                    for k in range(j, 13):
                                        if k >= 12:
                                            k -= 12
                                        reloj[k + 1][0].mostrar()
                                elif hora_llena[j] and j == 12:
                                    perdido = True
                                break
                        break

            if tecla[K_ESCAPE]:
                pygame.quit()
                sys.exit()

            # Dibujar el contador de movimientos
            texto_movimientos = fuente.render(f"Movimientos: {movimientos}", True, BLANCO)
            pantalla.blit(texto_movimientos, (150, 10))

    else:
        while True:
            pantalla.blit(imagen_fondo, (0, 0))
            pos = pygame.mouse.get_pos()
            tecla = pygame.key.get_pressed()

            if not perdido:
                dibujar_tablero()
            else:
                perder()
                break  # Salir del bucle si se ha perdido

            if all(hora_llena):
                ganar()
                break  # Salir del bucle si se ha ganado

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    for ite in range(13):
                        if (posicion_hora[ite][0] <= pos[0] <= posicion_hora[ite][0] + ANCHO_CARTA and
                                posicion_hora[ite][1] <= pos[1] <= posicion_hora[ite][1] + ALTO_CARTA and
                                not reloj[ite][0].oculta and not hora_llena[ite]):
                            # Verificar si la pila de los 13 ya tiene 3 cartas de valor 13
                            if ite == 12 and len(reloj[12]) >= 3 and all(carta.simbolo == "K" for carta in reloj[12]):
                                continue
                            Objetivo = reloj[ite].pop(0)
                            pos_temp = ite
                            atrapado = True
                            verificar_si_lleno(ite)
                            break
                    else:
                        atrapado = False
                if evento.type == pygame.MOUSEBUTTONUP and atrapado:
                    for ite in range(13):
                        if (posicion_hora[ite][0] <= pos[0] <= posicion_hora[ite][0] + ANCHO_CARTA and
                                posicion_hora[ite][1] <= pos[1] <= posicion_hora[ite][1] + ALTO_CARTA and
                                lista_horas[Objetivo.simbolo] == ite):
                            pos_inicial = (pos[0] - 20, pos[1] - 20)
                            pos_final = (posicion_hora[ite][0], posicion_hora[ite][1])
                            animar_movimiento(Objetivo, pos_inicial, pos_final)
                            reloj[ite].append(Objetivo)  # Mover la carta al fondo de la pila
                            reloj[ite][0].mostrar()  # Mostrar la carta superior
                            Objetivo = None
                            verificar_si_lleno(ite)
                            movimientos += 1  # Incrementar el contador de movimientos
                            if hora_llena[ite] and ite != 12:
                                for i in range(ite, 13):
                                    if i >= 12:
                                        i -= 12
                                    reloj[i + 1][0].mostrar()
                            elif hora_llena[ite] and ite == 12:
                                perdido = True
                            break
                    else:
                        if pos_temp is not None:
                            reloj[pos_temp].insert(0, Objetivo)
                            hora_llena[pos_temp] = False
                            Objetivo = None
                            pos_temp = None

            if tecla[K_ESCAPE]:
                pygame.quit()
                sys.exit()

            if atrapado and Objetivo:
                pantalla.blit(Objetivo.carta, (pos[0] - 20, pos[1] - 20))

            # Dibujar el contador de movimientos
            texto_movimientos = fuente.render(f"Movimientos: {movimientos}", True, BLANCO)
            pantalla.blit(texto_movimientos, (150, 10))

            pygame.display.flip()


# Declare switch_automatico as a global variable
switch_automatico = False

def mostrar_menu_principal():
    global switch_automatico

    # Ocultar todas las cartas antes de mostrar el menú principal
    for carta in cards.talia:
        carta.ocultar()

    fuente_titulo = pygame.font.Font("Sprites/Fonts/Casino3DFilledMarquee.ttf", 100)
    fuente_auto = pygame.font.SysFont(None, 36)
    titulo = fuente_titulo.render("Solitario del Reloj", True, BLANCO)
    texto_auto = fuente_auto.render("AUTO", True, BLANCO)
    rect_titulo = titulo.get_rect(center=(ANCHO // 2, ALTO // 2 - 200))
    rect_texto_auto = texto_auto.get_rect(center=(ANCHO // 2 + 320, ALTO // 2))

    imagen_play = pygame.image.load("Sprites/play_btn.png")
    imagen_play = pygame.transform.scale(imagen_play, (200, 200))
    rect_play = imagen_play.get_rect(center=(ANCHO // 2, ALTO // 2))

    imagen_configuracion = pygame.image.load("Sprites/config_btn.png")
    imagen_configuracion = pygame.transform.scale(imagen_configuracion, (100, 100))
    rect_configuracion = imagen_configuracion.get_rect(bottomleft=(50, ALTO - 50))

    imagen_estadisticas = pygame.image.load("Sprites/estadistica_btn.png")
    imagen_estadisticas = pygame.transform.scale(imagen_estadisticas, (100, 100))
    rect_estadisticas = imagen_estadisticas.get_rect(bottomleft=(200, ALTO - 50))

    imagen_switch_on = pygame.image.load("Sprites/switch_on.png")
    imagen_switch_on = pygame.transform.scale(imagen_switch_on, (130, 50))
    imagen_switch_off = pygame.image.load("Sprites/switch_off.png")
    imagen_switch_off = pygame.transform.scale(imagen_switch_off, (130, 50))
    rect_switch = imagen_switch_off.get_rect(center=(ANCHO // 2 + 200, ALTO // 2))

    imagen_fondo_menu = pygame.image.load("Sprites/fondo_menu.jpg")
    imagen_fondo_menu = pygame.transform.scale(imagen_fondo_menu, (ANCHO, ALTO))

    while True:
        pantalla.blit(imagen_fondo_menu, (0, 0))
        pantalla.blit(titulo, rect_titulo)
        pantalla.blit(imagen_play, rect_play)
        pantalla.blit(imagen_configuracion, rect_configuracion)
        pantalla.blit(imagen_estadisticas, rect_estadisticas)
        pantalla.blit(texto_auto, rect_texto_auto)

        if switch_automatico:
            pantalla.blit(imagen_switch_on, rect_switch)
        else:
            pantalla.blit(imagen_switch_off, rect_switch)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if rect_play.collidepoint(evento.pos):
                    mostrar_interfaz_pregunta()
                elif rect_configuracion.collidepoint(evento.pos):
                    # Lógica para abrir configuración
                    pass
                elif rect_estadisticas.collidepoint(evento.pos):
                    # Lógica para abrir estadísticas
                    pass
                elif rect_switch.collidepoint(evento.pos):
                    switch_automatico = not switch_automatico

        pygame.display.flip()

def mostrar_interfaz_pregunta():
    global pregunta
    fuente_pregunta = pygame.font.SysFont(None, 48)
    fuente_boton = pygame.font.SysFont(None, 36)
    texto_pregunta = fuente_pregunta.render("¿DESEA REALIZAR UNA PREGUNTA?", True, BLANCO)
    rect_pregunta = texto_pregunta.get_rect(center=(ANCHO // 2, ALTO // 2 - 100))

    input_box = pygame.Rect(ANCHO // 2 - 200, ALTO // 2, 400, 50)
    color_inactivo = pygame.Color('lightskyblue3')
    color_activo = pygame.Color('dodgerblue2')
    color = color_inactivo
    activo = False
    texto = ''

    boton_aceptar = fuente_boton.render("Aceptar", True, BLANCO)
    rect_aceptar = boton_aceptar.get_rect(center=(ANCHO // 2 - 100, ALTO // 2 + 100))

    boton_no = fuente_boton.render("No, gracias", True, BLANCO)
    rect_no = boton_no.get_rect(center=(ANCHO // 2 + 100, ALTO // 2 + 100))

    imagen_fondo_pregunta = pygame.image.load("Sprites/fondo_pregunta.png")
    imagen_fondo_pregunta = pygame.transform.scale(imagen_fondo_pregunta, (ANCHO, ALTO))

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(evento.pos):
                    activo = not activo
                else:
                    activo = False
                color = color_activo if activo else color_inactivo

                if rect_aceptar.collidepoint(evento.pos):
                    if texto.strip() == "":
                        # Mostrar mensaje de error si el campo de texto está vacío
                        error_texto = fuente_boton.render("El campo de texto no puede estar vacío", True,
                                                          pygame.Color('red'))
                        pantalla.blit(error_texto, (ANCHO // 2 - 200, ALTO // 2 + 200))
                        pygame.display.flip()
                        pygame.time.wait(2000)
                    else:
                        pregunta = texto
                        bucle_principal()
                elif rect_no.collidepoint(evento.pos):
                    pregunta = ""
                    bucle_principal()

            if evento.type == pygame.KEYDOWN:
                if activo:
                    if evento.key == pygame.K_RETURN:
                        if texto.strip() == "":
                            # Mostrar mensaje de error si el campo de texto está vacío
                            error_texto = fuente_boton.render("El campo de texto no puede estar vacío", True,
                                                              pygame.Color('red'))
                            pantalla.blit(error_texto, (ANCHO // 2 - 200, ALTO // 2 + 200))
                            pygame.display.flip()
                            pygame.time.wait(2000)
                        else:
                            pregunta = texto
                            bucle_principal()
                    elif evento.key == pygame.K_BACKSPACE:
                        texto = texto[:-1]
                    else:
                        texto += evento.unicode

        pantalla.blit(imagen_fondo_pregunta, (0, 0))
        pantalla.blit(texto_pregunta, rect_pregunta)
        txt_surface = fuente_boton.render(texto, True, color)
        width = max(400, txt_surface.get_width() + 10)
        input_box.w = width
        pantalla.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(pantalla, color, input_box, 2)
        pantalla.blit(boton_aceptar, rect_aceptar)
        pantalla.blit(boton_no, rect_no)

        pygame.display.flip()


mostrar_menu_principal()