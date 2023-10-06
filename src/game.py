import pygame.draw
import controls
from audio_handler import AudioHandler
from controls import handle_player_controls
from level import Level, Obstacle
from math_utils import *
from player import Player, Direction


class Game:
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    BACKGROUND_COLOR = 'black'
    FPS = 60
    TEXT_FONT = ('Mono', 20)

    def __init__(self):
        self.screen = pygame.display.set_mode((Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT))
        pygame.display.set_caption('Headphones Recommended')
        pygame.font.init()
        font = pygame.font.SysFont(*Game.TEXT_FONT)
        self.text = font.render(controls.get_control_hint(), True, 'white')
        self.audio_handler = AudioHandler()

        self.level = Level()
        self.level.generate_objects(
            Game.SCREEN_WIDTH,
            Game.SCREEN_HEIGHT,
            Obstacle.DEFAULT_RADIUS
        )

        self.player = Player(
            Position(*self.level.start_position),
            Angle(np.pi / 2),
            (Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT)
        )

        self.running = True
        self.loop()

    def draw_text(self):
        self.screen.blit(self.text, (20, 20))

    def redraw(self):
        self.screen.fill(Game.BACKGROUND_COLOR)
        self.draw_player()
        self.draw_objects()
        self.draw_text()
        pygame.display.flip()

    def draw_player(self):
        frustum_radius = Player.VIEWING_BOUNDS.radius
        offset_angle = Player.VIEWING_BOUNDS.angle
        arc_start = self.player.direction - offset_angle

        pygame.draw.circle(
            self.screen,
            Player.COLOR,
            self.player.position,
            Player.BODY_RADIUS
        )

        pygame.draw.arc(
            self.screen,
            Player.FRUSTUM_COLOR,
            (
                self.player.position.x - frustum_radius,
                self.player.position.y - frustum_radius,
                2 * frustum_radius,
                2 * frustum_radius
            ),
            arc_start.rad, (arc_start + offset_angle * 2).rad,
            1
        )

        arc_start_coordinate = PolarCoordinate(arc_start, frustum_radius)
        arc_end_coordinate = PolarCoordinate(arc_start + offset_angle * 2, frustum_radius)
        arc_start_world_coordinate = self.player.relative_polar_coordinate_to_world_position(arc_start_coordinate)
        arc_end_world_coordinate = self.player.relative_polar_coordinate_to_world_position(arc_end_coordinate)

        pygame.draw.line(
            self.screen,
            Player.FRUSTUM_COLOR,
            (self.player.position.x, self.player.position.y),
            (arc_start_world_coordinate.x, arc_start_world_coordinate.y)
        )

        pygame.draw.line(
            self.screen,
            Player.FRUSTUM_COLOR,
            (self.player.position.x, self.player.position.y),
            (arc_end_world_coordinate.x, arc_end_world_coordinate.y)
        )

    def draw_objects(self):
        for o in self.level.obstacles:
            pygame.draw.circle(
                self.screen,
                o.color,
                o.position,
                Obstacle.DEFAULT_RADIUS
            )

        pygame.draw.circle(
            self.screen,
            Level.TARGET_COLOR,
            self.level.target,
            Level.TARGET_RADIUS
        )

    def scan_surroundings(self, adjust_audio):
        radius = Player.VIEWING_BOUNDS.radius
        closest_right_obstacle_dist = radius + 1
        closest_center_obstacle_dist = radius + 1
        closest_left_obstacle_dist = radius + 1

        for o in self.level.obstacles:
            relative_polar_coordinate = self.player.world_position_to_relative_polar_coordinate(o.position)
            if self.player.can_see(relative_polar_coordinate):
                o.color = Obstacle.DEFAULT_COLOR_IN_SIGHT

                """if the player collides with an obstacle, the game ends"""
                if self.player.distance_to(o.position) <= Player.BODY_RADIUS:
                    self.player.is_alive = False
                    self.audio_handler.play_game_over_sound(self.player)
                    return

                obstacle_direction = self.player.direction_relative_to_player(relative_polar_coordinate)
                distance = self.player.distance_to(o.position)

                """adjust the volume according to the closest obstacle per direction"""
                if adjust_audio:
                    if obstacle_direction == Direction.Left:
                        if distance < closest_left_obstacle_dist:
                            closest_left_obstacle_dist = distance
                    elif obstacle_direction == Direction.Center:
                        if distance < closest_center_obstacle_dist:
                            closest_center_obstacle_dist = distance
                    else:
                        if distance < closest_right_obstacle_dist:
                            closest_right_obstacle_dist = distance
            else:
                o.color = Obstacle.DEFAULT_COLOR

        """if the player reaches the target, the game ends"""
        dist_to_target = self.player.distance_to(self.level.target)
        if dist_to_target < Level.TARGET_RADIUS + Player.BODY_RADIUS:
            self.audio_handler.play_completion_sound(self.player)

        if adjust_audio:
            self.audio_handler.set_volume(
                AudioHandler.distance_to_volume(closest_left_obstacle_dist, radius),
                AudioHandler.distance_to_volume(closest_center_obstacle_dist, radius),
                AudioHandler.distance_to_volume(closest_right_obstacle_dist, radius)
            )

            """the target makes a sound, if the player is facing towards it"""
            target_polar_coordinate = self.player.world_position_to_relative_polar_coordinate(self.level.target)
            if self.player.is_facing(target_polar_coordinate):
                target_direction = self.player.direction_relative_to_player(target_polar_coordinate)
                target_panning = Player.DIRECTION_TO_PANNING[target_direction]
                self.audio_handler.set_target_panning(target_panning)
                self.audio_handler.set_target_volume(
                    AudioHandler.distance_to_volume(dist_to_target, Game.SCREEN_WIDTH)
                )
            else:
                self.audio_handler.set_target_volume(0.0)

    def loop(self):
        clock = pygame.time.Clock()
        adjust_audio_timer = 0

        while self.running:
            if not self.player.is_alive:
                break
            adjust_audio_timer += clock.tick(Game.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if adjust_audio_timer >= AudioHandler.ADJUST_AUDIO_TIMEOUT:
                self.scan_surroundings(True)
                adjust_audio_timer = 0
            else:
                self.scan_surroundings(False)
            handle_player_controls(self.player)

            self.redraw()

        while True:
            pass
