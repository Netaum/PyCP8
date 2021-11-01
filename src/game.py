import pygame
from chip import Chip

def main():
    pygame.init()
    logo = pygame.image.load("./img/Play.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("Emulator")
    screen = pygame.display.set_mode((640, 320))
    running = True
    pixel = pygame.Surface((10, 10))
    chip = Chip()

    while running:
        chip.emulate_cycle()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        key_pressed(chip, keys)

        print_pixel(screen, pixel, chip)
      
        pygame.display.update()

def print_pixel(screen, pixel, chip: Chip):
    for y in range(32):
        for x in range(64):
            i = (y * 64) + x
            if chip.gfx[i] == 0:
                pixel.fill((0,0,0))
            else:
                pixel.fill((255,255,255))

            screen.blit(pixel, ((x * 10), (y * 10)))

def key_pressed(chip: Chip, keys):
    chip.keys[0x1] = int(keys[pygame.K_1])
    chip.keys[0x2] = int(keys[pygame.K_2])
    chip.keys[0x3] = int(keys[pygame.K_3])
    chip.keys[0xC] = int(keys[pygame.K_4])

    chip.keys[0x4] = int(keys[pygame.K_q])
    chip.keys[0x5] = int(keys[pygame.K_w])
    chip.keys[0x6] = int(keys[pygame.K_e])
    chip.keys[0xD] = int(keys[pygame.K_r])

    chip.keys[0x7] = int(keys[pygame.K_a])
    chip.keys[0x8] = int(keys[pygame.K_s])
    chip.keys[0x9] = int(keys[pygame.K_d])
    chip.keys[0xE] = int(keys[pygame.K_f])

    chip.keys[0xA] = int(keys[pygame.K_z])
    chip.keys[0x0] = int(keys[pygame.K_x])
    chip.keys[0xB] = int(keys[pygame.K_c])
    chip.keys[0xF] = int(keys[pygame.K_v])


if __name__ == "__main__":
    main()