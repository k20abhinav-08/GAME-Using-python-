import cv2
import mediapipe as mp
import pygame
import sys
import random

# Initialize pygame
pygame.init()



# Window setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("VR Fruit Ninja")

# ✅ Define function
def generate_background():
    surface = pygame.Surface((WIDTH, HEIGHT))
    surface.fill((0, 0, 0))

    paint_colors = {
        (255, 0, 0): 22,
        (255, 255, 255): 17,
        (255, 255, 0): 4
    }

    for color, percent in paint_colors.items():
        total_spots = WIDTH * HEIGHT // 800 * percent // 100
        for _ in range(total_spots):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            core_radius = random.randint(2, 4)
            glow_radius = core_radius * 3

            glow = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, color + (40,), (glow_radius, glow_radius), glow_radius)
            surface.blit(glow, (x - glow_radius, y - glow_radius))

            pygame.draw.circle(surface, color, (x, y), core_radius)

    return surface

# ✅ Now call the function
background = generate_background()






# Load fruit images
apple_img = pygame.image.load("apple.png")
orange_img = pygame.image.load("orange.png")
fruit_images = [apple_img, orange_img]

# MediaPipe hand tracking setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Webcam setup
cap = cv2.VideoCapture(0)

# Fruit setup
NUM_FRUITS = 6
fruits = []

for _ in range(NUM_FRUITS):
    fruits.append({
        "x": random.randint(100, WIDTH - 100),
        "y": HEIGHT,
        "speed": -random.randint(10, 16),
        "sliced": False,
        "size": random.randint(50, 80),
        "image": random.choice(fruit_images)
    })

clock = pygame.time.Clock()
running = True

while running:
    screen.blit(background, (0, 0))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update fruit positions
    for fruit in fruits:
        if not fruit["sliced"]:
            fruit["y"] += fruit["speed"]
            fruit["speed"] += 0.5

        # Reset if off screen
        if fruit["y"] > HEIGHT:
            fruit["x"] = random.randint(100, WIDTH - 100)
            fruit["y"] = HEIGHT
            fruit["speed"] = -random.randint(10, 16)
            fruit["sliced"] = False
            fruit["image"] = random.choice(fruit_images)

    # Read webcam frame
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    hand_pos = None

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            h, w, c = frame.shape
            x = int(hand_landmarks.landmark[8].x * WIDTH)
            y = int(hand_landmarks.landmark[8].y * HEIGHT)
            hand_pos = (x, y)

            # Draw finger circle
            pygame.draw.circle(screen, (255, 0, 0), hand_pos, 10)

            # Check for fruit collision
            for fruit in fruits:
                fruit_rect = pygame.Rect(fruit["x"], fruit["y"], fruit["size"], fruit["size"])
                if fruit_rect.collidepoint(hand_pos) and not fruit["sliced"]:
                    fruit["sliced"] = True
                    fruit["y"] = HEIGHT + 100  # fall out of screen

    # Draw fruits
    for fruit in fruits:
        if not fruit["sliced"]:
            fruit_scaled = pygame.transform.scale(fruit["image"], (fruit["size"], fruit["size"]))
            screen.blit(fruit_scaled, (fruit["x"], fruit["y"]))

    # Webcam preview (optional)
    cv2.imshow("Hand View", frame)
    pygame.display.update()
    clock.tick(30)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()
