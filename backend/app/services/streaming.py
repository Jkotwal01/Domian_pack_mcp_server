"""
Streaming Service for Real-Time Progress Updates

Provides Server-Sent Events (SSE) for streaming progress to the frontend.
"""

import asyncio
import json
from typing import Dict, AsyncGenerator, Optional
from collections import defaultdict
from datetime import datetime
from app.models.api_models import ProgressEvent


class StreamingService:
    """
    Manages SSE streams for multiple concurrent operations.
    Thread-safe event queues per session/operation.
    """
    
    def __init__(self):
        self.streams: Dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()
    
    async def create_stream(self, stream_id: str) -> None:
        """
        Create a new event stream.
        
        Args:
            stream_id: Unique identifier for the stream (session_id or operation_id)
        """
        async with self._lock:
            if stream_id not in self.streams:
                self.streams[stream_id] = asyncio.Queue()
    
    async def emit(
        self,
        stream_id: str,
        event_type: str,
        message: str,
        data: Optional[Dict] = None,
        progress_percent: Optional[int] = None
    ) -> None:
        """
        Emit an event to a stream.
        
        Args:
            stream_id: Stream identifier
            event_type: Type of event (status, progress, llm_chunk, validation, diff, complete, error)
            message: Event message
            data: Optional event data
            progress_percent: Optional progress percentage (0-100)
        """
        event = ProgressEvent(
            type=event_type,
            message=message,
            data=data,
            timestamp=datetime.utcnow(),
            progress_percent=progress_percent
        )
        
        async with self._lock:
            if stream_id in self.streams:
                await self.streams[stream_id].put(event)
    
    async def stream_events(self, stream_id: str, timeout: int = 300) -> AsyncGenerator[str, None]:
        """
        SSE event stream generator.
        
        Args:
            stream_id: Stream identifier
            timeout: Timeout in seconds for waiting for events
            
        Yields:
            SSE-formatted event strings
        """
        # Ensure stream exists
        await self.create_stream(stream_id)
        
        queue = self.streams[stream_id]
        start_time = asyncio.get_event_loop().time()
        
        try:
            while True:
                # Check timeout
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > timeout:
                    yield self._format_sse_event(ProgressEvent(
                        type="error",
                        message="Stream timeout",
                        timestamp=datetime.utcnow()
                    ))
                    break
                
                try:
                    # Wait for event with timeout
                    event = await asyncio.wait_for(queue.get(), timeout=5.0)
                    
                    # Format and yield SSE event
                    yield self._format_sse_event(event)
                    
                    # Break on complete or error
                    if event.type in ("complete", "error"):
                        break
                        
                except asyncio.TimeoutError:
                    # Send keepalive ping
                    yield ": keepalive\n\n"
                    continue
                    
        finally:
            # Cleanup stream
            await self.close_stream(stream_id)
    
    async def close_stream(self, stream_id: str) -> None:
        """
        Close and cleanup a stream.
        
        Args:
            stream_id: Stream identifier
        """
        async with self._lock:
            if stream_id in self.streams:
                del self.streams[stream_id]
    
    def _format_sse_event(self, event: ProgressEvent) -> str:
        """
        Format event as SSE message.
        
        Args:
            event: Progress event
            
        Returns:
            SSE-formatted string
        """
        event_dict = event.model_dump()
        # Convert datetime to ISO format string
        event_dict["timestamp"] = event.timestamp.isoformat()
        
        return f"data: {json.dumps(event_dict)}\n\n"
    
    async def emit_status(self, stream_id: str, message: str, progress: Optional[int] = None):
        """Convenience method to emit status event"""
        await self.emit(stream_id, "status", message, progress_percent=progress)
    
    async def emit_validation(self, stream_id: str, message: str, progress: Optional[int] = None):
        """Convenience method to emit validation event"""
        await self.emit(stream_id, "validation", message, progress_percent=progress)
    
    async def emit_llm_chunk(self, stream_id: str, chunk: str, progress: Optional[int] = None):
        """Convenience method to emit LLM chunk event"""
        await self.emit(stream_id, "llm_chunk", chunk, progress_percent=progress)
    
    async def emit_diff(self, stream_id: str, message: str, diff_data: Dict, progress: Optional[int] = None):
        """Convenience method to emit diff event"""
        await self.emit(stream_id, "diff", message, data=diff_data, progress_percent=progress)
    
    async def emit_complete(self, stream_id: str, message: str, result_data: Optional[Dict] = None):
        """Convenience method to emit complete event"""
        await self.emit(stream_id, "complete", message, data=result_data, progress_percent=100)
    
    async def emit_error(self, stream_id: str, message: str, error_data: Optional[Dict] = None):
        """Convenience method to emit error event"""
        await self.emit(stream_id, "error", message, data=error_data)


# Global streaming service instance
streaming_service = StreamingService()
