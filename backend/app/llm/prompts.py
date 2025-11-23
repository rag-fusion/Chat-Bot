"""
Enhanced prompt templates for better LLM responses.
"""

from __future__ import annotations

from typing import List, Dict, Any


SYSTEM_PROMPT_TEMPLATE = """You are an offline assistant that answers questions using only the provided context. Follow these rules:

1. Use ONLY the information from the provided sources
2. Cite sources inline using [1], [2], etc.
3. If you don't know something, say "I don't know" rather than guessing
4. Be concise but complete in your answers
5. If multiple sources contradict each other, mention this
6. For images, describe what you see based on the provided description
7. For audio, reference the transcript timestamps when available

CONTEXT SOURCES:
{context_sources}

USER QUESTION: {user_query}

Answer:"""


def build_prompt(query: str, sources: List[Dict[str, Any]]) -> str:
    """Build a comprehensive prompt with context sources, optimized for multimodal content."""
    if not sources:
        return f"USER QUESTION: {query}\n\nAnswer: I don't have any relevant information to answer this question."
    
    context_lines = []
    for i, source in enumerate(sources, start=1):
        # Build source description
        source_desc = f"[{i}] "
        
        # Add file information and modality indicator
        file_name = source.get('file_name', 'Unknown')
        file_type = source.get('file_type', 'unknown')
        modality = source.get('modality', file_type)
        
        source_desc += f"{file_name}"
        
        # Add modality hint for better LLM context
        if file_type == 'image':
            source_desc += " (Screenshot/Image)"
        elif file_type == 'pdf':
            source_desc += " (PDF Document)"
        elif file_type == 'audio':
            source_desc += " (Audio)"
        
        # Add location information
        if file_type == 'pdf' and source.get('page_number'):
            source_desc += f" - Page {source['page_number']}"
        elif file_type == 'audio' and source.get('timestamp'):
            source_desc += f" - {source['timestamp']}"
        
        # Add content snippet
        # For images, we want OCR text to be prominent
        content = source.get('content', '').strip()
        if content:
            # Truncate very long content
            if len(content) > 500:
                content = content[:500] + "..."
            source_desc += f": {content}"
        
        # If no content but we have OCR text in metadata, show it
        # (for backward compatibility, also check for ocr_text field)
        ocr_text = source.get('ocr_text', '')
        if ocr_text and not content:
            source_desc += f": (OCR) {ocr_text}"
        
        context_lines.append(source_desc)
    
    context_sources = "\n".join(context_lines)
    
    return SYSTEM_PROMPT_TEMPLATE.format(
        context_sources=context_sources,
        user_query=query
    )


def build_simple_prompt(query: str, sources: List[Dict[str, Any]]) -> str:
    """Build a simpler prompt for basic use cases."""
    if not sources:
        return f"Question: {query}\nAnswer: I don't have information to answer this question."
    
    context_parts = []
    for i, source in enumerate(sources, start=1):
        content = source.get('content', '').strip()
        file_name = source.get('file_name', 'Unknown')
        context_parts.append(f"Source {i} ({file_name}): {content}")
    
    context = "\n\n".join(context_parts)
    
    return f"""Context:
{context}

Question: {query}

Answer using only the information above. Cite sources with [1], [2], etc. If you don't know, say so."""


def build_multimodal_prompt(query: str, sources: List[Dict[str, Any]]) -> str:
    """Build prompt optimized for multimodal content with proper image handling."""
    if not sources:
        return f"Question: {query}\nAnswer: I don't have any relevant information."
    
    # Group sources by modality
    text_sources = []
    image_sources = []
    audio_sources = []
    
    for source in sources:
        modality = source.get('modality', source.get('file_type', 'text'))
        if modality == 'image':
            image_sources.append(source)
        elif modality == 'audio':
            audio_sources.append(source)
        else:
            text_sources.append(source)
    
    prompt_parts = []
    counter = 1
    
    if text_sources:
        prompt_parts.append("TEXT SOURCES:")
        for source in text_sources:
            content = source.get('content', '').strip()
            file_name = source.get('file_name', 'Unknown')
            if content:
                if len(content) > 300:
                    content = content[:300] + "..."
                prompt_parts.append(f"[{counter}] {file_name}: {content}")
            counter += 1
    
    if image_sources:
        prompt_parts.append("\nIMAGE SOURCES (Screenshots/Diagrams):")
        for source in image_sources:
            # For images, the content field should already contain OCR text (from image_processor.py)
            content = source.get('content', '').strip()
            file_name = source.get('file_name', 'Unknown')
            
            # Fallback to ocr_text field if available and content is just the filename
            ocr_text = source.get('ocr_text', '')
            if not content or content.startswith('Image:'):
                if ocr_text:
                    content = ocr_text
                else:
                    content = "(Image - describe based on filename and any visible elements)"
            
            if len(content) > 300:
                content = content[:300] + "..."
            
            # Make image source more distinct for the LLM
            prompt_parts.append(f"[{counter}] {file_name} (IMAGE): {content}")
            counter += 1
    
    if audio_sources:
        prompt_parts.append("\nAUDIO SOURCES (Transcripts):")
        for source in audio_sources:
            content = source.get('content', '').strip()
            file_name = source.get('file_name', 'Unknown')
            timestamp = source.get('timestamp', '')
            if content:
                if len(content) > 300:
                    content = content[:300] + "..."
                if timestamp:
                    prompt_parts.append(f"[{counter}] {file_name} ({timestamp}): {content}")
                else:
                    prompt_parts.append(f"[{counter}] {file_name}: {content}")
            counter += 1
    
    context = "\n".join(prompt_parts)
    
    return f"""You are an AI assistant analyzing multimodal content. Use the sources below to answer the question.

{context}

Question: {query}

Important Instructions:
1. Use ONLY information from the sources [1] through [{counter-1}]
2. For image sources, describe what they show based on the text/OCR content provided
3. Cite sources inline using [1], [2], [3], etc.
4. If information is not in the sources, say "I don't have that information in the provided sources"
5. Be specific and accurate in your answers

Answer:"""
