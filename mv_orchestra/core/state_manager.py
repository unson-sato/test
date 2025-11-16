#!/usr/bin/env python3
"""
State Manager for MV Orchestra

Hybrid SQLite + JSONL approach for state persistence:
- SQLite: Structured data, fast queries
- JSONL: Full conversation history, append-only log

Based on Phase 1 requirements from design specification v2.0
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib


class StateManager:
    """
    Hybrid state persistence manager

    Features:
    - SQLite for structured metadata
    - JSONL for complete conversation log
    - Resumable workflows
    - State checkpointing
    """

    def __init__(self, workspace_dir: str):
        """
        Initialize state manager

        Args:
            workspace_dir: Directory for state files
        """
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)

        # Database and log paths
        self.db_path = self.workspace / "state.db"
        self.log_path = self.workspace / "conversation.jsonl"

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                audio_path TEXT NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL,
                status TEXT NOT NULL,
                current_phase TEXT,
                accumulated_cost REAL DEFAULT 0.0,
                iteration_count INTEGER DEFAULT 0,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Checkpoints table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                phase TEXT NOT NULL,
                timestamp REAL NOT NULL,
                state_data TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # Messages table (for quick queries)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                iteration INTEGER NOT NULL,
                role TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                timestamp REAL NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        conn.commit()
        conn.close()

    def create_session(
        self,
        audio_path: str,
        session_id: Optional[str] = None
    ) -> str:
        """
        Create new session

        Args:
            audio_path: Path to audio file
            session_id: Optional custom session ID

        Returns:
            Session ID
        """
        if session_id is None:
            # Generate session ID from audio path and timestamp
            timestamp = datetime.now().isoformat()
            session_id = hashlib.md5(
                f"{audio_path}_{timestamp}".encode()
            ).hexdigest()[:16]

        now = datetime.now().isoformat()
        start_time = datetime.now().timestamp()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sessions (
                session_id, audio_path, start_time, status,
                current_phase, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, audio_path, start_time, "RUNNING",
            "INIT", now, now
        ))

        conn.commit()
        conn.close()

        return session_id

    def update_session(
        self,
        session_id: str,
        status: Optional[str] = None,
        current_phase: Optional[str] = None,
        accumulated_cost: Optional[float] = None,
        iteration_count: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """
        Update session metadata

        Args:
            session_id: Session identifier
            status: Session status (RUNNING, COMPLETED, FAILED)
            current_phase: Current phase name
            accumulated_cost: Total cost so far
            iteration_count: Number of iterations
            error_message: Error message if failed
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        values = []

        if status is not None:
            updates.append("status = ?")
            values.append(status)

        if current_phase is not None:
            updates.append("current_phase = ?")
            values.append(current_phase)

        if accumulated_cost is not None:
            updates.append("accumulated_cost = ?")
            values.append(accumulated_cost)

        if iteration_count is not None:
            updates.append("iteration_count = ?")
            values.append(iteration_count)

        if error_message is not None:
            updates.append("error_message = ?")
            values.append(error_message)

        # Always update timestamp
        updates.append("updated_at = ?")
        values.append(datetime.now().isoformat())

        # Add session_id for WHERE clause
        values.append(session_id)

        cursor.execute(f"""
            UPDATE sessions
            SET {', '.join(updates)}
            WHERE session_id = ?
        """, values)

        conn.commit()
        conn.close()

    def save_checkpoint(
        self,
        session_id: str,
        phase: str,
        state_data: Dict[str, Any]
    ):
        """
        Save state checkpoint

        Args:
            session_id: Session identifier
            phase: Current phase name
            state_data: State dictionary to save
        """
        timestamp = datetime.now().timestamp()
        state_json = json.dumps(state_data)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO checkpoints (session_id, phase, timestamp, state_data)
            VALUES (?, ?, ?, ?)
        """, (session_id, phase, timestamp, state_json))

        conn.commit()
        conn.close()

    def load_checkpoint(
        self,
        session_id: str,
        phase: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Load latest checkpoint

        Args:
            session_id: Session identifier
            phase: Optional specific phase to load

        Returns:
            State dictionary or None if no checkpoint
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if phase:
            cursor.execute("""
                SELECT state_data FROM checkpoints
                WHERE session_id = ? AND phase = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (session_id, phase))
        else:
            cursor.execute("""
                SELECT state_data FROM checkpoints
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (session_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        return None

    def log_message(
        self,
        session_id: str,
        iteration: int,
        role: str,
        content: Any
    ):
        """
        Log message to JSONL and database

        Args:
            session_id: Session identifier
            iteration: Iteration number
            role: Message role (user/assistant/system)
            content: Message content
        """
        timestamp = datetime.now().timestamp()

        # Create message entry
        message = {
            'session_id': session_id,
            'iteration': iteration,
            'role': role,
            'content': content,
            'timestamp': timestamp
        }

        # Append to JSONL log
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(message) + '\n')

        # Calculate content hash
        content_str = json.dumps(content, sort_keys=True)
        content_hash = hashlib.md5(content_str.encode()).hexdigest()

        # Store in database for quick queries
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages (
                session_id, iteration, role, content_hash, timestamp
            ) VALUES (?, ?, ?, ?, ?)
        """, (session_id, iteration, role, content_hash, timestamp))

        conn.commit()
        conn.close()

    def load_conversation(
        self,
        session_id: str,
        from_iteration: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Load conversation history from JSONL

        Args:
            session_id: Session identifier
            from_iteration: Optional start iteration

        Returns:
            List of message dictionaries
        """
        messages = []

        if not self.log_path.exists():
            return messages

        with open(self.log_path, 'r') as f:
            for line in f:
                msg = json.loads(line.strip())

                if msg['session_id'] != session_id:
                    continue

                if from_iteration and msg['iteration'] < from_iteration:
                    continue

                messages.append(msg)

        return messages

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session metadata

        Args:
            session_id: Session identifier

        Returns:
            Session info dictionary or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM sessions WHERE session_id = ?
        """, (session_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def list_sessions(
        self,
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        List recent sessions

        Args:
            status: Optional filter by status
            limit: Maximum number of sessions

        Returns:
            List of session dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if status:
            cursor.execute("""
                SELECT * FROM sessions
                WHERE status = ?
                ORDER BY start_time DESC
                LIMIT ?
            """, (status, limit))
        else:
            cursor.execute("""
                SELECT * FROM sessions
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def resume_session(self, session_id: str) -> Dict[str, Any]:
        """
        Resume interrupted session

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with session info and latest state
        """
        # Get session info
        session_info = self.get_session_info(session_id)
        if not session_info:
            raise ValueError(f"Session {session_id} not found")

        # Load latest checkpoint
        state = self.load_checkpoint(session_id)

        # Load conversation history
        messages = self.load_conversation(session_id)

        return {
            'session_info': session_info,
            'state': state,
            'messages': messages
        }


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("STATE MANAGER - EXAMPLE")
    print("=" * 70)

    # Initialize state manager
    manager = StateManager("./test_state")

    # Create session
    session_id = manager.create_session("test_audio.mp3")
    print(f"\n✓ Session created: {session_id}")

    # Update session
    manager.update_session(
        session_id,
        status="RUNNING",
        current_phase="ANALYZING",
        accumulated_cost=0.0,
        iteration_count=1
    )
    print(f"✓ Session updated")

    # Save checkpoint
    manager.save_checkpoint(
        session_id,
        "ANALYZING",
        {
            'phase': 'ANALYZING',
            'progress': 0.5,
            'data': {'tempo': 120, 'key': 'C'}
        }
    )
    print(f"✓ Checkpoint saved")

    # Log messages
    manager.log_message(session_id, 1, "user", "Analyze audio")
    manager.log_message(session_id, 1, "assistant", "Analysis complete")
    print(f"✓ Messages logged")

    # Load checkpoint
    state = manager.load_checkpoint(session_id)
    print(f"✓ Checkpoint loaded: {state}")

    # List sessions
    sessions = manager.list_sessions()
    print(f"\n✓ Recent sessions: {len(sessions)}")
    for s in sessions:
        print(f"  - {s['session_id']}: {s['status']} ({s['current_phase']})")

    print("\n" + "=" * 70)
    print("✓ State manager ready")
    print("=" * 70)
