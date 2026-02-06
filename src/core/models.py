"""Pydantic models for data validation."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class VideoMetadata(BaseModel):
    """YouTube video metadata."""
    
    title: Optional[str] = None
    views: Optional[int] = None
    duration: Optional[int] = Field(None, description="Duration in seconds")
    channel: Optional[str] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    chapters: List[Dict[str, Any]] = Field(default_factory=list)


class Thumbnail(BaseModel):
    """YouTube video thumbnail information."""
    
    url: str
    width: Optional[int] = None
    height: Optional[int] = None
    resolution: Optional[str] = None


class VideoSearchResult(BaseModel):
    """YouTube video search result."""
    
    title: str
    video_id: str
    url: str


class QueryRequest(BaseModel):
    """Request model for chain queries."""
    
    query: str = Field(..., description="User query to process")
