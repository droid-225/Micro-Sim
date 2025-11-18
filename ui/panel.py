from __future__ import annotations

from typing import Callable, Iterable

import pygame

from settings import (
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_TEXT,
    FONT_NAME,
    FONT_SIZE,
    MAX_CHARGE_STRENGTH,
    MAX_TIME_SCALE,
    MIN_CHARGE_STRENGTH,
    MIN_TIME_SCALE,
    PANEL_WIDTH,
    SIMULATION_HEIGHT,
    SIMULATION_WIDTH,
)
from .widgets import Button, CycleButton, Slider, TextInput, Toggle, Widget


class ControlPanel:
    """
    Sidebar UI managing simulation parameters.
    """

    def __init__(
        self,
        simulation,
        *,
        add_mode_callback: Callable[[bool], None],
        charge_mode_callback: Callable[[str], None],
        speed_callback: Callable[[float], None],
        reset_callback: Callable[[], None],
    ) -> None:
        self.simulation = simulation
        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        self.surface = pygame.Surface((PANEL_WIDTH, SIMULATION_HEIGHT))
        self.rect = pygame.Rect(SIMULATION_WIDTH, 0, PANEL_WIDTH, SIMULATION_HEIGHT)
        self.widgets: list[Widget] = []

        margin = 20
        x = margin
        width = PANEL_WIDTH - margin * 2
        y = margin
        spacing = 70

        # Charge strength slider
        self.charge_slider = Slider(
            pygame.Rect(x, y, width, 20),
            MIN_CHARGE_STRENGTH,
            MAX_CHARGE_STRENGTH,
            simulation.charge_strength,
            simulation.set_charge_strength,
            format_value=lambda v: f"{v:.2f}",
            label="Charge Strength",
        )
        self.widgets.append(self.charge_slider)
        y += spacing

        # Spawn count slider (integer)
        self.spawn_slider = Slider(
            pygame.Rect(x, y, width, 20),
            1,
            10,
            float(simulation.spawn_count),
            lambda val: simulation.set_spawn_count(int(val)),
            format_value=lambda v: f"{int(v)}",
            label="Spawn Count",
        )
        self.widgets.append(self.spawn_slider)
        y += spacing

        # Max particles slider
        # Zoom slider
        self.zoom_slider = Slider(
            pygame.Rect(x, y, width, 20),
            0.5,
            2.5,
            simulation.zoom,
            simulation.set_zoom,
            format_value=lambda v: f"{v:.2f}x",
            label="Zoom",
        )
        self.widgets.append(self.zoom_slider)
        y += spacing

        # Toggle between add/move mode
        self.mode_toggle = Toggle(
            pygame.Rect(x, y, width, 32),
            "Add Mode",
            True,
            add_mode_callback,
        )
        self.widgets.append(self.mode_toggle)
        y += spacing

        # Simulation speed slider
        self.speed_slider = Slider(
            pygame.Rect(x, y, width, 20),
            MIN_TIME_SCALE,
            MAX_TIME_SCALE,
            simulation.time_scale,
            speed_callback,
            format_value=lambda v: f"{v:.2f}x",
            label="Time Scale",
        )
        self.widgets.append(self.speed_slider)
        y += spacing

        # Charge selection cycle
        self.charge_cycle = CycleButton(
            pygame.Rect(x, y, width, 32),
            "Spawn Charge",
            ["Random", "Positive", "Negative"],
            0,
            charge_mode_callback,
        )
        self.widgets.append(self.charge_cycle)
        y += spacing

        # Reset button
        self.widgets.append(
            Button(
                pygame.Rect(x, y, width, 36),
                "Reset Simulation",
                reset_callback,
            )
        )
        y += spacing

        # Max particle input
        self.max_particles_input = TextInput(
            pygame.Rect(x, y, width, 32),
            str(self.simulation.max_particles),
            lambda text: self._commit_max_particles(text),
            restrict_numeric=True,
        )
        self.widgets.append(self.max_particles_input)

    def handle_event(self, event: pygame.event.Event) -> bool:
        localized = self._localize_event(event)

        for widget in self.widgets:
            if widget.handle_event(localized):
                return True
        return False

    def update(self, mouse_pos: tuple[int, int]) -> None:
        local_pos = (mouse_pos[0] - self.rect.left, mouse_pos[1] - self.rect.top)

        for widget in self.widgets:
            widget.update(local_pos)

    def draw(self, surface: pygame.Surface, hud_lines: Iterable[str]) -> None:
        # Sync live values before drawing
        self.charge_slider.value = self.simulation.charge_strength
        self.spawn_slider.value = float(self.simulation.spawn_count)
        self.zoom_slider.value = self.simulation.zoom
        self.speed_slider.value = self.simulation.time_scale
        if not self.max_particles_input.active:
            self.max_particles_input.text = str(self.simulation.max_particles)

        self.surface.fill(COLOR_PANEL_BG)
        pygame.draw.rect(self.surface, COLOR_PANEL_BORDER, self.surface.get_rect(), 2)

        for widget in self.widgets:
            widget.draw(self.surface, self.font)

        # HUD text at bottom
        y = self.surface.get_height() - 10
        for line in reversed(list(hud_lines)):
            label = self.font.render(line, True, COLOR_TEXT)
            y -= label.get_height() + 4
            self.surface.blit(label, (12, y))

        surface.blit(self.surface, self.rect)

    def _localize_event(self, event: pygame.event.Event) -> pygame.event.Event:
        if hasattr(event, "pos"):
            local_pos = (
                event.pos[0] - self.rect.left,
                event.pos[1] - self.rect.top,
            )
            event_dict = dict(event.dict)
            event_dict["pos"] = local_pos
            return pygame.event.Event(event.type, event_dict)
        return event

    def set_charge_mode(self, mode: str) -> None:
        lookup = {"random": 0, "positive": 1, "negative": 2}
        idx = lookup.get(mode.lower(), 0)
        self.charge_cycle.index = idx

    def _commit_max_particles(self, text: str) -> None:
        try:
            value = int(text)
        except ValueError:
            return
        self.simulation.set_max_particles(value)
        self.max_particles_input.text = str(self.simulation.max_particles)

