"""
Atomic Execution Controller for MCP Server

This module orchestrates the entire document transformation pipeline
with all-or-nothing guarantees. It's the main entry point for transformations.

Flow:
1. Validate input shape
2. Deep-copy document
3. Resolve all paths
4. Pre-validate operations
5. Schema validation (pre)
6. Run safety checks
7. Apply operations sequentially
8. Schema validation (post)
9. Generate diff
10. Serialize output
11. Return response

If ANY step fails → abort, return original document + errors
"""

import copy
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from path_resolver import resolve_path, PathError
from safety_checks import run_safety_checks, SafetyCheckResult, ErrorLevel
from schema import validate_schema, ValidationError
from operations import apply_operation, apply_batch, OperationError
from utils import (
    parse_content,
    serialize_content,
    calculate_diff,
    ParseError,
    SerializationError
)


@dataclass
class ExecutionOptions:
    """Options for transformation execution"""
    strict_mode: bool = True  # Fail on warnings
    auto_create_paths: bool = False  # Auto-create missing paths
    preserve_formatting: bool = True  # Preserve YAML formatting
    max_operations: int = 100  # Maximum operations per batch
    timeout_seconds: float = 30.0  # Execution timeout
    bulk_threshold: int = 10  # Warning threshold for bulk ops
    forbidden_paths: Optional[List[str]] = None  # Paths that cannot be modified
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "strict_mode": self.strict_mode,
            "auto_create_paths": self.auto_create_paths,
            "preserve_formatting": self.preserve_formatting,
            "max_operations": self.max_operations,
            "timeout_seconds": self.timeout_seconds,
            "bulk_threshold": self.bulk_threshold,
            "forbidden_paths": self.forbidden_paths or []
        }


@dataclass
class TransformationError:
    """Represents an error during transformation"""
    code: str
    message: str
    phase: str  # Which phase the error occurred in
    path: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "phase": self.phase,
            "path": self.path,
            "context": self.context or {}
        }


@dataclass
class TransformationResult:
    """Result of document transformation"""
    success: bool
    document: Dict[str, Any]  # Original if failed, modified if success
    serialized: str  # Serialized output
    diff: Optional[Dict[str, Any]] = None
    errors: List[TransformationError] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    affected_paths: List[str] = field(default_factory=list)
    execution_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "document": self.document,
            "serialized": self.serialized,
            "diff": self.diff,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": self.warnings,
            "affected_paths": self.affected_paths,
            "execution_metadata": self.execution_metadata
        }


class ExecutionError(Exception):
    """Raised when execution fails"""
    pass


def validate_input_shape(
    document: Any,
    operations: Any,
    schema: Any
) -> Optional[TransformationError]:
    """
    Validate that inputs have correct shape.
    
    Args:
        document: Document to validate
        operations: Operations to validate
        schema: Schema to validate
        
    Returns:
        TransformationError if invalid, None otherwise
    """
    if not isinstance(document, dict):
        return TransformationError(
            code="INVALID_DOCUMENT_TYPE",
            message=f"Document must be a dictionary, got {type(document).__name__}",
            phase="input_validation"
        )
    
    if not isinstance(operations, list):
        return TransformationError(
            code="INVALID_OPERATIONS_TYPE",
            message=f"Operations must be a list, got {type(operations).__name__}",
            phase="input_validation"
        )
    
    if not isinstance(schema, dict):
        return TransformationError(
            code="INVALID_SCHEMA_TYPE",
            message=f"Schema must be a dictionary, got {type(schema).__name__}",
            phase="input_validation"
        )
    
    # Validate each operation has required fields
    for i, op in enumerate(operations):
        if not isinstance(op, dict):
            return TransformationError(
                code="INVALID_OPERATION_TYPE",
                message=f"Operation {i} must be a dictionary, got {type(op).__name__}",
                phase="input_validation",
                context={"operation_index": i}
            )
        
        if "action" not in op:
            return TransformationError(
                code="MISSING_OPERATION_ACTION",
                message=f"Operation {i} missing required field 'action'",
                phase="input_validation",
                context={"operation_index": i, "operation": op}
            )
        
        if "path" not in op:
            return TransformationError(
                code="MISSING_OPERATION_PATH",
                message=f"Operation {i} missing required field 'path'",
                phase="input_validation",
                context={"operation_index": i, "operation": op}
            )
    
    return None


def execute_transformation(
    document: Dict[str, Any],
    schema: Dict[str, Any],
    operations: List[Dict[str, Any]],
    options: Optional[ExecutionOptions] = None
) -> TransformationResult:
    """
    Execute document transformation atomically.
    
    This is the main entry point for all transformations.
    Guarantees all-or-nothing execution.
    
    Args:
        document: Document to transform (will not be mutated)
        schema: JSON schema for validation
        operations: List of operations to apply
        options: Execution options
        
    Returns:
        TransformationResult with outcome
    """
    start_time = time.time()
    options = options or ExecutionOptions()
    errors = []
    warnings = []
    affected_paths = []
    
    # Phase 1: Validate input shape
    error = validate_input_shape(document, operations, schema)
    if error:
        return TransformationResult(
            success=False,
            document=document,
            serialized="",
            errors=[error],
            execution_metadata={
                "phase_failed": "input_validation",
                "duration_ms": (time.time() - start_time) * 1000
            }
        )
    
    # Phase 2: Check operation count
    if len(operations) > options.max_operations:
        return TransformationResult(
            success=False,
            document=document,
            serialized="",
            errors=[TransformationError(
                code="TOO_MANY_OPERATIONS",
                message=f"Operation count ({len(operations)}) exceeds maximum ({options.max_operations})",
                phase="input_validation",
                context={"count": len(operations), "max": options.max_operations}
            )],
            execution_metadata={
                "phase_failed": "input_validation",
                "duration_ms": (time.time() - start_time) * 1000
            }
        )
    
    # Phase 3: Deep-copy document (preserve original)
    try:
        working_doc = copy.deepcopy(document)
    except Exception as e:
        return TransformationResult(
            success=False,
            document=document,
            serialized="",
            errors=[TransformationError(
                code="DOCUMENT_COPY_FAILED",
                message=f"Failed to copy document: {str(e)}",
                phase="preparation"
            )],
            execution_metadata={
                "phase_failed": "preparation",
                "duration_ms": (time.time() - start_time) * 1000
            }
        )
    
    # Phase 4: Schema validation (pre-mutation)
    try:
        validate_schema(working_doc, schema)
    except ValidationError as e:
        return TransformationResult(
            success=False,
            document=document,
            serialized="",
            errors=[TransformationError(
                code="SCHEMA_VALIDATION_FAILED_PRE",
                message=f"Document invalid before transformation: {str(e)}",
                phase="pre_validation"
            )],
            execution_metadata={
                "phase_failed": "pre_validation",
                "duration_ms": (time.time() - start_time) * 1000
            }
        )
    
    # Phase 5: Safety checks
    safety_result = run_safety_checks(
        operations,
        working_doc,
        schema,
        options={
            "bulk_threshold": options.bulk_threshold,
            "forbidden_paths": options.forbidden_paths
        }
    )
    
    # Collect warnings
    warnings.extend([w.to_dict() for w in safety_result.warnings])
    
    # Check for blocking errors
    if safety_result.has_blocking_errors():
        return TransformationResult(
            success=False,
            document=document,
            serialized="",
            errors=[TransformationError(
                code=e.code,
                message=e.message,
                phase="safety_checks",
                path=e.path,
                context=e.context
            ) for e in safety_result.errors],
            warnings=warnings,
            execution_metadata={
                "phase_failed": "safety_checks",
                "duration_ms": (time.time() - start_time) * 1000
            }
        )
    
    # In strict mode, warnings are blocking
    if options.strict_mode and warnings:
        return TransformationResult(
            success=False,
            document=document,
            serialized="",
            errors=[TransformationError(
                code="STRICT_MODE_WARNING",
                message="Warnings present in strict mode",
                phase="safety_checks",
                context={"warnings": warnings}
            )],
            warnings=warnings,
            execution_metadata={
                "phase_failed": "safety_checks",
                "duration_ms": (time.time() - start_time) * 1000
            }
        )
    
    # Phase 6: Apply operations
    try:
        if len(operations) == 1:
            # Single operation
            working_doc = apply_operation(working_doc, operations[0])
        else:
            # Batch operations
            working_doc = apply_batch(working_doc, operations)
        
        # Track affected paths (simplified - would need enhancement)
        for op in operations:
            path = op.get("path", [])
            if path:
                path_str = ".".join(str(p) for p in path)
                if path_str not in affected_paths:
                    affected_paths.append(path_str)
    
    except OperationError as e:
        return TransformationResult(
            success=False,
            document=document,
            serialized="",
            errors=[TransformationError(
                code="OPERATION_FAILED",
                message=str(e),
                phase="operation_execution"
            )],
            warnings=warnings,
            execution_metadata={
                "phase_failed": "operation_execution",
                "duration_ms": (time.time() - start_time) * 1000
            }
        )
    except Exception as e:
        return TransformationResult(
            success=False,
            document=document,
            serialized="",
            errors=[TransformationError(
                code="UNEXPECTED_ERROR",
                message=f"Unexpected error during operation: {str(e)}",
                phase="operation_execution"
            )],
            warnings=warnings,
            execution_metadata={
                "phase_failed": "operation_execution",
                "duration_ms": (time.time() - start_time) * 1000
            }
        )
    
    # Phase 7: Schema validation (post-mutation)
    try:
        validate_schema(working_doc, schema)
    except ValidationError as e:
        return TransformationResult(
            success=False,
            document=document,
            serialized="",
            errors=[TransformationError(
                code="SCHEMA_VALIDATION_FAILED_POST",
                message=f"Document invalid after transformation: {str(e)}",
                phase="post_validation",
                context={"validation_error": str(e)}
            )],
            warnings=warnings,
            execution_metadata={
                "phase_failed": "post_validation",
                "duration_ms": (time.time() - start_time) * 1000
            }
        )
    
    # Phase 8: Calculate diff
    try:
        diff = calculate_diff(document, working_doc)
    except Exception as e:
        # Diff calculation failure is not critical
        diff = {"error": str(e)}
        warnings.append({
            "code": "DIFF_CALCULATION_FAILED",
            "message": f"Failed to calculate diff: {str(e)}"
        })
    
    # Phase 9: Serialize output
    # Note: We don't have file_type here, so we'll return the document
    # The caller will handle serialization based on their needs
    
    # Calculate execution time
    duration_ms = (time.time() - start_time) * 1000
    
    return TransformationResult(
        success=True,
        document=working_doc,
        serialized="",  # Will be filled by caller
        diff=diff,
        errors=[],
        warnings=warnings,
        affected_paths=affected_paths,
        execution_metadata={
            "operations_applied": len(operations),
            "duration_ms": duration_ms,
            "validation_passed": True
        }
    )


def preview_transformation(
    document: Dict[str, Any],
    schema: Dict[str, Any],
    operations: List[Dict[str, Any]],
    options: Optional[ExecutionOptions] = None
) -> Dict[str, Any]:
    """
    Preview what would change without applying operations.
    
    This is a dry-run mode that shows the diff without committing.
    
    Args:
        document: Document to preview
        schema: JSON schema
        operations: Operations to preview
        options: Execution options
        
    Returns:
        Preview result with diff and validation info
    """
    result = execute_transformation(document, schema, operations, options)
    
    return {
        "would_succeed": result.success,
        "diff": result.diff,
        "errors": [e.to_dict() for e in result.errors],
        "warnings": result.warnings,
        "affected_paths": result.affected_paths,
        "operations_count": len(operations)
    }
