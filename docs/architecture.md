# TacticalVision Architecture

## Overview

TacticalVision is an educational computer-vision
video analytics system.

The system processes video frames, detects objects,
tracks them over time, analyzes their movement,
evaluates spatial zones, and records generated
events.

## Pipeline

Camera
↓
OpenCV
↓
YOLO
↓
Object Tracking
↓
Position Extraction
↓
Motion Analysis
↓
Zone Analysis
↓
Event Engine
↓
SQLite

## Components

### Camera

Responsible for acquiring frames from a webcam
or compatible video source.

### Detector

Uses a YOLO model to detect objects in frames.

### Tracker

Maintains object identities across consecutive frames.

### Trajectory Tracker

Stores recent positions for tracked objects.

### Motion Analyzer

Calculates approximate direction and pixel velocity.

### Zone Engine

Determines whether an object's center point is
inside a configured zone.

### Event Engine

Generates ENTER and EXIT events.

### Database

Persists event information using SQLite.

## Design Goals

- Modular architecture
- Low resource consumption
- Local execution
- Reproducible setup
- Testable components
- Clear separation of responsibilities
