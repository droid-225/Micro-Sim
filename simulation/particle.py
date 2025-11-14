from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, Tuple

import pygame

from settings import (
    COLOR_NEGATIVE,
    COLOR_NEUTRAL,
    COLOR_POSITIVE,
    POSITIVE_PARTICLE_MASS,
    NEGATIVE_PARTICLE_MASS,
    PARTICLE_RADIUS,
)


@dataclass
class Particle:
    """
    Represents a charged particle within the simulation.
    """

    charge: float
    position: pygame.Vector2
    velocity: pygame.Vector2
    radius: int = PARTICLE_RADIUS
    mass: float = POSITIVE_PARTICLE_MASS
    id_counter: ClassVar[int] = 0
    color_override: Tuple[int, int, int] | None = None

    id: int = field(init=False)

    def __post_init__(self) -> None:
        self.id = Particle.id_counter
        Particle.id_counter += 1

    @property
    def color(self) -> Tuple[int, int, int]:
        if self.color_override:
            return self.color_override
        if self.charge > 0:
            return COLOR_POSITIVE
        if self.charge < 0:
            self.mass = NEGATIVE_PARTICLE_MASS
            return COLOR_NEGATIVE
        return COLOR_NEUTRAL

    def apply_force(self, force: pygame.Vector2, dt: float) -> None:
        """
        Integrate the incoming force into the particle's velocity.
        """
        acceleration = force / self.mass
        self.velocity += acceleration * dt

    def update(self, dt: float, bounds: pygame.Rect) -> None:
        """
        Integrate velocity into position and handle boundary collisions.
        """
        self.position += self.velocity * dt
        self._apply_boundary(bounds)

    def _apply_boundary(self, bounds: pygame.Rect) -> None:
        if self.position.x - self.radius < bounds.left:

            self.position.x = bounds.left + self.radius
            self.velocity.x *= -1
        elif self.position.x + self.radius > bounds.right:
            self.position.x = bounds.right - self.radius
            self.velocity.x *= -1

        if self.position.y - self.radius < bounds.top:
            self.position.y = bounds.top + self.radius
            self.velocity.y *= -1
        elif self.position.y + self.radius > bounds.bottom:
            self.position.y = bounds.bottom - self.radius
            self.velocity.y *= -1

    def draw(
        self,
        surface: pygame.Surface,
        zoom: float,
        origin: pygame.Vector2,
        font: pygame.font.Font,
    ) -> None:
        """
        Render the particle to the target surface.
        """
        screen_pos_vec = (self.position - origin) * zoom
        screen_pos = (int(screen_pos_vec.x), int(screen_pos_vec.y))
        scaled_radius = max(4, int(self.radius * zoom))

        pygame.draw.circle(surface, self.color, screen_pos, scaled_radius)
        #label = font.render(str(self.id), True, (255, 255, 255))
        label = font.render("+" if self.charge > 0 else "-", True, (255, 255, 255))
        label_rect = label.get_rect(center=screen_pos)
        surface.blit(label, label_rect)

