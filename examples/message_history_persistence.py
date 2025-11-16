#!/usr/bin/env python3
"""
Message History Persistence Strategies

Compares different approaches for storing conversation history:
1. SQLite - Structured, queryable database
2. JSONL - Simple, line-delimited JSON
3. Hybrid - Best of both worlds

For non-interactive Claude Code workflows
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict


@dataclass
class Message:
    """
    A single message in the conversation
    """
    session_id: str
    iteration: int
    role: str  # "user" or "assistant"
    content: Any  # Can be string or structured content
    timestamp: str
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        if data['metadata'] is None:
            data['metadata'] = {}
        return data


class MessageStore(ABC):
    """
    Abstract base class for message storage
    """

    @abstractmethod
    def save_message(self, message: Message):
        """Save a message"""
        pass

    @abstractmethod
    def get_messages(self, session_id: str, iteration: Optional[int] = None) -> List[Message]:
        """Retrieve messages"""
        pass

    @abstractmethod
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        pass

    @abstractmethod
    def close(self):
        """Close/cleanup resources"""
        pass


# ============================================================================
# Strategy 1: SQLite Database
# ============================================================================

class SQLiteMessageStore(MessageStore):
    """
    Store messages in SQLite database

    Advantages:
    - Structured queries
    - Efficient for large datasets
    - ACID guarantees
    - Can index for fast lookups

    Disadvantages:
    - More complex setup
    - Binary format (not human-readable)
    - Needs schema migrations
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                iteration INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,  -- JSON string
                timestamp TEXT NOT NULL,
                metadata TEXT,  -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indices for common queries
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_iteration
            ON messages(session_id, iteration)
        """)

        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_timestamp
            ON messages(session_id, timestamp)
        """)

        self.conn.commit()

    def save_message(self, message: Message):
        """Save a message to database"""
        self.conn.execute("""
            INSERT INTO messages (session_id, iteration, role, content, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            message.session_id,
            message.iteration,
            message.role,
            json.dumps(message.content),
            message.timestamp,
            json.dumps(message.metadata) if message.metadata else None
        ))
        self.conn.commit()

    def get_messages(self, session_id: str, iteration: Optional[int] = None) -> List[Message]:
        """Retrieve messages from database"""
        if iteration is not None:
            cursor = self.conn.execute("""
                SELECT * FROM messages
                WHERE session_id = ? AND iteration = ?
                ORDER BY id
            """, (session_id, iteration))
        else:
            cursor = self.conn.execute("""
                SELECT * FROM messages
                WHERE session_id = ?
                ORDER BY iteration, id
            """, (session_id,))

        messages = []
        for row in cursor:
            messages.append(Message(
                session_id=row['session_id'],
                iteration=row['iteration'],
                role=row['role'],
                content=json.loads(row['content']),
                timestamp=row['timestamp'],
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            ))

        return messages

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        cursor = self.conn.execute("""
            SELECT
                COUNT(*) as total_messages,
                MAX(iteration) as max_iteration,
                MIN(timestamp) as first_message,
                MAX(timestamp) as last_message
            FROM messages
            WHERE session_id = ?
        """, (session_id,))

        row = cursor.fetchone()

        return {
            "total_messages": row['total_messages'],
            "max_iteration": row['max_iteration'] or 0,
            "first_message": row['first_message'],
            "last_message": row['last_message']
        }

    def query_by_role_count(self, session_id: str) -> Dict[str, int]:
        """Count messages by role"""
        cursor = self.conn.execute("""
            SELECT role, COUNT(*) as count
            FROM messages
            WHERE session_id = ?
            GROUP BY role
        """, (session_id,))

        return {row['role']: row['count'] for row in cursor}

    def close(self):
        """Close database connection"""
        self.conn.close()


# ============================================================================
# Strategy 2: JSONL (JSON Lines)
# ============================================================================

class JSONLMessageStore(MessageStore):
    """
    Store messages in JSONL (JSON Lines) format

    Advantages:
    - Human-readable
    - Simple append-only writes
    - Easy to stream/process
    - No schema needed
    - Version control friendly

    Disadvantages:
    - Slow for queries (needs full scan)
    - No indexing
    - Large files can be unwieldy
    """

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create file if it doesn't exist
        if not self.file_path.exists():
            self.file_path.touch()

    def save_message(self, message: Message):
        """Append message to JSONL file"""
        with open(self.file_path, 'a') as f:
            f.write(json.dumps(message.to_dict()) + '\n')

    def get_messages(self, session_id: str, iteration: Optional[int] = None) -> List[Message]:
        """Retrieve messages from JSONL file"""
        messages = []

        with open(self.file_path, 'r') as f:
            for line in f:
                if not line.strip():
                    continue

                data = json.loads(line)

                # Filter by session_id and iteration
                if data['session_id'] != session_id:
                    continue

                if iteration is not None and data['iteration'] != iteration:
                    continue

                messages.append(Message(**data))

        return messages

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        messages = self.get_messages(session_id)

        if not messages:
            return {
                "total_messages": 0,
                "max_iteration": 0,
                "first_message": None,
                "last_message": None
            }

        return {
            "total_messages": len(messages),
            "max_iteration": max(m.iteration for m in messages),
            "first_message": min(m.timestamp for m in messages),
            "last_message": max(m.timestamp for m in messages)
        }

    def close(self):
        """No cleanup needed for JSONL"""
        pass


# ============================================================================
# Strategy 3: Hybrid (SQLite + JSONL)
# ============================================================================

class HybridMessageStore(MessageStore):
    """
    Hybrid approach: Use both SQLite and JSONL

    - SQLite for fast queries and statistics
    - JSONL for human-readable backup and archival

    Best of both worlds!
    """

    def __init__(self, db_path: str, jsonl_path: str):
        self.sqlite_store = SQLiteMessageStore(db_path)
        self.jsonl_store = JSONLMessageStore(jsonl_path)

    def save_message(self, message: Message):
        """Save to both stores"""
        self.sqlite_store.save_message(message)
        self.jsonl_store.save_message(message)

    def get_messages(self, session_id: str, iteration: Optional[int] = None) -> List[Message]:
        """Retrieve from SQLite (faster)"""
        return self.sqlite_store.get_messages(session_id, iteration)

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get stats from SQLite (faster)"""
        return self.sqlite_store.get_session_stats(session_id)

    def close(self):
        """Close both stores"""
        self.sqlite_store.close()
        self.jsonl_store.close()


# ============================================================================
# Comparison Benchmark
# ============================================================================

def benchmark_stores():
    """
    Compare performance of different storage strategies
    """
    import time

    print("\n" + "="*70)
    print("MESSAGE STORAGE BENCHMARK")
    print("="*70)

    session_id = "test_session"
    num_messages = 1000

    # Generate test messages
    test_messages = []
    for i in range(num_messages):
        msg = Message(
            session_id=session_id,
            iteration=i // 2,  # 2 messages per iteration
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}",
            timestamp=datetime.now().isoformat(),
            metadata={"index": i}
        )
        test_messages.append(msg)

    # Test SQLite
    print("\n1. SQLite Database")
    print("-" * 70)
    sqlite_store = SQLiteMessageStore("/tmp/test_messages.db")

    start = time.time()
    for msg in test_messages:
        sqlite_store.save_message(msg)
    write_time = time.time() - start
    print(f"Write {num_messages} messages: {write_time:.3f}s")

    start = time.time()
    messages = sqlite_store.get_messages(session_id)
    read_time = time.time() - start
    print(f"Read {len(messages)} messages: {read_time:.3f}s")

    start = time.time()
    stats = sqlite_store.get_session_stats(session_id)
    query_time = time.time() - start
    print(f"Query stats: {query_time:.3f}s")
    print(f"Stats: {stats}")

    sqlite_store.close()

    # Test JSONL
    print("\n2. JSONL File")
    print("-" * 70)
    jsonl_store = JSONLMessageStore("/tmp/test_messages.jsonl")

    start = time.time()
    for msg in test_messages:
        jsonl_store.save_message(msg)
    write_time = time.time() - start
    print(f"Write {num_messages} messages: {write_time:.3f}s")

    start = time.time()
    messages = jsonl_store.get_messages(session_id)
    read_time = time.time() - start
    print(f"Read {len(messages)} messages: {read_time:.3f}s")

    start = time.time()
    stats = jsonl_store.get_session_stats(session_id)
    query_time = time.time() - start
    print(f"Query stats: {query_time:.3f}s")
    print(f"Stats: {stats}")

    jsonl_store.close()

    # Test Hybrid
    print("\n3. Hybrid (SQLite + JSONL)")
    print("-" * 70)
    hybrid_store = HybridMessageStore("/tmp/test_hybrid.db", "/tmp/test_hybrid.jsonl")

    start = time.time()
    for msg in test_messages:
        hybrid_store.save_message(msg)
    write_time = time.time() - start
    print(f"Write {num_messages} messages: {write_time:.3f}s")

    start = time.time()
    messages = hybrid_store.get_messages(session_id)
    read_time = time.time() - start
    print(f"Read {len(messages)} messages: {read_time:.3f}s")

    start = time.time()
    stats = hybrid_store.get_session_stats(session_id)
    query_time = time.time() - start
    print(f"Query stats: {query_time:.3f}s")
    print(f"Stats: {stats}")

    hybrid_store.close()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("SQLite: Fast queries, structured, good for large datasets")
    print("JSONL: Simple, human-readable, version control friendly")
    print("Hybrid: Best of both, recommended for production")


# ============================================================================
# Example Usage
# ============================================================================

def example_usage():
    """
    Example of using message stores in a workflow
    """
    print("\n" + "="*70)
    print("EXAMPLE: Using Message Stores")
    print("="*70)

    # Choose a store (Hybrid recommended)
    store = HybridMessageStore(
        db_path="./workspace/messages.db",
        jsonl_path="./workspace/messages.jsonl"
    )

    session_id = "example_session"

    # Simulate a conversation
    for iteration in range(3):
        # User message
        user_msg = Message(
            session_id=session_id,
            iteration=iteration,
            role="user",
            content=f"User prompt for iteration {iteration}",
            timestamp=datetime.now().isoformat()
        )
        store.save_message(user_msg)

        # Assistant message
        assistant_msg = Message(
            session_id=session_id,
            iteration=iteration,
            role="assistant",
            content=[
                {"type": "text", "text": f"Response for iteration {iteration}"},
                {"type": "tool_use", "id": f"tool_{iteration}", "name": "example_tool"}
            ],
            timestamp=datetime.now().isoformat()
        )
        store.save_message(assistant_msg)

    # Retrieve messages
    print("\nAll messages:")
    messages = store.get_messages(session_id)
    for msg in messages:
        print(f"  [{msg.iteration}] {msg.role}: {msg.content}")

    # Get stats
    print("\nSession stats:")
    stats = store.get_session_stats(session_id)
    for key, value in stats.items():
        print(f"  {key}: {value}")

    store.close()


if __name__ == "__main__":
    example_usage()
    print("\n")
    benchmark_stores()
