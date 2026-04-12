import pygame

# --- 설정 (이 부분이 도구에 의해 자동 생성되는 영역) ---
SPRITE_SHEET_PATH = "your_spritesheet.png"
FRAME_WIDTH = 32
FRAME_HEIGHT = 32
# 사용자가 선택한 프레임의 (row, col) 좌표 리스트
SELECTED_SEQUENCE = [(0, 0), (0, 1), (0, 2), (0, 3)] 
FPS = 10 

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet_path, frame_w, frame_h, sequence):
        super().__init__()
        self.sheet = pygame.image.load(sheet_path).convert_alpha()
        self.frames = []
        
        # 1. 시트에서 선택된 프레임 자르기 (자동 생성 로직)
        for row, col in sequence:
            rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
            frame_image = self.sheet.subsurface(rect)
            self.frames.append(frame_image)
            
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(200, 200))
        self.last_update = pygame.time.get_ticks()

    def update(self):
        # 2. 애니메이션 속도 제어
        now = pygame.time.get_ticks()
        if now - self.last_update > 1000 // FPS:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

# --- 실행부 ---
pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()

sprite = AnimatedSprite(SPRITE_SHEET_PATH, FRAME_WIDTH, FRAME_HEIGHT, SELECTED_SEQUENCE)
all_sprites = pygame.sprite.Group(sprite)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    all_sprites.update()
    screen.fill((200, 200, 200)) # 배경색
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()