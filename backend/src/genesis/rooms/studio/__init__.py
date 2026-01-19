"""Studio module for video synthesis."""

from genesis.rooms.studio.agent import StudioAgent
from genesis.rooms.studio.schemas import (
    AudioTrack,
    PanelVideoSegment,
    StudioInput,
    StudioOutput,
    VideoComposition,
)

__all__ = [
    "StudioAgent",
    "AudioTrack",
    "PanelVideoSegment",
    "StudioInput",
    "StudioOutput",
    "VideoComposition",
]
