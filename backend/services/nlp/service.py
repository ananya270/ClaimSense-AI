"""Comprehensive Claim Description NLP Analysis Orchestrator (Phase 6)."""

import time
from typing import Dict, Any, List, Optional
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


class ClaimNLPService:
    """Singleton service for executing full NLP analysis on claim descriptions."""

    ENGINE_VERSION = "1.0.0"

    @classmethod
    def analyze_claim_narrative(
        cls,
        text: str,
        claim_id: Optional[str] = None,
        claimant_name: Optional[str] = None,
        extracted_doc_rows: Optional[List[Dict[str, Any]]] = None,
        claim_record: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Executes full NLP analysis pipeline on a claim statement.
        
        Performs:
        1. Preprocessing & Normalization
        2. Sentence Segmentation
        3. Entity Extraction
        4. Accident Event Identification
        5. Chronological Timeline Reconstruction
        6. Accident Type Classification
        7. Claimant-Reported Damage Extraction
        8. Cross-Source Document Consistency Verification
        """
        start_time = time.perf_counter()

        original_text = text or ""
        normalized_text = normalize_text(original_text)
        sentences = segment_sentences(normalized_text)

        # 1. Entity Extraction
        entities = extract_entities(normalized_text, claimant_name_hint=claimant_name)

        # 2. Event Extraction & Chronology
        raw_events = extract_events(normalized_text, sentences)
        chronology_data = reconstruct_chronology(raw_events, sentences, raw_text=normalized_text)

        # 3. Accident Type Classification
        classification = classify_accident_type(normalized_text)

        # 4. Damage Description Extraction
        reported_damages = extract_reported_damages(normalized_text, sentences)

        # 5. Cross-Source Document Consistency
        consistency_data = cross_check_consistency(
            claim_id=claim_id or "UNKNOWN",
            nlp_entities=entities,
            nlp_classification=classification,
            reported_damages=reported_damages,
            extracted_doc_rows=extracted_doc_rows or [],
            claim_record=claim_record or {},
        )

        # 6. Salient Keywords & Phrases
        keywords = extract_keywords_and_phrases(normalized_text)

        # 7. Collect Missing and Ambiguous Information
        missing_info = list(chronology_data.get("missing_temporal_info", []))
        ambiguous_info = list(chronology_data.get("ambiguous_temporal_info", []))

        if not reported_damages:
            missing_info.append("No specific vehicle components or panels were explicitly named as damaged in statement.")
        if not any(e["entity_type"] in ("ROAD_INTERSECTION", "LOCATION") for e in entities):
            missing_info.append("Accident location or cross street was not explicitly mentioned.")

        processing_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return {
            "claim_id": claim_id,
            "engine_version": cls.ENGINE_VERSION,
            "processing_status": "completed",
            "processing_time_ms": processing_time_ms,
            "original_narrative": original_text,
            "normalized_narrative": normalized_text,
            "total_sentences": len(sentences),
            "sentences": sentences,
            "keywords": keywords,
            "entities": entities,
            "total_entities": len(entities),
            "accident_classification": classification,
            "accident_type": classification.get("accident_type", "UNKNOWN"),
            "accident_type_confidence": classification.get("confidence", 0.0),
            "classification_method": classification.get("classification_method", "Linguistic Pattern Matching"),
            "classification_supporting_text": classification.get("supporting_text", ""),
            "events": raw_events,
            "total_events": len(raw_events),
            "chronology": chronology_data,
            "timeline": chronology_data.get("timeline", []),
            "reported_damages": reported_damages,
            "total_reported_damages": len(reported_damages),
            "consistency": consistency_data,
            "missing_information": missing_info,
            "ambiguous_information": ambiguous_info,
        }
