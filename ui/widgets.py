from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Sequence

import pygame

from settings import (
    COLOR_BUTTON,
    COLOR_BUTTON_HOVER,
    COLOR_PANEL_BORDER,
    COLOR_SLIDER_HANDLE,
    COLOR_SLIDER_TRACK,
    COLOR_TEXT,
)


class Widget:
    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect
        self.hovered = False
        self.active = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

    def update(self, mouse_pos: tuple[int, int]) -> None:
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        raise NotImplementedError


class Button(Widget):
    def __init__(self, rect: pygame.Rect, text: str, callback: Callable[[], None]) -> None:
        super().__init__(rect)
        self.text = text
        self.callback = callback

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            self.callback()
            return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        color = COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.rect, 2, border_radius=6)
        label = font.render(self.text, True, COLOR_TEXT)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)


class Toggle(Widget):
    def __init__(self, rect: pygame.Rect, text: str, initial: bool, callback: Callable[[bool], None]) -> None:
        super().__init__(rect)
        self.text = text
        self.value = initial
        self.callback = callback

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            self.value = not self.value
            self.callback(self.value)
            return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        bg_color = COLOR_BUTTON_HOVER if self.value else COLOR_BUTTON
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.rect, 2, border_radius=6)
        label = font.render(f"{self.text}: {'ON' if self.value else 'OFF'}", True, COLOR_TEXT)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)


class CycleButton(Widget):
    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        options: Sequence[str],
        initial_index: int,
        callback: Callable[[str], None],
    ) -> None:
        super().__init__(rect)
        self.label = label
        self.options = list(options)
        self.index = initial_index
        self.callback = callback

    @property
    def value(self) -> str:
        return self.options[self.index]

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            self.index = (self.index + 1) % len(self.options)
            self.callback(self.value)
            return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        bg = COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON
        pygame.draw.rect(surface, bg, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.rect, 2, border_radius=6)
        text = f"{self.label}: {self.value}"
        label_surface = font.render(text, True, COLOR_TEXT)
        label_rect = label_surface.get_rect(center=self.rect.center)
        surface.blit(label_surface, label_rect)


class Slider(Widget):
    def __init__(
        self,
        rect: pygame.Rect,
        min_value: float,
        max_value: float,
        value: float,
        callback: Callable[[float], None],
        *,
        format_value: Optional[Callable[[float], str]] = None,
        label: str | None = None,
    ) -> None:
        super().__init__(rect)
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.callback = callback
        self.format_value = format_value or (lambda val: f"{val:.2f}")
        self.label = label

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            self.active = True
            self._update_value(event.pos[0])
            return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.active = False
        if event.type == pygame.MOUSEMOTION and self.active:
            self._update_value(event.pos[0])
            return True
        return False

    def _update_value(self, mouse_x: int) -> None:
        t = (mouse_x - self.rect.left) / self.rect.width
        t = max(0.0, min(1.0, t))
        self.value = self.min_value + t * (self.max_value - self.min_value)
        self.callback(self.value)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        track_rect = pygame.Rect(self.rect.left, self.rect.centery - 4, self.rect.width, 8)
        pygame.draw.rect(surface, COLOR_SLIDER_TRACK, track_rect, border_radius=4)

        t = (self.value - self.min_value) / (self.max_value - self.min_value)
        handle_x = self.rect.left + t * self.rect.width
        handle_rect = pygame.Rect(0, 0, 14, 20)
        handle_rect.center = (handle_x, self.rect.centery)
        pygame.draw.rect(surface, COLOR_SLIDER_HANDLE, handle_rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, handle_rect, 2, border_radius=4)

        label_text = self.format_value(self.value)
        if self.label:
            label_text = f"{self.label}: {label_text}"

        label_surface = font.render(label_text, True, COLOR_TEXT)
        label_rect = label_surface.get_rect(midtop=(self.rect.centerx, self.rect.bottom + 6))
        surface.blit(label_surface, label_rect)


class TextInput(Widget):
    def __init__(
        self,
        rect: pygame.Rect,
        initial_text: str,
        on_commit: Callable[[str], None],
        *,
        restrict_numeric: bool = False,
    ) -> None:
        super().__init__(rect)
        self.text = initial_text
        self.on_commit = on_commit
        self.restrict_numeric = restrict_numeric
        self.active = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return self.active
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.on_commit(self.text)
                return True
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            char = event.unicode
            if char and char.isprintable():
                if self.restrict_numeric and not char.isdigit():
                    return False
                self.text += char
                return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        bg = COLOR_BUTTON_HOVER if self.active else COLOR_BUTTON
        pygame.draw.rect(surface, bg, self.rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.rect, 2, border_radius=4)

        label_surface = font.render(self.text or " ", True, COLOR_TEXT)
        label_rect = label_surface.get_rect(center=self.rect.center)
        surface.blit(label_surface, label_rect)

