#!/usr/bin/env python3
"""
Error Handling Utilities for MV Orchestra

Implements production-ready error handling patterns:
- Exponential backoff retry
- Circuit breaker
- Adaptive retry
- Graceful degradation

Based on Phase 1 requirements from design specification v2.0
"""

import time
import functools
from typing import Callable, Any, Optional, Type, Tuple
from enum import Enum
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


def exponential_backoff_retry(
    max_retries: int = 4,
    base_delay: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for exponential backoff retry

    Retry pattern: 2s → 4s → 8s → 16s (default)

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap
        exceptions: Tuple of exceptions to catch and retry

    Example:
        @exponential_backoff_retry(max_retries=4, base_delay=2.0)
        def call_api():
            # Will retry with delays: 2s, 4s, 8s, 16s
            response = requests.get("https://api.example.com")
            return response
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise

                    # Calculate exponential backoff delay
                    delay = min(base_delay * (2 ** attempt), max_delay)

                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}), "
                        f"retrying in {delay:.1f}s: {e}"
                    )

                    time.sleep(delay)

            # Should never reach here, but just in case
            raise last_exception

        return wrapper
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern implementation

    States:
    - CLOSED: Normal operation
    - OPEN: Too many failures, reject requests
    - HALF_OPEN: Testing if service recovered

    Usage:
        breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)

        @breaker
        def call_external_service():
            # Your code here
            pass
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        """
        Initialize circuit breaker

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying again
            expected_exception: Exception type to track
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def __call__(self, func: Callable) -> Callable:
        """Decorator interface"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return self.call(func, *args, **kwargs)
        return wrapper

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            func: Function to execute
            *args, **kwargs: Function arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception(
                    f"Circuit breaker OPEN: too many failures "
                    f"(retry after {self.recovery_timeout}s)"
                )

        try:
            # Execute function
            result = func(*args, **kwargs)

            # Success - reset failure count
            if self.state == CircuitState.HALF_OPEN:
                logger.info(f"Circuit breaker closing (service recovered)")
                self.state = CircuitState.CLOSED

            self.failure_count = 0
            return result

        except self.expected_exception as e:
            # Track failure
            self.failure_count += 1
            self.last_failure_time = time.time()

            logger.warning(
                f"Circuit breaker failure {self.failure_count}/{self.failure_threshold}: {e}"
            )

            # Open circuit if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.error(
                    f"Circuit breaker OPEN after {self.failure_count} failures"
                )

            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True

        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.recovery_timeout

    def reset(self):
        """Manually reset circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        logger.info("Circuit breaker manually reset")


class AdaptiveRetry:
    """
    Adaptive retry with success rate tracking

    Adjusts retry strategy based on recent success/failure rates
    """

    def __init__(self, window_size: int = 10):
        """
        Initialize adaptive retry

        Args:
            window_size: Number of recent attempts to track
        """
        self.window_size = window_size
        self.recent_results = []

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Calculate current success rate
            success_rate = self._get_success_rate()

            # Adjust retry count based on success rate
            if success_rate > 0.8:
                max_retries = 2  # High success, fewer retries
            elif success_rate > 0.5:
                max_retries = 4  # Medium success, normal retries
            else:
                max_retries = 6  # Low success, more retries

            logger.info(
                f"Adaptive retry: success_rate={success_rate:.2f}, "
                f"max_retries={max_retries}"
            )

            # Execute with adaptive retry count
            @exponential_backoff_retry(max_retries=max_retries)
            def execute():
                return func(*args, **kwargs)

            try:
                result = execute()
                self._record_result(True)
                return result
            except Exception as e:
                self._record_result(False)
                raise

        return wrapper

    def _record_result(self, success: bool):
        """Record attempt result"""
        self.recent_results.append(success)
        if len(self.recent_results) > self.window_size:
            self.recent_results.pop(0)

    def _get_success_rate(self) -> float:
        """Calculate recent success rate"""
        if not self.recent_results:
            return 0.5  # Default: neutral

        successes = sum(self.recent_results)
        return successes / len(self.recent_results)


def graceful_degradation(
    fallback_func: Optional[Callable] = None,
    return_value: Any = None
):
    """
    Graceful degradation decorator

    If function fails, use fallback function or return default value

    Args:
        fallback_func: Alternative function to call on failure
        return_value: Default value to return on failure

    Example:
        @graceful_degradation(return_value=[])
        def get_recommendations():
            # If this fails, return empty list instead of crashing
            return api.get_recommendations()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    f"{func.__name__} failed, using graceful degradation: {e}"
                )

                # Try fallback function
                if fallback_func is not None:
                    try:
                        return fallback_func(*args, **kwargs)
                    except Exception as fallback_error:
                        logger.error(
                            f"Fallback also failed: {fallback_error}"
                        )

                # Return default value
                return return_value

        return wrapper
    return decorator


# Example usage and tests
if __name__ == "__main__":
    print("=" * 70)
    print("ERROR HANDLING UTILITIES - EXAMPLES")
    print("=" * 70)

    # Example 1: Exponential backoff
    print("\n1. Exponential Backoff Retry:")

    attempt_count = [0]

    @exponential_backoff_retry(max_retries=3, base_delay=0.5)
    def flaky_function():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise Exception(f"Attempt {attempt_count[0]} failed")
        return "Success!"

    try:
        result = flaky_function()
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Failed: {e}")

    # Example 2: Circuit breaker
    print("\n2. Circuit Breaker:")

    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=2.0)

    @breaker
    def unreliable_service():
        import random
        if random.random() < 0.7:  # 70% failure rate
            raise Exception("Service unavailable")
        return "OK"

    for i in range(10):
        try:
            result = unreliable_service()
            print(f"   Call {i+1}: {result}")
        except Exception as e:
            print(f"   Call {i+1}: Failed - {e}")
        time.sleep(0.1)

    # Example 3: Graceful degradation
    print("\n3. Graceful Degradation:")

    @graceful_degradation(return_value="Default content")
    def get_content():
        raise Exception("API down")

    content = get_content()
    print(f"   Content: {content}")

    print("\n" + "=" * 70)
    print("✓ Error handling utilities ready")
    print("=" * 70)
