import pygame.key

from player import Player


def handle_player_controls(player: Player):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player.move_forward()

    if keys[pygame.K_LEFT]:
        player.turn_left()
    if keys[pygame.K_RIGHT]:
        player.turn_right()


def get_control_hint() -> str:
    return "Move Forward: W | Turn Right-Left: Arrows"
