import pygame, random, sys, os, json

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing ")

clock = pygame.time.Clock()

# LOAD / SAVE 
def load_data():
    if os.path.exists("save.json"):
        with open("save.json") as f:
            old_data = json.load(f)

            # Money starts from 0 every game
            old_data["money"] = 0

            return old_data

    return {
        "highscore": 0,
        "money": 0,
        "owned_cars": [True, False, False],
        "selected_car": 0,
        "gift_claimed": False
    }

def save_data():
    with open("save.json", "w") as f:
        json.dump(data, f)

data = load_data()

# IMAGE SECTION
def load_image(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        return None

car_images = [
    load_image("assets/car.png", (50, 100)),
    load_image("assets/car2.png", (50, 100)),
    load_image("assets/car3.png", (50, 100))
]

enemy_img = load_image("assets/enemy.png", (50, 100))
gift_img = load_image("assets/gift.png", (120, 120))

#SOUND SECTION
try:
    pygame.mixer.music.load("assets/bg.mp3")
    pygame.mixer.music.play(-1)
except:
    pass

try:
    crash = pygame.mixer.Sound("assets/crash.wav")
except:
    crash = None

#GAME DATA
lanes = [80, 170, 260]

target_lane = 1
px = lanes[target_lane]
py = 480

font = pygame.font.Font(None, 36)
big = pygame.font.Font(None, 50)

MENU = "menu"
PLAYING = "play"
GAME_OVER = "over"
SHOP = "shop"
CREDITS = "credits"

state = MENU

# Restart limit
restarts_left = 2

def reset():
    global px, ex, ey, score, speed, coins, target_lane

    target_lane = 1
    px = lanes[target_lane]

    ex = random.choice(lanes)
    ey = -100

    score = 0
    speed = 5

    coins = []

reset()

def center(text, y, font, color=(255, 255, 255)):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(WIDTH // 2, y))
    screen.blit(img, rect)

#MAIN LOOP
running = True

while running:

    screen.fill((30, 30, 30))

    for e in pygame.event.get():

        if e.type == pygame.QUIT:
            save_data()
            running = False

        if e.type == pygame.KEYDOWN:

            #MENU
            if state == MENU:

                if e.key == pygame.K_RETURN:
                    restarts_left = 2
                    reset()
                    state = PLAYING

                if e.key == pygame.K_s:
                    state = SHOP

                if e.key == pygame.K_c:
                    state = CREDITS

            #  PLAYING 
            elif state == PLAYING:

                if e.key == pygame.K_LEFT:
                    target_lane = max(0, target_lane - 1)

                if e.key == pygame.K_RIGHT:
                    target_lane = min(2, target_lane + 1)

            #  GAME OVER 
            elif state == GAME_OVER:

                if e.key == pygame.K_r and restarts_left > 0:
                    restarts_left -= 1
                    reset()
                    state = PLAYING

                if e.key == pygame.K_m:
                    state = MENU

            #  SHOP 
            elif state == SHOP:

                if e.key == pygame.K_1:
                    data["selected_car"] = 0

                if e.key == pygame.K_2:

                    if not data["owned_cars"][1] and data["money"] >= 200:
                        data["money"] -= 200
                        data["owned_cars"][1] = True

                    if data["owned_cars"][1]:
                        data["selected_car"] = 1

                if e.key == pygame.K_3:

                    if not data["owned_cars"][2] and data["money"] >= 400:
                        data["money"] -= 400
                        data["owned_cars"][2] = True

                    if data["owned_cars"][2]:
                        data["selected_car"] = 2

                if e.key == pygame.K_m:
                    save_data()
                    state = MENU

            #  CREDITS 
            elif state == CREDITS:

                if e.key == pygame.K_g and not data["gift_claimed"]:

                    data["money"] += 200
                    data["owned_cars"][1] = True
                    data["gift_claimed"] = True

                    save_data()

                if e.key == pygame.K_m:
                    state = MENU

    # MENU SCREEN 
    if state == MENU:

        center("CAR RACING ULTIMATE", 180, big)

        center("ENTER - Play", 260, font)
        center("S - Shop", 300, font)
        center("C - Credits", 340, font)

    #  PLAYING SCREEN 
    elif state == PLAYING:

        # Smooth movement
        target_x = lanes[target_lane]
        px += (target_x - px) * 0.2

        # Enemy movement
        ey += speed

        if ey > HEIGHT:

            ey = -100
            ex = random.choice(lanes)

            score += 1
            speed += 0.2

        # Spawn coins
        if random.randint(1, 50) == 1:
            coins.append([random.choice(lanes), -50])

        # Draw coins
        for c in coins:
            c[1] += speed

            pygame.draw.circle(
                screen,
                (255, 215, 0),
                (c[0] + 25, c[1] + 25),
                10
            )

        # Coin collection
        for c in coins[:]:

            if abs(px - c[0]) < 30 and abs(py - c[1]) < 70:

                coins.remove(c)

                data["money"] += 10

        # Collision
        if abs(px - ex) < 30 and abs(py - ey) < 80:

            if crash:
                crash.play()

            if score > data["highscore"]:
                data["highscore"] = score

            save_data()

            state = GAME_OVER

        # Draw player
        car = car_images[data["selected_car"]]

        if car:
            rect = car.get_rect(center=(px, py))
            screen.blit(car, rect)

        # Draw enemy
        if enemy_img:
            rect = enemy_img.get_rect(center=(ex, ey))
            screen.blit(enemy_img, rect)

        # HUD
        center(f"Score: {score}", 30, font)
        center(f"Money: {data['money']}", 60, font)
        center(f"High: {data['highscore']}", 90, font)

    #  GAME OVER SCREEN 
    elif state == GAME_OVER:

        center("GAME OVER", 200, big, (255, 0, 0))

        center(f"Score: {score}", 250, font)

        center(
            f"Money: {data['money']}",
            290,
            font,
            (255, 215, 0)
        )

        center(f"Restarts Left: {restarts_left}", 340, font)

        if restarts_left > 0:
            center("R - Restart", 390, font)

        center("M - Menu", 440, font)

    #  SHOP SCREEN 
    elif state == SHOP:

        center("SHOP", 80, big)

        prices = [0, 200, 400]

        for i, img in enumerate(car_images):

            x = 60 + i * 110
            y = 150

            if img:
                screen.blit(img, (x, y))

            if data["owned_cars"][i]:
                text = font.render("Owned", True, (0, 255, 0))
            else:
                text = font.render(f"${prices[i]}", True, (255, 255, 0))

            screen.blit(text, (x, y + 110))

            if data["selected_car"] == i:
                pygame.draw.rect(
                    screen,
                    (0, 255, 255),
                    (x - 5, y - 5, 60, 110),
                    2
                )

        center("1 / 2 / 3 Buy & Select", 420, font)
        center("M - Menu", 460, font)

    #  CREDITS SCREEN 
    elif state == CREDITS:

        center("CREDITS", 150, big)

        if gift_img:
            screen.blit(gift_img, (WIDTH // 2 - 60, 200))

        if not data["gift_claimed"]:

            center(
                "Gift Unlocked!",
                350,
                font,
                (0, 255, 0)
            )

            center(
                "Press G to Claim Reward",
                390,
                font
            )

        else:

            center(
                "Gift already claimed",
                350,
                font,
                (255, 215, 0)
            )

        center("Press M for Menu", 450, font)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()