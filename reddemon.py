import heapq
import pyglet
from pyglet.window import key
import sys # Kasutame väljumiseks


# --- Üldised seaded ---
TILE = 40
current_level = 1

# Mängu olekud: 'START', 'PLAYING', 'SETTINGS', 'JUMPSCARE', 'FINISH'
GAME_STATE = 'START' 

# Resolutsiooni valikud ja algne seadistus
RESOLUTIONS = [(800, 600), (1024, 768), (1280, 720)]
current_resolution_index = 0
DEFAULT_RES = RESOLUTIONS[current_resolution_index]

window = pyglet.window.Window(DEFAULT_RES[0], DEFAULT_RES[1], "2D Labürindi Mäng")

# --- Ressursid (Palun veenduge, et need failiteed on õiged!) ---
try:
    start_bg = pyglet.image.load(r"c:\Users\matti\OneDrive\Desktop\Mattias_Kingo_MazeGame\assets\lukama pilt.png")
    jumpscare_image = pyglet.image.load(r"c:\Users\matti\OneDrive\Desktop\Mattias_Kingo_MazeGame\assets\jumpscare.jpg")
    jumpscare_sound = pyglet.media.load(r"c:\Users\matti\OneDrive\Desktop\Mattias_Kingo_MazeGame\assets\jumpscare.wav.mp3", streaming=False)
    bg_music = pyglet.media.load(r"c:\Users\matti\OneDrive\Desktop\Mattias_Kingo_MazeGame\assets\dark-horror-soundscape-345814.mp3")
    step_sound = pyglet.media.load(r"c:\Users\matti\OneDrive\Desktop\Mattias_Kingo_MazeGame\assets\step-351163.mp3", streaming=False)
except pyglet.resource.ResourceNotFoundException as e:
    print(f"Viga ressursi laadimisel: {e}")
    print("Veenduge, et 'assets/' kaust ja failinimed on õiged.")
    # Asendame musta taustaga, kui pilti pole
    start_bg = pyglet.image.create(1, 1, pyglet.image.SolidColorImagePattern((0, 0, 0, 255)))
    jumpscare_image = pyglet.image.create(1, 1, pyglet.image.SolidColorImagePattern((0, 0, 0, 255)))


# --- Taustamuusika ---
bg_player = pyglet.media.Player()
bg_player.queue(bg_music)
bg_player.loop = True

# --- Vaenlane ---
enemy_x, enemy_y = 1, 1
ENEMY_SPEED = 0.5 # A* liikumise intervall sekundites

# --- Mängija ---
player_x = 0
player_y = 0

# --- Labürint ---
maze = []
ROWS = 0
COLS = 0

# --- Abifunktsioonid ---
def set_new_resolution(res):
    """Muudab akna suuruse ja seadistab vaatevälja ümber."""
    global current_resolution_index
    # Leiame indeksi, et see oleks salvestatud
    try:
        current_resolution_index = RESOLUTIONS.index(res)
    except ValueError:
        # Kui mingil põhjusel resolutsioon valikus puudub
        pass

    window.set_size(res[0], res[1])
    pyglet.gl.glViewport(0, 0, res[0], res[1])
    print(f"Resolutsioon muudetud: {res[0]}x{res[1]}")

def can_move(x, y):
    """Kontrollib, kas ruut on labürindi piires ja vaba (mitte sein 1)."""
    return 0 <= x < COLS and 0 <= y < ROWS and maze[y][x] != 1

def neighbors(node):
    """Leiab antud ruudu A* jaoks sobivad naabrid."""
    x, y = node
    nbrs = []
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx, ny = x+dx, y+dy
        if can_move(nx, ny):
            nbrs.append((nx, ny))
    return nbrs

def heuristic(a, b):
    """Manhattani kaugus A* jaoks."""
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(start, goal):
    """A* algoritmi implementatsioon lühima tee leidmiseks."""
    if start == goal:
        return [start]

    open_set = []
    # (f_score, g_score, current_node, parent_node)
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start, None))
    came_from = {}
    gscore = {start: 0}
    closed = set()

    while open_set:
        _, g, current, parent = heapq.heappop(open_set)
        
        if current in closed:
            continue
        
        came_from[current] = parent
        
        if current == goal:
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = came_from.get(node)
            return path[::-1] # Tagastame pööratud tee (algusest lõpuni)
        
        closed.add(current)

        for nbr in neighbors(current):
            tentative_g = g + 1
            if tentative_g < gscore.get(nbr, 1e9):
                gscore[nbr] = tentative_g
                f = tentative_g + heuristic(nbr, goal)
                heapq.heappush(open_set, (f, tentative_g, nbr, current))
                
    return []

# --- Mängija liikumine ---
def try_move_player(dx, dy):
    global player_x, player_y

    nx = player_x + dx
    ny = player_y + dy

    if can_move(nx, ny):
        player_x = nx
        player_y = ny
        return True

    return False

# --- Levelid ---
def load_level(level_number):
    global maze, player_x, player_y, ROWS, COLS, enemy_x, enemy_y, ENEMY_SPEED

    # Levelide definitsioonid
    if level_number == 1:
        maze = [
            [1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,1,1,1,1],
            [1,1,1,1,1,2,1,1,1,1] # 2 on FINISH
        ]
        ENEMY_SPEED = 0.6
        player_x, player_y = 8, 1
        enemy_x, enemy_y = 1, 1

    elif level_number == 2:
        maze = [
            [1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,0,1,0,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,0,1,0,1,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,2,1],
            [1,1,1,1,1,1,1,1,1,1]
        ]
        ENEMY_SPEED = 0.35
        player_x, player_y = 8, 1
        enemy_x, enemy_y = 1, 1

    elif level_number == 3:
        maze = [
            [1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,2,1],
            [1,1,1,1,1,1,1,1,1,1]
        ]
        ENEMY_SPEED = 0.15
        player_x, player_y = 8, 1
        enemy_x, enemy_y = 1, 1

    ROWS = len(maze)
    COLS = len(maze[0])

def load_next_level():
    global current_level, GAME_STATE
    current_level += 1

    if current_level > 3:
        GAME_STATE = 'FINISH'
        # Sulgeme akna 5 sekundi pärast
        pyglet.clock.schedule_once(lambda dt: window.close(), 5)
    else:
        load_level(current_level)
        schedule_enemy_speed()

def check_finish():
    """Kontrollib, kas mängija on jõudnud finiširuutu (2)."""
    if maze[player_y][player_x] == 2:
        load_next_level()

# --- Vaenlane A* liikumine ---
def move_enemy_towards_player(dt):
    global enemy_x, enemy_y, GAME_STATE

    # Liikumine ainult PLAYING olekus
    if GAME_STATE != 'PLAYING':
        return

    start = (enemy_x, enemy_y)
    goal = (player_x, player_y)
    path = astar(start, goal)

    if len(path) >= 2:
        # Liigub tee järgmisele sammule
        enemy_x, enemy_y = path[1]

    # JUMPSCARE (Mängu kaotus)
    if enemy_x == player_x and enemy_y == player_y:
        GAME_STATE = 'JUMPSCARE'
        # Peatame taustamuusika
        bg_player.pause() 
        jumpscare_sound.play()
        # Sulgeme akna 3 sekundi pärast
        pyglet.clock.schedule_once(lambda dt: window.close(), 3)

def schedule_enemy_speed():
    """Seadistab vaenlase liikumisintervalli vastavalt kiirusele."""
    pyglet.clock.unschedule(move_enemy_towards_player)
    pyglet.clock.schedule_interval(move_enemy_towards_player, ENEMY_SPEED)


# --- DRAW ---
@window.event
def on_draw():
    window.clear()
    pyglet.gl.glClearColor(0.05,0.05,0.05,1)

    # 1. START SCREEN
    if GAME_STATE == 'START':
        # Skaleerime taustapildi akna suuruseks
        start_bg.blit(0,0,width=window.width,height=window.height)
        
        pyglet.text.Label("Red Demon Maze", font_size=64, x=window.width//2, y=window.height//2+50,
                              anchor_x='center', anchor_y='center', color=(255,0,0,255)).draw()
        pyglet.text.Label("Press SPACE to Play", font_size=36, x=window.width//2, y=window.height//2-50,
                              anchor_x='center', anchor_y='center', color=(255, 255, 255, 255)).draw()
        pyglet.text.Label("Press ENTER for Settings", font_size=24, x=window.width//2, y=window.height//2-100,
                              anchor_x='center', anchor_y='center', color=(255, 255, 255, 255)).draw()
        return

    # 2. SETTINGS SCREEN
    elif GAME_STATE == 'SETTINGS':
        pyglet.text.Label("SETTINGS", font_size=48, x=window.width//2, y=window.height - 100,
                              anchor_x='center', anchor_y='center', color=(255, 255, 255, 255)).draw()
        
        y_pos = window.height // 2
        
        # Resolutsiooni valiku silt
        pyglet.text.Label("Resolution (W/S):", font_size=24, x=window.width//2 - 10, y=y_pos + 20,
                              anchor_x='right', anchor_y='center', color=(255, 255, 255, 255)).draw()
        
        # Kuvame hetkel valitud resolutsiooni (punaselt)
        res_str = f"{RESOLUTIONS[current_resolution_index][0]}x{RESOLUTIONS[current_resolution_index][1]}"
        
        pyglet.text.Label(f"> {res_str} <", font_size=28, x=window.width//2 + 20, y=y_pos + 20,
                              anchor_x='left', anchor_y='center', color=(255, 0, 0, 255)).draw()

        pyglet.text.Label("Press ENTER to Apply & Back to Menu", font_size=20, x=window.width//2, y=y_pos - 100,
                              anchor_x='center', anchor_y='center', color=(255, 255, 255, 255)).draw()
        return

    # 3. JUMPSCARE SCREEN
    elif GAME_STATE == 'JUMPSCARE':
        jumpscare_image.blit(0,0,width=window.width,height=window.height)
        return

    # 4. FINISH SCREEN
    elif GAME_STATE == 'FINISH':
        pyglet.text.Label("U escaped the demon...", font_size=48,
                              x=window.width//2, y=window.height//2,
                              anchor_x='center', anchor_y='center',
                              color=(255,0,0,255)).draw()
        return

    # 5. PLAYING (Mängu Joonistamine)
    
    # Maze
    for y in range(ROWS):
        for x in range(COLS):
            tile = maze[y][x]
            if tile == 1:
                # Sein (Hall)
                color = [50,50,50]*4
            elif tile == 2:
                # Finiš (Roheline)
                color = [0,255,0]*4
            else:
                continue
            
            # Joonista ruut
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                ('v2f',[x*TILE,y*TILE, x*TILE+TILE,y*TILE,
                        x*TILE+TILE,y*TILE+TILE, x*TILE,y*TILE+TILE]),
                ('c3B',color))

    # Player (Oranž)
    px, py = player_x*TILE, player_y*TILE
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
        ('v2f',[px,py, px+TILE,py, px+TILE,py+TILE, px,py+TILE]),
        ('c3B',[210,105,30]*4))

    # Enemy (Punane)
    ex, ey = enemy_x*TILE, enemy_y*TILE
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
        ('v2f',[ex,ey, ex+TILE,ey, ex+TILE,ey+TILE, ex,ey+TILE]),
        ('c3B',[255,0,0]*4))
    
    # Kuvame praeguse leveli numbri
    pyglet.text.Label(f"Level: {current_level}", font_size=18, 
                      x=window.width - 10, y=window.height - 10, 
                      anchor_x='right', anchor_y='top', color=(255, 255, 255, 255)).draw()


# --- KEY PRESS ---
@window.event
def on_key_press(symbol, modifiers):
    global GAME_STATE, current_level, current_resolution_index

    # --- SETTINGS LOOGIKA ---
    if GAME_STATE == 'SETTINGS':
        if symbol == key.ESCAPE:
            # Tühista ja mine tagasi ilma muutuseta
            GAME_STATE = 'START'
            # (Võiks taastada vana resolutsiooni, aga lihtsuse huvides ei tee seda)
        
        elif symbol == key.ENTER:
            # Kinnita resolutsioon ja mine tagasi START menüüsse
            set_new_resolution(RESOLUTIONS[current_resolution_index])
            GAME_STATE = 'START'
            
        # Resolutsiooni valimine: W (üles) / S (alla)
        elif symbol == key.W or symbol == key.UP:
            current_resolution_index = (current_resolution_index - 1) % len(RESOLUTIONS)
        elif symbol == key.S or symbol == key.DOWN:
            current_resolution_index = (current_resolution_index + 1) % len(RESOLUTIONS)
        return

    # --- START LOOGIKA ---
    if GAME_STATE == 'START':
        if symbol == key.SPACE:
            load_level(current_level)
            GAME_STATE = 'PLAYING'
            bg_player.play()
            schedule_enemy_speed()
        elif symbol == key.ENTER:
            GAME_STATE = 'SETTINGS'
        elif symbol == key.Q: # Lisasime Q Quit nupu
            sys.exit()
        return

    # Peata liikumine, kui pole mängus
    if GAME_STATE != 'PLAYING':
        return

    # --- PLAYING (Mängija liikumine) LOOGIKA ---
    moved = False

    if symbol == key.W or symbol == key.UP:
        moved = try_move_player(0, 1)
    elif symbol == key.S or symbol == key.DOWN:
        moved = try_move_player(0, -1)
    elif symbol == key.A or symbol == key.LEFT:
        moved = try_move_player(-1, 0)
    elif symbol == key.D or symbol == key.RIGHT:
        moved = try_move_player(1, 0)

    if moved:
        # Heli mängitakse ainult liikumise korral
        step_sound.play() 
        check_finish()


# --- RUN ---
# Esmalt laeme esimese leveli andmed, et ROWS/COLS oleks defineeritud
load_level(current_level) 
# Mängu käivitamine
pyglet.app.run()
