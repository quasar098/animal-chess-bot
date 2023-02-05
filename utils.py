from enum import Enum
import pygame
from typing import Optional, Union
from os.path import join
from typing import TYPE_CHECKING


BOARD_WIDTH = 7
BOARD_HEIGHT = 7
TILE_SIZE = 100

SCREEN_WIDTH = BOARD_WIDTH*TILE_SIZE+168
SCREEN_HEIGHT = BOARD_HEIGHT*TILE_SIZE
FRAMERATE = 75

BG_COLOR = pygame.Color(49, 46, 43)


class Team(Enum):
    NOTEAM = -1
    BLUE = 0
    RED = 1


class ImageId(Enum):
    OUTLINE = -5
    HIGHLIGHT = -4
    CAPTURE_HINT = -3
    MOVE_HINT = -2
    BOARD = -1
    GOOSE = 0
    KNIGHT = 1
    MONKEY = 2
    BUFFALO = 3
    COBRA = 4
    PEDESTRIAN = 5


class SoundId(Enum):
    START = 0
    MOVE = 1
    TAKE = 2
    GAME_OVER = 3


images: dict[tuple[Team, ImageId], pygame.Surface] = {}
sounds: dict[SoundId, pygame.mixer.Sound] = {}
channels: list[pygame.mixer.Channel] = []


def rehue_image(surface: pygame.Surface):
    with pygame.PixelArray(surface) as pixels:
        for x in range(surface.get_width()):
            for y in range(surface.get_height()):
                rgb = surface.unmap_rgb(pixels[x][y])
                color = pygame.Color(*rgb)
                h, s, l, a = color.hsla
                color.hsla = (int(h) + 114) % 360, int(s), int(l), int(a)
                pixels[x][y] = color
        return pixels.make_surface().convert_alpha()


def init_assets():
    pygame.mixer.set_num_channels(30)
    for image_id in ImageId:
        if image_id == ImageId.MOVE_HINT:
            image = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(image, pygame.Color(0, 0, 0), (49, 49), 16)
            image.set_alpha(34)
            images[(Team.NOTEAM, image_id)] = image
            continue
        if image_id == ImageId.CAPTURE_HINT:
            image = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(image, pygame.Color(0, 0, 0), (49, 49), 50)
            pygame.draw.circle(image, pygame.Color(0, 0, 0, 0), (49, 49), 40)
            image.set_alpha(41)
            images[(Team.NOTEAM, image_id)] = image
            continue
        if image_id == ImageId.HIGHLIGHT:
            image = pygame.Surface((100, 100), pygame.SRCALPHA)
            image.fill((204, 145, 34))
            image.set_alpha(121)
            images[(Team.NOTEAM, image_id)] = image
            continue
        if image_id == ImageId.OUTLINE:
            image = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.rect(image, (255, 255, 255), (0, 0, 100, 5))
            pygame.draw.rect(image, (255, 255, 255), (0, 95, 100, 5))
            pygame.draw.rect(image, (255, 255, 255), (0, 0, 5, 95))
            pygame.draw.rect(image, (255, 255, 255), (95, 0, 5, 95))
            image.set_alpha(150)
            images[(Team.NOTEAM, image_id)] = image
            continue
        image = pygame.image.load(join("assets", f"{image_id.name.lower()}.png")).convert_alpha()
        if image_id.value >= 0:
            images[(Team.BLUE, image_id)] = image.copy()
            images[(Team.RED, image_id)] = rehue_image(image)
        if image_id == ImageId.BOARD:
            image = pygame.transform.scale(image, (TILE_SIZE*BOARD_WIDTH, TILE_SIZE*BOARD_HEIGHT))
            images[(Team.NOTEAM, image_id)] = image
            continue
    for _ in range(30):
        channels.append(pygame.mixer.Channel(_))
    for sound_id in SoundId:
        sounds[sound_id] = pygame.mixer.Sound(join("assets", f"{sound_id.name.lower().replace('_', '')}.mp3"))


def draw_move_hint(screen: pygame.Surface, x: int, y: int):
    screen.blit(images[(Team.NOTEAM, ImageId.MOVE_HINT)], (x * TILE_SIZE, y * TILE_SIZE))


def draw_capture_hint(screen: pygame.Surface, x: int, y: int):
    screen.blit(images[(Team.NOTEAM, ImageId.CAPTURE_HINT)], (x * TILE_SIZE, y * TILE_SIZE))


def draw_highlight(screen: pygame.Surface, x: int, y: int):
    screen.blit(images[(Team.NOTEAM, ImageId.HIGHLIGHT)], (x*TILE_SIZE, y*TILE_SIZE))


def draw_outline(screen: pygame.Surface, x: int, y: int):
    screen.blit(images[(Team.NOTEAM, ImageId.OUTLINE)], (x*TILE_SIZE, y*TILE_SIZE))


def clamp(n: Union[float, int], a: Union[float, int], b: Union[float, int]):
    return max(min(b, n), a)


def play_sound(sound: SoundId, volume=0.7):
    for channel in channels:
        if channel.get_busy():
            continue
        channel.set_volume(volume)
        channel.play(sounds[sound])
        return True
    return False