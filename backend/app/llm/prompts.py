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
    """Build a comprehensive prompt with context sources."""
    if not sources:
        return f"USER QUESTION: {query}\n\nAnswer: I don't have any relevant information to answer this question."
    
    context_lines = []
    for i, source in enumerate(sources, start=1):
        # Build source description
        source_desc = f"[{i}] "
        
        # Add file information
        file_name = source.get('file_name', 'Unknown')
        file_type = source.get('file_type', 'unknown')
        source_desc += f"{file_name} ({file_type})"
        
        # Add location information
        if file_type == 'pdf' and source.get('page_number'):
            source_desc += f" - Page {source['page_number']}"
        elif file_type == 'audio' and source.get('timestamp'):
            source_desc += f" - {source['timestamp']}"
        elif file_type == 'image':
            source_desc += " - Image"
        
        # Add content snippet
        content = source.get('content', '').strip()
        if content:
            # Truncate very long content
            if len(content) > 500:
                content = content[:500] + "..."
            source_desc += f": {content}"
        
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
    """Build prompt optimized for multimodal content."""
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
    
    if text_sources:
        prompt_parts.append("TEXT SOURCES:")
        for i, source in enumerate(text_sources, start=1):
            content = source.get('content', '').strip()
            file_name = source.get('file_name', 'Unknown')
            prompt_parts.append(f"[{i}] {file_name}: {content}")
    
    if image_sources:
        prompt_parts.append("\nIMAGE SOURCES:")
        for i, source in enumerate(image_sources, start=len(text_sources) + 1):
            content = source.get('content', '').strip()
            file_name = source.get('file_name', 'Unknown')
            prompt_parts.append(f"[{i}] {file_name}: {content}")
    
    if audio_sources:
        prompt_parts.append("\nAUDIO SOURCES:")
        for i, source in enumerate(audio_sources, start=len(text_sources) + len(image_sources) + 1):
            content = source.get('content', '').strip()
            file_name = source.get('file_name', 'Unknown')
            timestamp = source.get('timestamp', '')
            if timestamp:
                prompt_parts.append(f"[{i}] {file_name} ({timestamp}): {content}")
            else:
                prompt_parts.append(f"[{i}] {file_name}: {content}")
    
    context = "\n".join(prompt_parts)
    
    return f"""You are an AI assistant analyzing multimodal content. Use the sources below to answer the question.

{context}

Question: {query}

Answer based on the provided sources. Use [1], [2], etc. for citations. If information is missing, say so."""
