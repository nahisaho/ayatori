"""Custom exception classes and error handlers."""

from typing import Any, Optional


class GraphRAGMCPError(Exception):
    """Base exception for GraphRAG MCP Server."""

    def __init__(
        self,
        message: str,
        code: str = "GRAPHRAG_ERROR",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize exception.

        Args:
            message: Error message
            code: Error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def to_mcp_error(self) -> dict[str, Any]:
        """Convert to MCP error response format.

        Returns:
            Dictionary with MCP error structure.
        """
        return {
            "code": self.code,
            "message": self.message,
            "data": self.details,
        }


class IndexNotFoundError(GraphRAGMCPError):
    """Raised when GraphRAG index is not found."""

    def __init__(
        self,
        index_path: str,
        message: Optional[str] = None,
    ) -> None:
        """Initialize exception.

        Args:
            index_path: Path where index was expected
            message: Custom error message
        """
        msg = message or f"GraphRAG index not found at: {index_path}"
        super().__init__(
            message=msg,
            code="INDEX_NOT_FOUND",
            details={
                "index_path": index_path,
                "suggestion": "Run 'graphrag-mcp index <data_path>' to create an index",
            },
        )


class LLMProviderError(GraphRAGMCPError):
    """Raised when LLM provider returns an error."""

    def __init__(
        self,
        provider: str,
        original_error: str,
        retryable: bool = False,
    ) -> None:
        """Initialize exception.

        Args:
            provider: LLM provider name
            original_error: Original error message
            retryable: Whether the operation can be retried
        """
        super().__init__(
            message=f"LLM provider error ({provider}): {original_error}",
            code="LLM_PROVIDER_ERROR",
            details={
                "provider": provider,
                "original_error": original_error,
                "retryable": retryable,
            },
        )
        self.retryable = retryable


class ValidationError(GraphRAGMCPError):
    """Raised when input validation fails."""

    def __init__(
        self,
        field: str,
        message: str,
        expected_type: Optional[str] = None,
    ) -> None:
        """Initialize exception.

        Args:
            field: Field name that failed validation
            message: Validation error message
            expected_type: Expected type description
        """
        super().__init__(
            message=f"Validation error for '{field}': {message}",
            code="VALIDATION_ERROR",
            details={
                "field": field,
                "message": message,
                "expected_type": expected_type,
            },
        )


class TokenBudgetExceededError(GraphRAGMCPError):
    """Raised when token budget is exceeded."""

    def __init__(
        self,
        requested_tokens: int,
        budget_tokens: int,
        truncated: bool = False,
    ) -> None:
        """Initialize exception.

        Args:
            requested_tokens: Number of tokens requested
            budget_tokens: Maximum allowed tokens
            truncated: Whether content was truncated
        """
        super().__init__(
            message=f"Token budget exceeded: {requested_tokens} > {budget_tokens}",
            code="TOKEN_BUDGET_EXCEEDED",
            details={
                "requested_tokens": requested_tokens,
                "budget_tokens": budget_tokens,
                "truncated": truncated,
                "suggestion": "Consider using a more specific query or reducing response size",
            },
        )
        self.truncated = truncated
