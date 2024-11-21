from enum import Enum


class DataExtractionType(str, Enum):
    TIMELINE = "timeline"
    BATCHES = "batches"
