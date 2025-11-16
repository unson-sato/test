#!/usr/bin/env python3
"""
Error Handling and Retry Mechanisms

For robust non-interactive Claude Code workflows:
1. Exponential backoff retry
2. Circuit breaker pattern
3. Error recovery strategies
4. Graceful degradation
"""

import time
import random
import logging
from datetime import datetime, timedelta
from typing import Callable, Any, Optional, Dict, List
from dataclasses import dataclass
from enum import Enum
from functools import wraps


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"          # Recoverable, can retry
    MEDIUM = "medium"    # Might recover, should retry with caution
    HIGH = "high"        # Difficult to recover, limited retries
    CRITICAL = "critical"  # Cannot recover, fail immediately


class ErrorCategory(Enum):
    """Types of errors"""
    NETWORK = "network"           # Network/connection issues
    API_LIMIT = "api_limit"       # Rate limiting, quotas
    VALIDATION = "validation"     # Input validation errors
    TOOL_EXECUTION = "tool_execution"  # Tool execution failures
    TIMEOUT = "timeout"           # Operation timeouts
    UNKNOWN = "unknown"           # Unclassified errors


@dataclass
class ErrorContext:
    """Context information about an error"""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    timestamp: str
    retry_count: int = 0
    metadata: Dict[str, Any] = None


# ============================================================================
# Strategy 1: Exponential Backoff Retry
# ============================================================================

def exponential_backoff_retry(
    max_retries: int = 4,
    base_delay: float = 2.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """
    Decorator for exponential backoff retry

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        jitter: Add random jitter to prevent thundering herd

    Example:
        @exponential_backoff_retry(max_retries=4, base_delay=2.0)
        def call_api():
            # API call that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(f"✓ Success after {attempt} retries")
                    return result

                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"✗ Failed after {max_retries} retries: {e}")
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)

                    # Add jitter (random variation)
                    if jitter:
                        delay = delay * (0.5 + random.random())

                    logger.warning(
                        f"⚠ Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )

                    time.sleep(delay)

        return wrapper
    return decorator


# ============================================================================
# Strategy 2: Circuit Breaker Pattern
# ============================================================================

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures

    Inspired by electrical circuit breakers:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, reject requests immediately
    - HALF_OPEN: After timeout, try one request to test recovery
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            func: Function to execute
            *args, **kwargs: Function arguments

        Returns:
            Function result

        Raises:
            Exception if circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self._should_attempt_reset():
                logger.info("Circuit breaker: Attempting recovery (HALF_OPEN)")
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception(f"Circuit breaker is OPEN. Too many failures.")

        try:
            result = func(*args, **kwargs)

            # Success - reset failure count
            if self.state == CircuitState.HALF_OPEN:
                logger.info("Circuit breaker: Recovery successful (CLOSED)")
                self.state = CircuitState.CLOSED

            self.failure_count = 0
            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            logger.warning(
                f"Circuit breaker: Failure {self.failure_count}/{self.failure_threshold}"
            )

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.error(
                    f"Circuit breaker: OPEN due to {self.failure_count} failures"
                )

            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if self.last_failure_time is None:
            return True

        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

    def reset(self):
        """Manually reset circuit breaker"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        logger.info("Circuit breaker: Manually reset (CLOSED)")


# ============================================================================
# Strategy 3: Error Recovery Strategies
# ============================================================================

class ErrorRecoveryStrategy:
    """
    Strategies for recovering from different types of errors
    """

    @staticmethod
    def classify_error(exception: Exception) -> ErrorContext:
        """
        Classify error and determine recovery strategy

        Args:
            exception: The exception to classify

        Returns:
            ErrorContext with classification
        """
        error_msg = str(exception).lower()

        # Network errors
        if any(keyword in error_msg for keyword in ["connection", "network", "timeout"]):
            return ErrorContext(
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.MEDIUM,
                message=str(exception),
                timestamp=datetime.now().isoformat()
            )

        # API rate limiting
        if any(keyword in error_msg for keyword in ["rate limit", "quota", "429"]):
            return ErrorContext(
                category=ErrorCategory.API_LIMIT,
                severity=ErrorSeverity.HIGH,
                message=str(exception),
                timestamp=datetime.now().isoformat()
            )

        # Validation errors
        if any(keyword in error_msg for keyword in ["validation", "invalid", "schema"]):
            return ErrorContext(
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.CRITICAL,
                message=str(exception),
                timestamp=datetime.now().isoformat()
            )

        # Default: Unknown
        return ErrorContext(
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.MEDIUM,
            message=str(exception),
            timestamp=datetime.now().isoformat()
        )

    @staticmethod
    def get_retry_strategy(error_context: ErrorContext) -> Dict[str, Any]:
        """
        Get retry strategy based on error classification

        Args:
            error_context: Classified error

        Returns:
            Retry configuration
        """
        strategies = {
            ErrorCategory.NETWORK: {
                "should_retry": True,
                "max_retries": 4,
                "base_delay": 2.0,
                "exponential_base": 2.0
            },
            ErrorCategory.API_LIMIT: {
                "should_retry": True,
                "max_retries": 3,
                "base_delay": 60.0,  # Longer delay for rate limits
                "exponential_base": 2.0
            },
            ErrorCategory.VALIDATION: {
                "should_retry": False,  # Validation errors won't fix themselves
                "max_retries": 0,
                "base_delay": 0.0,
                "exponential_base": 1.0
            },
            ErrorCategory.TOOL_EXECUTION: {
                "should_retry": True,
                "max_retries": 2,
                "base_delay": 5.0,
                "exponential_base": 2.0
            },
            ErrorCategory.TIMEOUT: {
                "should_retry": True,
                "max_retries": 3,
                "base_delay": 10.0,
                "exponential_base": 1.5
            },
            ErrorCategory.UNKNOWN: {
                "should_retry": True,
                "max_retries": 2,
                "base_delay": 5.0,
                "exponential_base": 2.0
            }
        }

        return strategies.get(error_context.category, strategies[ErrorCategory.UNKNOWN])


# ============================================================================
# Strategy 4: Adaptive Retry with Error Classification
# ============================================================================

def adaptive_retry(func: Callable) -> Callable:
    """
    Decorator that adapts retry strategy based on error type

    Example:
        @adaptive_retry
        def call_api():
            # API call
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        attempt = 0

        while True:
            try:
                return func(*args, **kwargs)

            except Exception as e:
                # Classify error
                error_context = ErrorRecoveryStrategy.classify_error(e)
                error_context.retry_count = attempt

                # Get retry strategy
                strategy = ErrorRecoveryStrategy.get_retry_strategy(error_context)

                logger.warning(
                    f"Error ({error_context.category.value}): {error_context.message}"
                )

                # Check if should retry
                if not strategy["should_retry"] or attempt >= strategy["max_retries"]:
                    logger.error(f"Giving up after {attempt} attempts")
                    raise

                # Calculate delay
                delay = min(
                    strategy["base_delay"] * (strategy["exponential_base"] ** attempt),
                    300.0  # Max 5 minutes
                )

                logger.info(f"Retrying in {delay:.2f}s (attempt {attempt + 1})")
                time.sleep(delay)

                attempt += 1

    return wrapper


# ============================================================================
# Strategy 5: Graceful Degradation
# ============================================================================

class GracefulDegradation:
    """
    Provide fallback functionality when primary operation fails
    """

    @staticmethod
    def with_fallback(
        primary_func: Callable,
        fallback_func: Callable,
        fallback_condition: Optional[Callable[[Exception], bool]] = None
    ) -> Any:
        """
        Execute primary function, fallback if it fails

        Args:
            primary_func: Primary function to try
            fallback_func: Fallback function if primary fails
            fallback_condition: Optional condition to check if fallback should be used

        Returns:
            Result from primary or fallback function
        """
        try:
            logger.info("Attempting primary operation")
            return primary_func()

        except Exception as e:
            # Check fallback condition
            should_fallback = True
            if fallback_condition:
                should_fallback = fallback_condition(e)

            if should_fallback:
                logger.warning(f"Primary failed: {e}. Using fallback.")
                return fallback_func()
            else:
                logger.error(f"Primary failed and fallback not applicable: {e}")
                raise


# ============================================================================
# Complete Example: Robust Claude API Caller
# ============================================================================

class RobustClaudeAPICaller:
    """
    Example of combining all error handling strategies
    """

    def __init__(self):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60.0
        )

    @adaptive_retry
    def call_with_retry(self, prompt: str) -> Dict[str, Any]:
        """Call API with adaptive retry"""
        # Simulated API call (would be real call in production)
        return self._simulate_api_call(prompt)

    def call_with_circuit_breaker(self, prompt: str) -> Dict[str, Any]:
        """Call API with circuit breaker protection"""
        return self.circuit_breaker.call(self._simulate_api_call, prompt)

    def call_with_fallback(self, prompt: str) -> Dict[str, Any]:
        """Call API with fallback to mock response"""
        return GracefulDegradation.with_fallback(
            primary_func=lambda: self._simulate_api_call(prompt),
            fallback_func=lambda: {"response": "Fallback response (API unavailable)"}
        )

    def _simulate_api_call(self, prompt: str) -> Dict[str, Any]:
        """Simulated API call (for demonstration)"""
        # Randomly fail to demonstrate error handling
        if random.random() < 0.3:  # 30% failure rate
            raise Exception("Simulated network error")

        return {"response": f"Response to: {prompt}"}


# ============================================================================
# Example Usage
# ============================================================================

def main():
    """Demonstrate error handling strategies"""

    print("\n" + "="*70)
    print("ERROR HANDLING DEMONSTRATION")
    print("="*70)

    caller = RobustClaudeAPICaller()

    # Test 1: Adaptive retry
    print("\n1. Adaptive Retry")
    print("-" * 70)
    try:
        result = caller.call_with_retry("Test prompt")
        print(f"✓ Success: {result}")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 2: Circuit breaker
    print("\n2. Circuit Breaker")
    print("-" * 70)
    for i in range(10):
        try:
            result = caller.call_with_circuit_breaker(f"Prompt {i}")
            print(f"  [{i}] ✓ {result}")
        except Exception as e:
            print(f"  [{i}] ✗ {e}")

    # Test 3: Graceful degradation
    print("\n3. Graceful Degradation")
    print("-" * 70)
    result = caller.call_with_fallback("Test prompt")
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
