from __future__ import annotations
import sys
import pygame

from settings import (
    COLOR_BACKGROUND,
    COLOR_TEXT,
    FPS,
    SIMULATION_HEIGHT,
    SIMULATION_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from simulation import Simulation
from ui.panel import ControlPanel


class App:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Charged Particle Simulator")
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.font = pygame.font.Font(None, 18)
        self.hud_font = pygame.font.Font(None, 22)
        self.sim_surface = pygame.Surface((SIMULATION_WIDTH, SIMULATION_HEIGHT))

        self.simulation = Simulation()
        self.add_mode = True
        self.dragging_particle = None
        self.drag_offset = pygame.Vector2()
        self.spawn_charge_mode = "random"

        self.panel = ControlPanel(
            self.simulation,
            add_mode_callback=self._set_add_mode,
            charge_mode_callback=self._set_spawn_charge_mode,
            speed_callback=self._set_time_scale,
            reset_callback=self._reset_simulation,
        )

    # Event handling -----------------------------------------------------

    def _set_add_mode(self, value: bool) -> None:
        self.add_mode = value
        self.dragging_particle = None

    def _set_spawn_charge_mode(self, value: str) -> None:
        self.spawn_charge_mode = value.lower()

    def _reset_simulation(self) -> None:
        self.simulation.reset()
        self.dragging_particle = None

    def _set_time_scale(self, value: float) -> None:
        self.simulation.set_time_scale(value)

    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            if not self._handle_events():
                break

            self._update(dt)
            self._render()

        pygame.quit()
        sys.exit()

    def _handle_events(self) -> bool:
        mouse_pos = pygame.mouse.get_pos()
        self.panel.update(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.panel.handle_event(event):
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.simulation.set_zoom(self.simulation.zoom - 0.1)
                if event.key in (pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self.simulation.set_zoom(self.simulation.zoom + 0.1)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_left_mouse_down(event.pos)
                elif event.button == 3:
                    self._handle_right_mouse_down(event.pos)
                elif event.button == 4:  # scroll up
                    self.simulation.set_zoom(self.simulation.zoom * 1.05)
                elif event.button == 5:  # scroll down
                    self.simulation.set_zoom(self.simulation.zoom / 1.05)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging_particle = None

            if event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)

        return True

    def _is_over_panel(self, position: tuple[int, int]) -> bool:
        return position[0] >= SIMULATION_WIDTH

    def _screen_to_world(self, position: tuple[int, int]) -> pygame.Vector2:
        x, y = position
        x = max(0, min(x, SIMULATION_WIDTH - 1))
        world_x = self.simulation.origin.x + x / self.simulation.zoom
        world_y = self.simulation.origin.y + y / self.simulation.zoom
        return pygame.Vector2(world_x, world_y)

    def _handle_left_mouse_down(self, position: tuple[int, int]) -> None:
        if self._is_over_panel(position):
            return

        world_pos = self._screen_to_world(position)

        if self.add_mode:
            charge = None
            if self.spawn_charge_mode == "positive":
                charge = 1.0
            elif self.spawn_charge_mode == "negative":
                charge = -1.0
            self.simulation.spawn_particles(world_pos, charge)
        else:
            particle = self.simulation.get_particle_at(world_pos)
            if particle:
                self.dragging_particle = particle
                self.drag_offset = particle.position - world_pos

    def _handle_right_mouse_down(self, position: tuple[int, int]) -> None:
        if self._is_over_panel(position):
            return
        world_pos = self._screen_to_world(position)
        self.simulation.remove_particle_at(world_pos)

    def _handle_mouse_motion(self, position: tuple[int, int]) -> None:
        if not self.dragging_particle:
            return
        world_pos = self._screen_to_world(position)
        self.dragging_particle.position = world_pos + self.drag_offset
        self.dragging_particle.velocity.update(0, 0)

    # Update & render ----------------------------------------------------

    def _update(self, dt: float) -> None:
        if not self.dragging_particle:
            self.simulation.update(dt)
        else:
            # keep dragged particle within bounds
            bounds = self.simulation.bounds
            self.dragging_particle.position.x = max(
                bounds.left + self.dragging_particle.radius,
                min(bounds.right - self.dragging_particle.radius, self.dragging_particle.position.x),
            )
            self.dragging_particle.position.y = max(
                bounds.top + self.dragging_particle.radius,
                min(bounds.bottom - self.dragging_particle.radius, self.dragging_particle.position.y),
            )

    def _render(self) -> None:
        self.screen.fill(COLOR_BACKGROUND)

        # Simulation area
        self.sim_surface.fill(COLOR_BACKGROUND)
        self.simulation.draw(self.sim_surface, self.hud_font)

        hud_lines = [
            f"Particles: {len(self.simulation.particles)}/{self.simulation.max_particles}",
            f"Mode: {'Add' if self.add_mode else 'Move'}",
            f"Spawn Charge: {self.spawn_charge_mode.title()}",
            f"Time Scale: {self.simulation.time_scale:.2f}x",
            f"Zoom: {self.simulation.zoom:.2f}x",
        ]
        self._draw_hud(self.sim_surface, hud_lines)
        self.screen.blit(self.sim_surface, (0, 0))

        # Control panel
        panel_hud_lines = [
            f"FPS: {self.clock.get_fps():.1f}",
            "Left Click: add/move particles",
            "Right Click: remove particle",
            "Scroll: zoom",
        ]
        self.panel.set_charge_mode(self.spawn_charge_mode)
        self.panel.draw(self.screen, panel_hud_lines)

        pygame.display.flip()

    def _draw_hud(self, surface: pygame.Surface, lines: list[str]) -> None:
        y = 10
        for line in lines:
            label = self.font.render(line, True, COLOR_TEXT)
            surface.blit(label, (10, y))
            y += label.get_height() + 4


def main() -> None:
    app = App()
    app.run()


if __name__ == "__main__":
    main()

