"""
Grounding Validator - Ensures LLM responses are factually grounded in source documents
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from rapidfuzz import fuzz
import json

logger = logging.getLogger(__name__)

class GroundingValidator:
    """
    Validates that LLM responses are grounded in source documents
    """
    
    def __init__(self, min_confidence: float = 0.8):
        self.min_confidence = min_confidence
        
    def validate_response(self, response: str, context_chunks: List[Dict]) -> Dict:
        """
        Validate an LLM response against provided context chunks
        
        Args:
            response: The LLM-generated response
            context_chunks: List of context chunks with text and metadata
            
        Returns:
            Dict containing validation results
        """
        validation_result = {
            "is_grounded": True,
            "grounding_score": 1.0,
            "unsupported_claims": [],
            "supported_claims": [],
            "citations_found": [],
            "confidence_breakdown": {},
            "recommendations": []
        }
        
        # Extract claims from response
        claims = self._extract_claims(response)
        
        # Validate each claim against context
        for claim in claims:
            claim_validation = self._validate_claim(claim, context_chunks)
            
            if claim_validation["is_supported"]:
                validation_result["supported_claims"].append({
                    "claim": claim,
                    "support_score": claim_validation["support_score"],
                    "source_chunk": claim_validation["source_chunk"],
                    "evidence": claim_validation["evidence"]
                })
            else:
                validation_result["unsupported_claims"].append({
                    "claim": claim,
                    "reason": claim_validation["reason"]
                })
                
        # Extract citations
        citations = self._extract_citations(response)
        validation_result["citations_found"] = citations
        
        # Calculate overall grounding score
        if claims:
            supported_count = len(validation_result["supported_claims"])
            validation_result["grounding_score"] = supported_count / len(claims)
            validation_result["is_grounded"] = validation_result["grounding_score"] >= self.min_confidence
            
        # Generate recommendations
        validation_result["recommendations"] = self._generate_recommendations(validation_result)
        
        return validation_result
    
    def _extract_claims(self, text: str) -> List[str]:
        """
        Extract individual claims from response text
        """
        # Split by sentences and filter out short ones
        sentences = re.split(r'[.!?]+', text)
        claims = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and not sentence.startswith(('Based on', 'According to', 'As per')):
                claims.append(sentence)
                
        return claims
    
    def _validate_claim(self, claim: str, context_chunks: List[Dict]) -> Dict:
        """
        Validate a single claim against context chunks
        """
        best_match = {
            "is_supported": False,
            "support_score": 0.0,
            "source_chunk": None,
            "evidence": "",
            "reason": "No matching content found"
        }
        
        for chunk in context_chunks:
            chunk_text = chunk.get("text", "")
            
            # Try exact match first
            if claim.lower() in chunk_text.lower():
                return {
                    "is_supported": True,
                    "support_score": 1.0,
                    "source_chunk": chunk.get("chunk_id"),
                    "evidence": claim,
                    "reason": "Exact match found"
                }
            
            # Try fuzzy matching
            similarity = fuzz.partial_ratio(claim.lower(), chunk_text.lower()) / 100.0
            
            if similarity > best_match["support_score"]:
                best_match.update({
                    "is_supported": similarity >= 0.7,
                    "support_score": similarity,
                    "source_chunk": chunk.get("chunk_id"),
                    "evidence": self._find_best_evidence(claim, chunk_text),
                    "reason": f"Fuzzy match with {similarity:.2f} similarity"
                })
                
        return best_match
    
    def _find_best_evidence(self, claim: str, chunk_text: str) -> str:
        """
        Find the best evidence snippet for a claim
        """
        # Split chunk into sentences and find best matching one
        sentences = re.split(r'[.!?]+', chunk_text)
        best_sentence = ""
        best_score = 0.0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:
                score = fuzz.partial_ratio(claim.lower(), sentence.lower()) / 100.0
                if score > best_score:
                    best_score = score
                    best_sentence = sentence
                    
        return best_sentence
    
    def _extract_citations(self, text: str) -> List[Dict]:
        """
        Extract citations from response text
        """
        citations = []
        
        # Look for citation patterns
        patterns = [
            r'\[Source: ([^\]]+)\]',
            r'\[Section ([^\]]+)\]',
            r'\[Page (\d+)\]',
            r'\[([^\]]+)\]'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                citations.append({
                    "type": "citation",
                    "text": match,
                    "full_citation": f"[Source: {match}]"
                })
                
        return citations
    
    def _generate_recommendations(self, validation_result: Dict) -> List[str]:
        """
        Generate recommendations based on validation results
        """
        recommendations = []
        
        if not validation_result["is_grounded"]:
            recommendations.append("Response contains unsupported claims - verify against source documents")
            
        if len(validation_result["unsupported_claims"]) > 0:
            recommendations.append(f"Remove or revise {len(validation_result['unsupported_claims'])} unsupported claims")
            
        if len(validation_result["citations_found"]) == 0:
            recommendations.append("Add source citations to improve grounding")
            
        if validation_result["grounding_score"] < 0.5:
            recommendations.append("Major grounding issues detected - review entire response")
        elif validation_result["grounding_score"] < 0.8:
            recommendations.append("Minor grounding issues - add more source references")
            
        return recommendations
    
    def validate_checklist_item(self, item: Dict, context_chunks: List[Dict]) -> Dict:
        """
        Validate a single checklist item against context
        """
        item_text = item.get("item", "")
        source_quote = item.get("source_quote", "")
        chunk_id = item.get("chunk_id", "")
        
        validation = {
            "item_id": item.get("id", chunk_id),
            "is_valid": True,
            "issues": [],
            "grounding_score": 0.0
        }
        
        # Check if source quote exists in context
        quote_found = False
        for chunk in context_chunks:
            if chunk.get("chunk_id") == chunk_id:
                chunk_text = chunk.get("text", "")
                if source_quote.lower() in chunk_text.lower():
                    quote_found = True
                    validation["grounding_score"] = 1.0
                    break
                else:
                    # Try fuzzy matching
                    similarity = fuzz.partial_ratio(source_quote.lower(), chunk_text.lower()) / 100.0
                    validation["grounding_score"] = similarity
                    if similarity >= 0.8:
                        quote_found = True
                    break
        
        if not quote_found:
            validation["is_valid"] = False
            validation["issues"].append("Source quote not found in context")
            
        # Check if item text is supported by source quote
        if source_quote and item_text:
            similarity = fuzz.partial_ratio(item_text.lower(), source_quote.lower()) / 100.0
            if similarity < 0.7:
                validation["is_valid"] = False
                validation["issues"].append("Item text not sufficiently supported by source quote")
                
        return validation
