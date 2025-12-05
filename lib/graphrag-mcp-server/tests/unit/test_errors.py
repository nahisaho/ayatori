"""Tests for error handling module."""

import pytest

from graphrag_mcp_server.errors import (
    GraphRAGMCPError,
    IndexNotFoundError,
    LLMProviderError,
    TokenBudgetExceededError,
    ValidationError,
)


class TestGraphRAGMCPError:
    """Test base GraphRAGMCPError."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = GraphRAGMCPError("Test error message")

        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.code == "GRAPHRAG_ERROR"
        assert error.details == {}

    def test_error_with_code_and_details(self):
        """Test error with custom code and details."""
        error = GraphRAGMCPError(
            message="Custom error",
            code="CUSTOM_ERROR",
            details={"key": "value"},
        )

        assert error.code == "CUSTOM_ERROR"
        assert error.details == {"key": "value"}

    def test_to_mcp_error(self):
        """Test conversion to MCP error format."""
        error = GraphRAGMCPError(
            message="Test",
            code="TEST_CODE",
            details={"foo": "bar"},
        )

        mcp_error = error.to_mcp_error()

        assert mcp_error["code"] == "TEST_CODE"
        assert mcp_error["message"] == "Test"
        assert mcp_error["data"] == {"foo": "bar"}


class TestIndexNotFoundError:
    """Test IndexNotFoundError."""

    def test_default_message(self):
        """Test default error message."""
        error = IndexNotFoundError("/path/to/index")

        assert "not found" in error.message.lower()
        assert "/path/to/index" in error.message
        assert error.code == "INDEX_NOT_FOUND"

    def test_custom_message(self):
        """Test custom error message."""
        error = IndexNotFoundError("/path", message="Custom not found message")

        assert error.message == "Custom not found message"

    def test_details_contain_suggestion(self):
        """Test that details contain index path and suggestion."""
        error = IndexNotFoundError("/path/to/index")

        assert error.details["index_path"] == "/path/to/index"
        assert "suggestion" in error.details
        assert "graphrag-mcp index" in error.details["suggestion"]


class TestLLMProviderError:
    """Test LLMProviderError."""

    def test_provider_error(self):
        """Test LLM provider error creation."""
        error = LLMProviderError(
            provider="openai",
            original_error="Rate limit exceeded",
            retryable=True,
        )

        assert "openai" in error.message
        assert "Rate limit exceeded" in error.message
        assert error.code == "LLM_PROVIDER_ERROR"
        assert error.retryable is True

    def test_non_retryable_error(self):
        """Test non-retryable LLM error."""
        error = LLMProviderError(
            provider="anthropic",
            original_error="Invalid API key",
            retryable=False,
        )

        assert error.retryable is False
        assert error.details["retryable"] is False


class TestValidationError:
    """Test ValidationError."""

    def test_validation_error(self):
        """Test validation error creation."""
        error = ValidationError(
            field="query",
            message="Query cannot be empty",
            expected_type="non-empty string",
        )

        assert "query" in error.message
        assert error.code == "VALIDATION_ERROR"
        assert error.details["field"] == "query"
        assert error.details["expected_type"] == "non-empty string"

    def test_validation_error_without_expected_type(self):
        """Test validation error without expected type."""
        error = ValidationError(field="limit", message="Must be positive")

        assert error.details["expected_type"] is None


class TestTokenBudgetExceededError:
    """Test TokenBudgetExceededError."""

    def test_token_budget_error(self):
        """Test token budget error creation."""
        error = TokenBudgetExceededError(
            requested_tokens=5000,
            budget_tokens=4000,
            truncated=True,
        )

        assert "5000" in error.message
        assert "4000" in error.message
        assert error.code == "TOKEN_BUDGET_EXCEEDED"
        assert error.truncated is True

    def test_token_budget_details(self):
        """Test token budget error details."""
        error = TokenBudgetExceededError(
            requested_tokens=10000,
            budget_tokens=8000,
        )

        assert error.details["requested_tokens"] == 10000
        assert error.details["budget_tokens"] == 8000
        assert "suggestion" in error.details
