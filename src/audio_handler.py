from dataclasses import dataclass
from enum import Enum
import numpy as np
import pygame.mixer

from player import Direction, Player


class CMajorScale(Enum):
    C = 1
    D = 2
    E = 3
    F = 4
    G = 5
    A = 6
    B = 7


@dataclass
class Audio:
    MAX_VOLUME = .1
    C3_MAJOR_FREQUENCIES = {
        CMajorScale.C: 131,
        CMajorScale.D: 147,
        CMajorScale.E: 165,
        CMajorScale.F: 175,
        CMajorScale.G: 196,
        CMajorScale.A: 220,
        CMajorScale.B: 247,
    }

    C4_MAJOR_FREQUENCIES = {
        CMajorScale.C: 262,
        CMajorScale.D: 294,
        CMajorScale.E: 330,
        CMajorScale.F: 349,
        CMajorScale.G: 392,
        CMajorScale.A: 440,
        CMajorScale.B: 494,
    }

    def __init__(self, sound_buffer, volume=1.0, panning=0.5):
        self.sound = pygame.mixer.Sound(sound_buffer)
        self.channel = self.sound.play(loops=-1)
        self.volume = volume
        self.panning = panning
        self.set_volume(volume)
        self.set_panning(panning)

    def set_panning(self, panning: float):
        """
        Adjust the direction, from which the sound is coming from

        :param panning: closer to 0 means further left, closer to 1 means further right
        """
        self.panning = panning
        self.channel.set_volume(1 - panning, panning)

    def set_volume(self, volume: float):
        self.volume = max(min(volume, Audio.MAX_VOLUME), 0)
        self.sound.set_volume(self.volume)


class AudioHandler:
    ADJUST_AUDIO_TIMEOUT = 60

    def __init__(self):
        pygame.mixer.init(size=32)
        self.left_sound = Audio(
            generate_sine_wave(Audio.C3_MAJOR_FREQUENCIES[CMajorScale.D]),
            panning=Player.DIRECTION_TO_PANNING[Direction.Left],
            volume=0.0
        )
        self.center_sound = Audio(
            generate_sine_wave(Audio.C4_MAJOR_FREQUENCIES[CMajorScale.E]),
            panning=Player.DIRECTION_TO_PANNING[Direction.Center],
            volume=0.0
        )
        self.right_sound = Audio(
            generate_sine_wave(Audio.C3_MAJOR_FREQUENCIES[CMajorScale.C]),
            panning=Player.DIRECTION_TO_PANNING[Direction.Right],
            volume=0.0
        )
        self.target_audio = Audio(
            generate_sine_wave_beep(Audio.C3_MAJOR_FREQUENCIES[CMajorScale.B]),
            panning=Player.DIRECTION_TO_PANNING[Direction.Center],
            volume=0.0
        )

    def set_panning(self, left, center, right):
        self.left_sound.set_panning(left)
        self.center_sound.set_panning(center)
        self.right_sound.set_panning(right)

    def set_target_panning(self, panning):
        self.target_audio.set_panning(panning)

    def set_target_volume(self, volume):
        self.target_audio.set_volume(volume)

    def set_volume(self, left, center, right):
        self.left_sound.set_volume(left)
        self.center_sound.set_volume(center)
        self.right_sound.set_volume(right)

    @staticmethod
    def distance_to_volume(distance, max_distance) -> float:
        return (1 - distance / max_distance) * Audio.MAX_VOLUME

    def play_completion_sound(self):
        self.set_volume(0.0, 0.0, 0.0)
        self.set_target_volume(0.0)

        sound = pygame.mixer.Sound("../assets/lvl_completed.mp3")
        channel = sound.play()
        while channel.get_busy():
            pass

    def play_game_over_sound(self):
        self.set_volume(0.0, 0.0, 0.0)
        self.set_target_volume(0.0)

        sound = pygame.mixer.Sound("../assets/game_over.mp3")
        channel = sound.play()
        while channel.get_busy():
            pass


def generate_sine_wave(frequency: int) -> np.ndarray:
    """
    Generate a monotone sound

    :param frequency: frequency of sound
    :return: sound buffer
    """
    return np.sin(2 * np.pi * np.arange(44100) * frequency / 44100).astype(np.float32)


def generate_sine_wave_beep(frequency: int) -> np.ndarray:
    """
    Generate a beeping sound

    :param frequency: frequency of sound
    :return: sound buffer
    """
    buffer = np.zeros(44100).astype(np.float32)
    buffer[:5000] = np.sin(2 * np.pi * np.arange(5000) * frequency / 5000).astype(np.float32)
    return buffer
