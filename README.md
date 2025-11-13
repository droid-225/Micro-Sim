# Charged Particle Simulator

A simple playground for experimenting with charged particles interacting through Coulomb forces. Built with Pygame and designed for quick tweaking via a control panel.

## Features

- Left panel displays the simulation; right panel exposes controls.
- Particles are coloured by charge (red = positive, blue = negative) and labelled with an ID.
- Left click (Add mode) to spawn new particles near the cursor; spawn count, spawn charge (positive/negative/random), and charge strength (0.1x–100x) are configurable.
- Toggle to switch left click between spawning particles and moving them (drag and drop).
- Right click removes the particle closest to the cursor.
- Scroll wheel or +/- keys adjust zoom; slider available in UI.
- Sliders to control charge strength, spawn count, zoom, and simulation speed (0.25x–4x); max particle count can be edited directly.
- Particles bounce off the environment bounds; zoom effectively grows/shrinks the playable area.
- Charged interactions: like charges repel, opposite charges attract and can bond edge-to-edge when attraction dominates collisions.
- Slider ranges (charge strength, time scale) are configurable via `settings.py`.

## Getting Started

```bash
python -m venv .venv
.venv\Scripts\activate  # On PowerShell
pip install -r requirements.txt
python sim.py
```

## Controls Recap

- Left click in add mode: spawn `spawn_count` particles.
- Left click in move mode: drag an existing particle.
- Right click: remove a particle.
- Mouse wheel or +/- keys: zoom in/out.
- Sliders/buttons in the control panel change parameters instantly.

