import pygame
from settings import INVINCIBILITY_DURATION
from sprites import Ghost
from support import import_sprite_sheet # Hàm chúng ta đã viết ở bước trước

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, food_sprites, portals, change_score):
        super().__init__(groups)
        
        # 1. Xử lý hình ảnh
        self.import_assets()
        self.status = 'down'
        self.frame_index = 0
        
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)

        self.hitbox = self.rect.inflate(-2, -2)
        # 2. Di chuyển
        self.pos = pygame.math.Vector2(self.rect.center) # Vị trí thực tế của player (dùng cho di chuyển mượt mà)
        self.direction = pygame.math.Vector2()
        self.speed = 100 # Pixel trên giây
        self.obstacle_sprites = obstacle_sprites
        self.food_sprites = food_sprites
        self.portals = portals
        self.change_score = change_score
        self.spawn_pos = pos
        self.vulnerable = True
        self.hit_time = 0

    def import_assets(self):
        # full_list chứa 16 ảnh theo thứ tự: 
        # [D0, U0, R0, L0, D1, U1, R1, L1, D2, U2, R2, L2, D3, U3, R3, L3]
        full_list = import_sprite_sheet('../images/player/Walk.png', 4, 4)
        # Muốn tăng kích thước ảnh lên gấp đôi, chúng ta có thể sử dụng pygame.transform.scale
        # Chúng ta nhặt ảnh theo cột (Cột 0: Down, 1: Up, 2: Right, 3: Left)
        self.animations = {
            'down':  [full_list[i] for i in [0, 4, 8, 12]],  # Nhặt cột 0
            'up':    [full_list[i] for i in [1, 5, 9, 13]],  # Nhặt cột 1
            'right': [full_list[i] for i in [3, 7, 11, 15]], # Nhặt cột 2
            'left':  [full_list[i] for i in [2, 6, 10, 14]]  # Nhặt cột 3
        }
        # Nếu muốn scale ảnh lên, chúng ta có thể làm như sau (ví dụ scale lên 1.5 lần):
        scale_factor = 1.1
        for key in self.animations:
            self.animations[key] = [pygame.transform.scale(img, 
                (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor))) 
                for img in self.animations[key]]
        
    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = 0
        self.direction.y = 0

        if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.status = 'down'
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.status = 'left' # Khi sang trái, status PHẢI là 'left' và không bị ghi đè
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.status = 'right' # Khi sang phải, status PHẢI là 'right' và không bị ghi đè

    def animate(self, dt):
    # Chỉ chạy animation khi có di chuyển
        if not self.vulnerable:
            # Nếu đang bất tử thì nhấp nháy ảnh (ẩn hiện liên tục)
            alpha = 255 if (pygame.time.get_ticks() // 200) % 2 == 0 else 0
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

        if self.direction.magnitude() > 0:
            self.frame_index += 5 * dt
            if self.frame_index >= len(self.animations[self.status]):
                self.frame_index = 0
        else:
            # Nếu đứng yên, trả về frame đầu tiên của hướng đó
            self.frame_index = 0
            
        self.image = self.animations[self.status][int(self.frame_index)]

    def move(self, dt):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # Di chuyển bằng số thực (self.pos) thay vì trực tiếp vào hitbox
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x) # Cập nhật hitbox bằng số đã làm tròn
        self.collision('horizontal')

        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.collision('vertical')
        
        # Đồng bộ ảnh hiển thị
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        for sprite in self.obstacle_sprites:
            if sprite.rect.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox.left = sprite.rect.right
                    self.pos.x = self.hitbox.centerx # Cập nhật lại pos thực sau va chạm
                if direction == 'vertical':
                    if self.direction.y > 0: self.hitbox.bottom = sprite.rect.top
                    if self.direction.y < 0: self.hitbox.top = sprite.rect.bottom
                    self.pos.y = self.hitbox.centery

    def teleport(self): 
        # Lấy tọa độ các cổng
        left_p = self.portals['portal_left']
        right_p = self.portals['portal_right']

        # Nếu đi quá xa về bên trái cổng trái -> Nhảy sang cổng phải
        if self.hitbox.right < left_p['x']:
            self.pos.x = right_p['x']
            self.hitbox.centerx = round(self.pos.x)
            
        # Nếu đi quá xa về bên phải cổng phải -> Nhảy sang cổng trái
        elif self.hitbox.left > right_p['x'] + 16: # 16 là độ rộng tile
            self.pos.x = left_p['x']
            self.hitbox.centerx = round(self.pos.x)

    def eat(self):
    # Kiểm tra va chạm giữa Player (self) và nhóm food_sprites
        # dokill=True giúp xóa ngay sprite food đó khi va chạm
        collided_sprites = pygame.sprite.spritecollide(self, self.food_sprites, True)
        
        for sprite in collided_sprites:
            if sprite.sprite_type == 'food':
                self.change_score(10) # Mỗi hạt đậu xanh 10 điểm
            elif sprite.sprite_type == 'power':
                self.change_score(50) # Viên năng lượng to thì 50 điểm
                for s in self.groups()[0]: 
                    if isinstance(s, Ghost):
                        s.scared = True
                        s.scared_timer = pygame.time.get_ticks()

    def power_up(self):
        print("Power-up activated! (Logic to be implemented)")

    def reset(self):
        self.pos = pygame.math.Vector2(self.spawn_pos)
        self.hitbox.center = self.pos
        self.rect.center = self.hitbox.center
        self.vulnerable = False # Bắt đầu trạng thái bất tử
        self.hit_time = pygame.time.get_ticks()

    def update(self, dt):
        if not self.vulnerable:
            if pygame.time.get_ticks() - self.hit_time >= INVINCIBILITY_DURATION:
                self.vulnerable = True
        self.input()
        self.animate(dt)
        self.move(dt)
        self.teleport()
        self.eat()