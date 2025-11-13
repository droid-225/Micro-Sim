from __future__ import annotations

import math
import random
from typing import Iterable

import pygame

from settings import (
    BOND_FORCE_THRESHOLD,
    COULOMB_CONSTANT,
    DEFAULT_CHARGE_STRENGTH,
    DEFAULT_MAX_PARTICLES,
    DEFAULT_SPAWN_COUNT,
    DEFAULT_TIME_SCALE,
    DEFAULT_ZOOM,
    DAMPING,
    MAX_CHARGE_STRENGTH,
    MAX_TIME_SCALE,
    MAX_FORCE,
    MIN_CHARGE_STRENGTH,
    MIN_TIME_SCALE,
    PARTICLE_MIN_DISTANCE,
    PARTICLE_RADIUS,
    PARTICLE_SPEED_RANGE,
    REPULSION_MULTIPLIER,
    RESTITUTION,
    SIMULATION_HEIGHT,
    SIMULATION_WIDTH,
)
from .particle import Particle


class Simulation:
    """
    Manages the set of particles and their interactions.
    """

    def __init__(self) -> None:
        self.particles: list[Particle] = []
        self.bounds = pygame.Rect(0, 0, SIMULATION_WIDTH, SIMULATION_HEIGHT)
        self.charge_strength = DEFAULT_CHARGE_STRENGTH
        self.max_particles = DEFAULT_MAX_PARTICLES
        self.spawn_count = DEFAULT_SPAWN_COUNT
        self.zoom = DEFAULT_ZOOM
        self.origin = pygame.Vector2(0, 0)
        self.time_scale = DEFAULT_TIME_SCALE

    # Particle management -------------------------------------------------

    def spawn_particle(self, position: pygame.Vector2, charge: float | None = None) -> None:
        if len(self.particles) >= self.max_particles:
            return

        if charge is None:
            charge = random.choice([-1.0, 1.0])

        vx = random.uniform(*PARTICLE_SPEED_RANGE)
        vy = random.uniform(*PARTICLE_SPEED_RANGE)

        particle = Particle(
            charge=charge,
            position=self._clamp_position(position),
            velocity=pygame.Vector2(vx, vy),
        )
        self.particles.append(particle)

    def spawn_particles(self, position: pygame.Vector2, charge: float | None = None) -> None:
        radius = PARTICLE_RADIUS * 4
        for _ in range(self.spawn_count):
            offset = pygame.Vector2(
                random.uniform(-radius, radius),
                random.uniform(-radius, radius),
            )
            particle_charge = charge if charge is not None else random.choice([-1.0, 1.0])
            self.spawn_particle(position + offset, particle_charge)

    def remove_particle_at(self, position: pygame.Vector2) -> None:
        if not self.particles:
            return

        target, distance = None, float("inf")
        for particle in self.particles:
            dist = particle.position.distance_to(position)
            if dist < distance and dist <= particle.radius * 1.5:
                target = particle
                distance = dist

        if target:
            self.particles.remove(target)

    def get_particle_at(self, position: pygame.Vector2) -> Particle | None:
        for particle in reversed(self.particles):
            if particle.position.distance_to(position) <= particle.radius:
                return particle
        return None

    # Simulation ----------------------------------------------------------

    def update(self, dt: float) -> None:
        if not self.particles:
            return

        scaled_dt = dt * self.time_scale

        forces, pair_forces = self._compute_forces()

        for particle, total_force in zip(self.particles, forces):
            particle.apply_force(total_force, scaled_dt)

        self._handle_collisions(pair_forces)

        for particle in self.particles:
            particle.velocity *= DAMPING
            particle.update(scaled_dt, self.bounds)

    def _compute_forces(self) -> tuple[list[pygame.Vector2], dict[tuple[int, int], float]]:
        count = len(self.particles)
        forces = [pygame.Vector2() for _ in range(count)]
        pair_forces: dict[tuple[int, int], float] = {}

        for i in range(count):
            for j in range(i + 1, count):
                a = self.particles[i]
                b = self.particles[j]

                delta = a.position - b.position
                distance_sq = max(delta.length_squared(), PARTICLE_MIN_DISTANCE**2)
                distance = math.sqrt(distance_sq)

                if distance == 0:
                    direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                    if direction.length_squared() == 0:
                        direction = pygame.Vector2(1, 0)
                    direction = direction.normalize()
                else:
                    direction = delta / distance

                force_magnitude = (
                    COULOMB_CONSTANT
                    * self.charge_strength
                    * a.charge
                    * b.charge
                    / distance_sq
                )
                if a.charge * b.charge > 0:
                    force_magnitude *= REPULSION_MULTIPLIER
                force_vector = direction * force_magnitude

                if force_vector.length() > MAX_FORCE:
                    force_vector.scale_to_length(MAX_FORCE)

                forces[i] += force_vector
                forces[j] -= force_vector

                pair_forces[(i, j)] = force_magnitude

        return forces, pair_forces

    def _handle_collisions(self, pair_forces: dict[tuple[int, int], float]) -> None:
        count = len(self.particles)
        for i in range(count):
            for j in range(i + 1, count):
                a = self.particles[i]
                b = self.particles[j]

                delta = b.position - a.position
                distance = delta.length()
                min_distance = a.radius + b.radius

                if distance == 0:
                    normal = pygame.Vector2(1, 0)
                    distance = 0.001
                else:
                    normal = delta / distance

                if distance >= min_distance:
                    continue

                overlap = min_distance - distance
                force_scalar = pair_forces.get((i, j), 0.0)
                self._resolve_pair(a, b, normal, overlap, force_scalar)

    # Rendering -----------------------------------------------------------

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        for particle in self.particles:
            particle.draw(surface, self.zoom, self.origin, font)

    # Configuration -------------------------------------------------------

    def set_zoom(self, zoom: float) -> None:
        self.zoom = max(0.4, min(zoom, 3.0))
        self.bounds.width = int(SIMULATION_WIDTH / self.zoom)
        self.bounds.height = int(SIMULATION_HEIGHT / self.zoom)

    def set_charge_strength(self, value: float) -> None:
        self.charge_strength = max(MIN_CHARGE_STRENGTH, min(value, MAX_CHARGE_STRENGTH))

    def set_spawn_count(self, count: int) -> None:
        self.spawn_count = max(1, min(count, 20))

    def set_max_particles(self, count: int) -> None:
        self.max_particles = max(1, min(count, 1000))

    def set_time_scale(self, value: float) -> None:
        self.time_scale = max(MIN_TIME_SCALE, min(value, MAX_TIME_SCALE))

    def reset(self) -> None:
        self.particles.clear()
        Particle.id_counter = 0

    # Utilities -----------------------------------------------------------

    def __iter__(self) -> Iterable[Particle]:
        return iter(self.particles)

    def _clamp_position(self, position: pygame.Vector2) -> pygame.Vector2:
        x = max(
            self.bounds.left + PARTICLE_RADIUS,
            min(self.bounds.right - PARTICLE_RADIUS, position.x),
        )
        y = max(
            self.bounds.top + PARTICLE_RADIUS,
            min(self.bounds.bottom - PARTICLE_RADIUS, position.y),
        )
        return pygame.Vector2(x, y)

    def _resolve_pair(
        self,
        a: Particle,
        b: Particle,
        normal: pygame.Vector2,
        overlap: float,
        force_scalar: float,
    ) -> None:
        correction = normal * (overlap / 2)
        a.position -= correction
        b.position += correction

        relative_velocity = b.velocity - a.velocity
        normal_speed = relative_velocity.dot(normal)

        if a.charge * b.charge < 0 and abs(force_scalar) >= BOND_FORCE_THRESHOLD:
            average_normal = (a.velocity.dot(normal) + b.velocity.dot(normal)) / 2
            a.velocity += normal * (average_normal - a.velocity.dot(normal))
            b.velocity += normal * (average_normal - b.velocity.dot(normal))

            tangent = pygame.Vector2(-normal.y, normal.x)
            avg_tangent = (a.velocity.dot(tangent) + b.velocity.dot(tangent)) / 2
            a.velocity += tangent * (avg_tangent - a.velocity.dot(tangent))
            b.velocity += tangent * (avg_tangent - b.velocity.dot(tangent))
        else:
            if normal_speed > 0:
                return

            impulse_mag = -(1 + RESTITUTION) * normal_speed
            impulse_mag /= (1 / a.mass) + (1 / b.mass)
            impulse = normal * impulse_mag

            a.velocity -= impulse / a.mass
            b.velocity += impulse / b.mass

