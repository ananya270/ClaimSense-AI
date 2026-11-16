"""NLP Claim Description Analysis Package (Phase 6)."""

from backend.services.nlp.service import ClaimNLPService
from backend.services.nlp.preprocessing import (
    normalize_text,
    segment_sentences,
    extract_keywords_and_phrases,
    extract_temporal_expressions,
)
from backend.services.nlp.entity_extractor import extract_entities
from backend.services.nlp.event_extractor import extract_events
from backend.services.nlp.chronology import reconstruct_chronology
from backend.services.nlp.classifier import classify_accident_type
from backend.services.nlp.damage_extractor import extract_reported_damages
from backend.services.nlp.consistency import cross_check_consistency

__all__ = [
    "ClaimNLPService",
    "normalize_text",
    "segment_sentences",
    "extract_keywords_and_phrases",
    "extract_temporal_expressions",
    "extract_entities",
    "extract_events",
    "reconstruct_chronology",
    "classify_accident_type",
    "extract_reported_damages",
    "cross_check_consistency",
]
