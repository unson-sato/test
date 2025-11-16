# Phase 8: Effects & Lyric Motion

## Overview

Phase 8 applies visual effects, color grading, and animated lyric motion graphics to enhance the final music video.

## Purpose

- Apply visual effects (fx_and_treatments from shot-grammar)
- Color grading and color correction
- Lyric motion graphics synchronized to audio
- Visual polish and enhancement
- Particle effects, glows, and stylization

## Input Requirements

- Phase 7: Assembled timeline
- Shot-grammar: fx_and_treatments rules
- Lyrics data: Word-level timing (optional)

## Shot-Grammar FX

From `shot-grammar.json`:

- slow_motion / fast_motion
- strobe_effect
- grain_texture
- color_grade_* (teal_orange, monochrome, desaturated, oversaturated)
- lens_flare (anamorphic, classic, digital)
- chromatic_aberration
- vignette
- double_exposure
- glitch_digital
- light_leaks
- lens_distortion

## Process Flow

1. Load timeline from Phase 7
2. Load fx rules from shot-grammar
3. Apply color grading per section
4. Add lyric motion graphics
5. Apply stylistic effects
6. Export enhanced timeline

## Output

- Enhanced timeline with effects
- Lyric timing data
- Color grading presets

---

**Status**: Skeleton implemented
**Next Phase**: Phase 9 (Final Rendering)
