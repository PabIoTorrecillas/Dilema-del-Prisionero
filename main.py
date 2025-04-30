import OpenGL, pygame, sys, random
from pyvidplayer import Video
from button import Button

pygame.init()

SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Dilema del Prisionero")

BG = pygame.image.load("assets/Background 1.png")
ruta_video_introduccion = "videos/introduccion.mp4"
ruta_video_ayuda = "videos/introduccion.mp4"

rewards = {
    ('ataca', 'ataca'): (3, 3),
    ('defiende', 'ataca'): (0, 5),
    ('ataca', 'defiende'): (5, 0),
    ('defiende', 'defiende'): (1, 1)
}

sprite_player_one = [
    pygame.transform.scale(pygame.image.load(f"jugadores/player_1/player_one_{i}.png"), (200, 200))  
    for i in range(1, 7)
]

sprite_player_two = [
    pygame.transform.scale(pygame.image.load(f"jugadores/player_2/player_two_{i}.png"), (200, 200))  
    for i in range(1, 7)
]

sprite_player_three = [
    pygame.transform.scale(pygame.image.load(f"jugadores/player_3/player_three_{i}.png"), (200, 200))  
    for i in range(1, 7)
]

sprite_player_four = [
    pygame.transform.scale(pygame.image.load(f"jugadores/player_4/player_four_{i}.png"), (200, 200))  
    for i in range(1, 7)
]

sprite_player_five = [
    pygame.transform.scale(pygame.image.load(f"jugadores/player_5/player_five_{i}.png"), (200, 200))  
    for i in range(1, 7)
]

sprite_aleatorio = [
    pygame.transform.scale(pygame.image.load(f"bots/bot_aleatorio/aleatorio_{i}.png"), (550, 550))  
    for i in range(1, 7)
]

sprite_cooperar = [
    pygame.transform.scale(pygame.image.load(f"bots/bot_siempre_cooperar/cooperar_{i}.png"), (550, 550))  
    for i in range(1, 7)
]

sprite_traicionar = [
    pygame.transform.scale(pygame.image.load(f"bots/bot_siempre_traicionar/traicionar_{i}.png"), (550, 550))  
    for i in range(1, 7)
]

sprite_tit_for_tat = [
    pygame.transform.scale(pygame.image.load(f"bots/bot_tit_for_tat/tit_for_tat_{i}.png"), (550, 550))  
    for i in range(1, 7)
]

sprite_grim_trigger = [
    pygame.transform.scale(pygame.image.load(f"bots/bot_grim_trigger/grim_trigger_{i}.png"), (550, 550))  
    for i in range(1, 7)
]

sprite_devs = [
    pygame.transform.scale(pygame.image.load(f"assets/devs/elden_ring/caballero_{i}.png"), (500, 500))  
    for i in range(1, 13)
]

def get_font(size): 
    return pygame.font.Font("assets/font.ttf", size)

def play():
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        newBG = pygame.image.load("assets/Background Seleccion.png")
        SCREEN.blit(newBG, (0, 0))

        PLAY_TEXT = get_font(45).render("Selecciona el modo de juego", True, "#b68f40")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(640, 120))
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)

        P1_VS_BOT_BUTTON = Button(image=None, pos=(640, 300), 
                                  text_input="P1 vs BOT", font=get_font(45), base_color="#d7fcd4", hovering_color="Green")
        BOT_VS_BOT_BUTTON = Button(image=None, pos=(640, 400), 
                                   text_input="BOT vs BOT", font=get_font(45), base_color="#d7fcd4", hovering_color="Green")
        BACK_BUTTON = Button(image=None, pos=(640, 650), 
                              text_input="BACK", font=get_font(75), base_color="#FCA9A4", hovering_color="Red")

        for button in [P1_VS_BOT_BUTTON, BOT_VS_BOT_BUTTON, BACK_BUTTON]:
            button.changeColor(PLAY_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if P1_VS_BOT_BUTTON.checkForInput(PLAY_MOUSE_POS):
                    play_mode_p1_vs_bot(ruta_video_introduccion)
                if BOT_VS_BOT_BUTTON.checkForInput(PLAY_MOUSE_POS):
                    play_mode_bot_vs_bot()
                if BACK_BUTTON.checkForInput(PLAY_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def pantalla_resumen(jugador_puntaje, bot_puntaje):
    while True:
        SCREEN.fill((0, 0, 0))  
        font = get_font(50)

        if jugador_puntaje > bot_puntaje:
            ganador_texto = "¡Ganador: Heroe!"
        elif jugador_puntaje < bot_puntaje:
            ganador_texto = "¡Ganador: Monstruo!"
        else:
            ganador_texto = "¡Empate!"

        resumen_texto = font.render(ganador_texto, True, "#b68f40")
        SCREEN.blit(resumen_texto, (640 - resumen_texto.get_width() // 2, 200))

        puntaje_texto = font.render(f"Heroe: {jugador_puntaje} | Monstruo: {bot_puntaje}", True, "White")
        SCREEN.blit(puntaje_texto, (640 - puntaje_texto.get_width() // 2, 300))

        BACK_BUTTON = Button(image=None, pos=(640, 500), 
                             text_input="BACK", font=get_font(40), base_color="White", hovering_color="Green")
        BACK_BUTTON.changeColor(pygame.mouse.get_pos())
        BACK_BUTTON.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(pygame.mouse.get_pos()):
                    return  

        pygame.display.update()

def play_mode_p1_vs_bot(ruta_video):
    rondas = 10
    ronda_actual = 1
    jugador_puntaje = 0
    bot_puntaje = 0
    jugador_decision = ""
    bot_decision = ""

    sprite_index = 0
    sprite_timer = pygame.time.get_ticks()
    sprite_animation_speed = 100

    player_sprites = [sprite_player_one, sprite_player_two, sprite_player_three]
    player_sprite_index = 0  
    current_player_sprites = player_sprites[player_sprite_index]  

    bot_strategies = [
        ('aleatorio', sprite_aleatorio),
        ('ataca', sprite_cooperar),
        ('defiende', sprite_traicionar),
        ('grim_trigger', sprite_grim_trigger),
        ('tit_for_tat', sprite_tit_for_tat)
    ]
    bot_strategy_index = 0  

    vid = Video(ruta_video)
    vid.set_size((1280, 720))
    video_playing = True

    cooldown = 1000  
    last_click_time = pygame.time.get_ticks()

    NEXT_BUTTON_BOT = Button(image=None, pos=(1150, 350), 
                         text_input=">", font=get_font(40), base_color="#b68f40", hovering_color="Yellow")
    PREV_BUTTON_BOT = Button(image=None, pos=(950, 350), 
                         text_input="<", font=get_font(40), base_color="#b68f40", hovering_color="Yellow")
    
    NEXT_BUTTON_PLAYER = Button(image=None, pos=(300, 450), 
                         text_input=">", font=get_font(40), base_color="#b68f40", hovering_color="Yellow")
    PREV_BUTTON_PLAYER = Button(image=None, pos=(160, 450), 
                         text_input="<", font=get_font(40), base_color="#b68f40", hovering_color="Yellow")

    last_opponent_decision = None  
    grim_trigger_triggered = False  

    while True:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and video_playing:
                vid.close()
                video_playing = False  
            if event.type == pygame.MOUSEBUTTONDOWN:
                if NEXT_BUTTON_BOT.checkForInput(pygame.mouse.get_pos()):
                    bot_strategy_index = (bot_strategy_index + 1) % len(bot_strategies)
                if PREV_BUTTON_BOT.checkForInput(pygame.mouse.get_pos()):
                    bot_strategy_index = (bot_strategy_index - 1) % len(bot_strategies)
                
                if NEXT_BUTTON_PLAYER.checkForInput(pygame.mouse.get_pos()):
                    player_sprite_index = (player_sprite_index + 1) % len(player_sprites)
                    current_player_sprites = player_sprites[player_sprite_index]  
                if PREV_BUTTON_PLAYER.checkForInput(pygame.mouse.get_pos()):
                    player_sprite_index = (player_sprite_index - 1) % len(player_sprites)
                    current_player_sprites = player_sprites[player_sprite_index]  

        if video_playing:
            vid.draw(SCREEN, (0, 0))
        else:
            newBG = pygame.image.load("assets/Background 3.png")
            SCREEN.blit(newBG, (0, 0))

            if current_time - sprite_timer > sprite_animation_speed:
                sprite_timer = current_time
                sprite_index = (sprite_index + 1) % len(sprite_player_one)

            current_bot_sprites = bot_strategies[bot_strategy_index][1]
            if current_time - sprite_timer > sprite_animation_speed:
                sprite_timer = current_time
                sprite_index = (sprite_index + 1) % len(current_bot_sprites)

            if current_time - sprite_timer > sprite_animation_speed:
                sprite_timer = current_time
                sprite_index = (sprite_index + 1) % len(current_player_sprites)

            current_bot_sprites = bot_strategies[bot_strategy_index][1]
            sprite2 = current_bot_sprites[sprite_index]
            sprite_position = (700, 130)  
            SCREEN.blit(sprite2, sprite_position)

            NEXT_BUTTON_BOT.changeColor(pygame.mouse.get_pos())
            NEXT_BUTTON_BOT.update(SCREEN)
            PREV_BUTTON_BOT.changeColor(pygame.mouse.get_pos())
            PREV_BUTTON_BOT.update(SCREEN)

            NEXT_BUTTON_PLAYER.changeColor(pygame.mouse.get_pos())
            NEXT_BUTTON_PLAYER.update(SCREEN)
            PREV_BUTTON_PLAYER.changeColor(pygame.mouse.get_pos())
            PREV_BUTTON_PLAYER.update(SCREEN)

            sprite = current_player_sprites[sprite_index]
            sprite_position = (120, 475)  
            SCREEN.blit(sprite, sprite_position)

            sprite2 = current_bot_sprites[sprite_index]
            sprite_position = (700, 130)  
            SCREEN.blit(sprite2, sprite_position)

            font = get_font(30)
            ronda_text = font.render(f"Ronda: {ronda_actual}/{rondas}", True, "#FCE5B4")
            SCREEN.blit(ronda_text, (70, 30))

            puntaje_text = font.render(f"Heroe: {jugador_puntaje} | Monstruo: {bot_puntaje}", True, "#FCE5B4")
            SCREEN.blit(puntaje_text, (70, 80))

            COOPERAR_BUTTON = Button(image=None, pos=(640, 341), 
                                     text_input="ATACAR", font=get_font(40), base_color="White", hovering_color="Orange")
            COOPERAR_BUTTON.changeColor(pygame.mouse.get_pos())
            COOPERAR_BUTTON.update(SCREEN)

            TRAICIONAR_BUTTON = Button(image=None, pos=(640, 450), 
                                       text_input="DEFENDER", font=get_font(40), base_color="White", hovering_color="Orange")
            TRAICIONAR_BUTTON.changeColor(pygame.mouse.get_pos())
            TRAICIONAR_BUTTON.update(SCREEN)

            BACK_BUTTON = Button(image=None, pos=(640, 650), 
                                 text_input="BACK", font=get_font(40), base_color="White", hovering_color="Green")
            BACK_BUTTON.changeColor(pygame.mouse.get_pos())
            BACK_BUTTON.update(SCREEN)

            HELP_BUTTON = Button(image=None, pos=(1150, 50), 
                                 text_input="R?", font=get_font(40), base_color="White", hovering_color="Yellow")
            HELP_BUTTON.changeColor(pygame.mouse.get_pos())
            HELP_BUTTON.update(SCREEN)

            P1_BUTTON = Button(image=None, pos=(230, 450), 
                                 text_input="P1", font=get_font(40), base_color="Blue", hovering_color="Blue")
            P1_BUTTON.changeColor(pygame.mouse.get_pos())
            P1_BUTTON.update(SCREEN)

            BOT_BUTTON = Button(image=None, pos=(1053, 350), 
                                 text_input="BOT", font=get_font(40), base_color="Red", hovering_color="Red")
            BOT_BUTTON.changeColor(pygame.mouse.get_pos())
            BOT_BUTTON.update(SCREEN)

            if jugador_decision and bot_decision:
                color_cooperar = "#4CAF50"  
                color_traicionar = "#FF5733"  
                color_texto_base = "#FCE5B4"  
    
                color_jugador = color_cooperar if jugador_decision == "ataca" else color_traicionar
                color_bot = color_cooperar if bot_decision == "ataca" else color_traicionar
    
                texto_base_jugador = font.render("Heroe: ", True, color_texto_base)
                texto_jugador = font.render(jugador_decision, True, color_jugador)
                texto_separador = font.render(" | Monstruo: ", True, color_texto_base)
                texto_bot = font.render(bot_decision, True, color_bot)
    
                x = 70
                y = 150
                SCREEN.blit(texto_base_jugador, (x, y))  
                x += texto_base_jugador.get_width()
                SCREEN.blit(texto_jugador, (x, y))  
                x += texto_jugador.get_width()
                SCREEN.blit(texto_separador, (x, y))  
                x += texto_separador.get_width()
                SCREEN.blit(texto_bot, (x, y))  

            if event.type == pygame.MOUSEBUTTONDOWN and current_time - last_click_time > cooldown:
                last_click_time = current_time  
                
                if BACK_BUTTON.checkForInput(pygame.mouse.get_pos()):
                    return
                if HELP_BUTTON.checkForInput(pygame.mouse.get_pos()):
                    play_mode_p1_vs_bot(ruta_video_ayuda)      
                if COOPERAR_BUTTON.checkForInput(pygame.mouse.get_pos()) or TRAICIONAR_BUTTON.checkForInput(pygame.mouse.get_pos()):
                    jugador_decision = "ataca" if COOPERAR_BUTTON.checkForInput(pygame.mouse.get_pos()) else "defiende"
                    
                    current_bot_strategy = bot_strategies[bot_strategy_index][0]
                    if current_bot_strategy == 'aleatorio':
                        bot_decision = random.choice(['ataca', 'defiende'])
                    elif current_bot_strategy == 'ataca':
                        bot_decision = 'ataca'
                    elif current_bot_strategy == 'defiende':
                        bot_decision = 'defiende'
                    elif current_bot_strategy == 'tit_for_tat':
                        bot_decision = random.choice(['ataca', 'defiende']) if last_opponent_decision is None else last_opponent_decision
                    elif current_bot_strategy == 'grim_trigger':
                        if grim_trigger_triggered:
                            bot_decision = 'ataca'
                        else:
                            bot_decision = 'defiende'

                    if jugador_decision == 'ataca':
                        grim_trigger_triggered = True
                    last_opponent_decision = jugador_decision

                    resultado = rewards[(jugador_decision, bot_decision)]
                    jugador_puntaje += resultado[0]
                    bot_puntaje += resultado[1]

                    ronda_actual += 1
                    if ronda_actual > rondas:
                        pantalla_resumen(jugador_puntaje, bot_puntaje)
                        return

        pygame.display.update()



def play_mode_bot_vs_bot():
    def mostrar_seleccion_bot(x, y, opciones, seleccion):
        """Muestra las opciones de selección de estrategias y sprites."""
        font = get_font(25)
        for i, opcion in enumerate(opciones):
            color = "White" if i != seleccion else "Yellow"
            texto = font.render(opcion[0].capitalize(), True, color)
            SCREEN.blit(texto, (x, y + i * 40))

    def pantalla_seleccion():
        """Pantalla para seleccionar estrategia y sprite de ambos lados."""
        seleccion_izquierda = 0
        seleccion_derecha = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        seleccion_izquierda = (seleccion_izquierda - 1) % len(player_strategies)
                    if event.key == pygame.K_s:
                        seleccion_izquierda = (seleccion_izquierda + 1) % len(player_strategies)
                    if event.key == pygame.K_UP:
                        seleccion_derecha = (seleccion_derecha - 1) % len(bot_strategies)
                    if event.key == pygame.K_DOWN:
                        seleccion_derecha = (seleccion_derecha + 1) % len(bot_strategies)
                    if event.key == pygame.K_RETURN:
                        return seleccion_izquierda, seleccion_derecha

            SCREEN.fill((0, 0, 0))
            font = get_font(30)
            titulo = font.render("Selecciona estrategias/sprites", True, "White")
            SCREEN.blit(titulo, (200, 50))

            titulo_izquierda = font.render("Heroes", True, "Blue")
            SCREEN.blit(titulo_izquierda, (200, 220))

            titulo_derecha = font.render("Monstruos", True, "Red")
            SCREEN.blit(titulo_derecha, (600, 220))

            mostrar_seleccion_bot(200, 300, player_strategies, seleccion_izquierda)
            mostrar_seleccion_bot(600, 300, bot_strategies, seleccion_derecha)

            pygame.display.update()

    player_strategies = [
        ('aleatorio', sprite_player_one),
        ('ataca', sprite_player_two),
        ('defiende', sprite_player_three),
        ('tit_for_tat', sprite_player_four),
        ('grim_trigger', sprite_player_five)
    ]

    bot_strategies = [
        ('aleatorio', sprite_aleatorio),
        ('ataca', sprite_cooperar),
        ('defiende', sprite_traicionar),
        ('grim_trigger', sprite_grim_trigger),
        ('tit_for_tat', sprite_tit_for_tat)
    ]

    seleccion_izquierda, seleccion_derecha = pantalla_seleccion()
    izquierda_strategy = player_strategies[seleccion_izquierda]
    derecha_strategy = bot_strategies[seleccion_derecha]

    rondas = 10
    ronda_actual = 1
    izquierda_puntaje = 0
    derecha_puntaje = 0

    sprite_index = 0
    sprite_timer = pygame.time.get_ticks()
    sprite_animation_speed = 100
    ronda_duracion = 2000  
    ronda_inicio = pygame.time.get_ticks()

    decision_izquierda = "N/A"
    decision_derecha = "N/A"

    # Variables para las estrategias
    izquierda_grim_trigger = False
    derecha_grim_trigger = False
    izquierda_last_decision = None
    derecha_last_decision = None

    while True:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        newBG = pygame.image.load("assets/Background 4.png")
        SCREEN.blit(newBG, (0, 0))

        if current_time - sprite_timer > sprite_animation_speed:
            sprite_timer = current_time
            sprite_index = (sprite_index + 1) % len(sprite_player_one)

        izquierda_sprite = izquierda_strategy[1][sprite_index]
        derecha_sprite = derecha_strategy[1][sprite_index]

        SCREEN.blit(izquierda_sprite, (200, 500))  
        SCREEN.blit(derecha_sprite, (500, 150))  

        font = get_font(30)
        ronda_text = font.render(f"Ronda: {ronda_actual}/{rondas}", True, "White")
        SCREEN.blit(ronda_text, (70, 20))

        puntaje_text = font.render(f"Heroe: {izquierda_puntaje} | Monstruo: {derecha_puntaje}", True, "White")
        SCREEN.blit(puntaje_text, (70, 60))

        decision_text = font.render(f"Heroe: {decision_izquierda} | Monstruo: {decision_derecha}", True, "Yellow")
        SCREEN.blit(decision_text, (70, 100))

        if current_time - ronda_inicio > ronda_duracion:
            if ronda_actual <= rondas:
                if izquierda_strategy[0] == 'aleatorio':
                    decision_izquierda = random.choice(['ataca', 'defiende'])
                elif izquierda_strategy[0] == 'ataca':
                    decision_izquierda = 'ataca'
                elif izquierda_strategy[0] == 'defiende':
                    decision_izquierda = 'defiende'
                elif izquierda_strategy[0] == 'tit_for_tat':
                    decision_izquierda = (
                        'defiende' if derecha_last_decision is None else derecha_last_decision
                    )
                elif izquierda_strategy[0] == 'grim_trigger':
                    if izquierda_grim_trigger:
                        decision_izquierda = 'ataca'
                    else:
                        decision_izquierda = 'defiende'
                        if derecha_last_decision == 'ataca':
                            izquierda_grim_trigger = True

                if derecha_strategy[0] == 'aleatorio':
                    decision_derecha = random.choice(['ataca', 'defiende'])
                elif derecha_strategy[0] == 'ataca':
                    decision_derecha = 'ataca'
                elif derecha_strategy[0] == 'defiende':
                    decision_derecha = 'defiende'
                elif derecha_strategy[0] == 'tit_for_tat':
                    decision_derecha = (
                        'defiende' if izquierda_last_decision is None else izquierda_last_decision
                    )
                elif derecha_strategy[0] == 'grim_trigger':
                    if derecha_grim_trigger:
                        decision_derecha = 'ataca'
                    else:
                        decision_derecha = 'defiende'
                        if izquierda_last_decision == 'ataca':
                            derecha_grim_trigger = True

                izquierda_last_decision = decision_izquierda
                derecha_last_decision = decision_derecha

                resultado = rewards[(decision_izquierda, decision_derecha)]
                izquierda_puntaje += resultado[0]
                derecha_puntaje += resultado[1]

                ronda_actual += 1
                ronda_inicio = current_time

            else:
                pantalla_resumen(izquierda_puntaje, derecha_puntaje)
                return

        pygame.display.update()


def options():
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        OPTIONS_TEXT = get_font(45).render("Desarrollado por:", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 50))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        NAME1_TEXT = get_font(35).render("Pablo Torrecillas", True, "Black")
        NAME1_RECT = NAME1_TEXT.get_rect(center=(640, 160))
        SCREEN.blit(NAME1_TEXT, NAME1_RECT)

        # NAME2_TEXT = get_font(35).render("Alberto Emiliano Solis Santos", True, "Black")
        # NAME2_RECT = NAME2_TEXT.get_rect(center=(640, 220))
        # SCREEN.blit(NAME2_TEXT, NAME2_RECT)

        sprite_index = (pygame.time.get_ticks() // 100) % len(sprite_devs)
        sprite = sprite_devs[sprite_index]
        SCREEN.blit(sprite, (365, 85))

        OPTIONS_BACK = Button(image=None, pos=(640, 650), 
                            text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Red")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("PROYECTO", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 250), 
                            text_input="JUGAR", font=get_font(70), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 400), 
                            text_input="CREDITO", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 550), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN) 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()