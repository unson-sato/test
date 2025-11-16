# MV Orchestra v3.0 - Architecture

システムアーキテクチャ詳細ドキュメント

---

## 目次

1. [システム概要](#システム概要)
2. [アーキテクチャ原則](#アーキテクチャ原則)
3. [コンポーネント設計](#コンポーネント設計)
4. [Phase別詳細](#phase別詳細)
5. [データフロー](#データフロー)
6. [状態管理](#状態管理)
7. [並列処理](#並列処理)
8. [エラーハンドリング](#エラーハンドリング)
9. [拡張性](#拡張性)

---

## システム概要

### アーキテクチャパターン

MV Orchestra v3.0は、以下のアーキテクチャパターンを組み合わせています：

- **パイプライン アーキテクチャ**: Phase 0-9の順次処理
- **マイクロサービス指向**: 各Phaseが独立したモジュール
- **イベントドリブン**: フィードバックループによる反応的処理
- **マルチエージェント**: 複数AIエージェントの協調動作

### 技術スタック

```
┌────────────────────────────────────────┐
│         Application Layer              │
│  (run_orchestrator.py / run_phase5_9.py)
└────────────────────────────────────────┘
           ↓
┌────────────────────────────────────────┐
│         Orchestration Layer            │
│  (OrchestratorAgent, FeedbackLoopMgr)  │
└────────────────────────────────────────┘
           ↓
┌────────────────────────────────────────┐
│         Core Components Layer          │
│  (AgentExecutor, EvaluationAgent, etc) │
└────────────────────────────────────────┘
           ↓
┌────────────────────────────────────────┐
│         External Services Layer        │
│  (Claude CLI, MCP, ffmpeg, Remotion)   │
└────────────────────────────────────────┘
```

---

## アーキテクチャ原則

### 1. 疎結合 (Loose Coupling)

各コンポーネントは独立して動作可能：

```python
# Phase 5だけを実行可能
from phase5 import run_phase5
run_phase5("session_id", mock_mode=True)

# Phase 7だけを実行可能
from phase7 import run_phase7
run_phase7("session_id", mock_mode=True)
```

### 2. 高凝集 (High Cohesion)

各モジュールは単一責任を持つ：

- `AgentExecutor`: エージェント実行のみ
- `EvaluationAgent`: 評価のみ
- `VideoEditor`: 動画編集のみ

### 3. 依存性注入 (Dependency Injection)

```python
# コンポーネントを外部から注入
orchestrator = OrchestratorAgent(
    session_id="test",
    claude_cli="/custom/path/to/claude"  # カスタムCLI
)

feedback_manager = FeedbackLoopManager(
    agent_executor=custom_executor,  # カスタム実装
    evaluation_agent=custom_evaluator
)
```

### 4. 状態の永続化

全ての状態は`SharedState`経由でディスクに保存：

```python
# セッション状態はJSONで永続化
sessions/{session_id}/state.json

# 各Phaseの結果も永続化
sessions/{session_id}/phase{N}/results.json
```

### 5. Mock対応

全てのコンポーネントがMock modeをサポート：

```python
# 実際のMCP呼び出し
generator = MCPClipGenerator(mcp_config=config)
result = await generator.generate_clip(design)

# Mock mode（外部依存なし）
generator = MCPClipGenerator(mcp_config=config)
result = await generator.generate_clip(design, mock_mode=True)
```

---

## コンポーネント設計

### コアコンポーネント階層

```
OrchestratorAgent (Phase 0-9統括)
    ↓
    ├── FeedbackLoopManager (品質改善ループ)
    │       ↓
    │       ├── AgentExecutor (並列実行)
    │       └── EvaluationAgent (評価・選定)
    │
    ├── SharedState / PipelineState (状態管理)
    │
    └── Phase 5-9 Components
            ├── MCPClipGenerator
            ├── CLIPEvaluator
            ├── VideoEditor
            ├── EffectsGenerator
            └── RemotionRenderer
```

### 1. OrchestratorAgent

**責務**: Phase 0-9全体の統括

**主要メソッド**:
```python
async def run_full_pipeline(audio_file: Path) -> Dict[str, Any]:
    """Phase 0-9完全実行"""

async def run_design_phases(start_phase: int, end_phase: int) -> Dict[str, Any]:
    """Phase 1-4設計フェーズ実行"""

async def _run_design_phase(phase_num: int) -> Dict[str, Any]:
    """単一設計フェーズ実行（フィードバックループ付き）"""
```

**設計ポイント**:
- 各PhaseはFeedbackLoopManager経由で実行
- 前Phaseの結果から文脈を構築
- 状態はSharedState経由で永続化

### 2. AgentExecutor

**責務**: ディレクターエージェントの並列実行

**主要メソッド**:
```python
async def run_all_directors_parallel(
    phase_num: int,
    context: Dict[str, Any],
    output_dir: Path
) -> List[AgentResult]:
    """5ディレクター並列実行"""

async def run_director_async(
    director_type: str,
    phase_num: int,
    context: Dict[str, Any],
    output_dir: Path
) -> Dict[str, Any]:
    """単一ディレクター実行"""
```

**並列処理フロー**:
```
Context準備
    ↓
5 Directors × asyncio.gather()
    ├─ Corporate ──→ Claude CLI
    ├─ Freelancer ─→ Claude CLI
    ├─ Veteran ────→ Claude CLI
    ├─ Award Winner→ Claude CLI
    └─ Newcomer ───→ Claude CLI
    ↓
Results収集・集約
    ↓
List[AgentResult]
```

### 3. EvaluationAgent

**責務**: 提出物の評価と勝者選定

**評価プロセス**:
```
Submissions (5つ)
    ↓
Evaluation Prompt + Context
    ↓
Claude CLI (評価専用プロンプト)
    ↓
JSON Output:
    - winner: str
    - scores: Dict[str, float]
    - reasoning: str
    - partial_adoptions: List[...]
    ↓
SelectionResult
```

**フォールバック機能**:
- 評価失敗時は単純スコアリング
- 成功した提出物を優先選択

### 4. FeedbackLoopManager

**責務**: 反復改善サイクルの管理

**フィードバックループフロー**:
```
初期Context
    ↓
┌─────────────────────────┐
│ Iteration Loop (max 3)  │
│                         │
│ 1. Run Agents (並列)    │
│      ↓                  │
│ 2. Evaluate (評価)      │
│      ↓                  │
│ 3. Check Score          │
│      ↓                  │
│   Score >= Threshold?   │
│      YES → Break        │
│      NO  → Continue     │
│      ↓                  │
│ 4. Generate Feedback    │
│      ↓                  │
│ 5. Update Context       │
│      ↓                  │
│   (Loop back to 1)      │
└─────────────────────────┘
    ↓
Final Result
```

**反復データ構造**:
```python
@dataclass
class IterationResult:
    iteration_num: int
    agent_results: List[AgentResult]
    evaluation: SelectionResult
    score: float
    improvement: float
```

### 5. SharedState / PipelineState

**責務**: セッション状態の管理・永続化

**状態階層**:
```
SharedState (低レベル)
    ├── Phase 0-9の状態
    ├── 試行履歴
    └── メタデータ

PipelineState (高レベル)
    ├── SharedStateラッパー
    ├── パイプライン検証
    ├── 進捗追跡
    └── サマリー生成
```

**状態遷移**:
```
not_started
    ↓ mark_phase_started()
in_progress
    ↓ mark_phase_completed()
completed / failed
```

---

## Phase別詳細

### Phase 0: Audio Analysis

**入力**: 音声ファイル (MP3, WAV, etc.)
**出力**: 音声特徴データ

```python
{
    "audio_file": "path/to/song.mp3",
    "duration": 180.0,  # 秒
    "bpm": 120,         # BPM
    "beats": [...],     # ビート位置
    "sections": [...]   # セクション区切り
}
```

**実装**:
- Placeholder（librosa統合予定）
- BPM検出、ビートトラッキング、セクション検出

### Phase 1-4: Design Phases

**Phase 1: Story & Message**
- 入力: 音声解析結果
- 出力: ストーリー・メッセージ

**Phase 2: Section Division**
- 入力: Phase 1結果 + 音声解析
- 出力: セクション分割

**Phase 3: Clip Division**
- 入力: Phase 1-2結果
- 出力: クリップ分割・設計

**Phase 4: Generation Strategy**
- 入力: Phase 1-3結果
- 出力: 生成戦略

**共通フロー**:
```
Context構築
    ↓
5 Directors並列実行
    ↓
Evaluation
    ↓
Score >= Threshold?
    YES → 完了
    NO  → Feedback生成 → 再実行
```

### Phase 5: MCP Clip Generation

**アーキテクチャ**:
```
Clip Designs (Phase 3)
    ↓
MCPSelector (動的選択)
    ↓
MCPClipGenerator
    ├─ Semaphore (並列制限)
    ├─ Retry Logic (指数バックオフ)
    └─ Progress Tracking
    ↓
Generated Clips
```

**並列生成**:
```python
semaphore = asyncio.Semaphore(max_parallel)

async def generate_with_limit(clip_design):
    async with semaphore:
        return await generate_clip(clip_design)

tasks = [generate_with_limit(d) for d in designs]
results = await asyncio.gather(*tasks)
```

### Phase 6: CLIP Quality Evaluation

**評価フロー**:
```
Generated Clips
    ↓
For each clip:
    ├─ CLIP Similarity (プロンプト一致度)
    └─ Technical Quality (解像度、FPS、コーデック)
    ↓
Overall Score = CLIP × 0.6 + Tech × 0.4
    ↓
Score < Threshold?
    YES → Regeneration Queue
    NO  → Pass
    ↓
Regeneration Loop (max 2回)
    ↓
Final Results
```

### Phase 7: Video Editing

**編集パイプライン**:
```
Validated Clips
    ↓
1. Trim (並列)
    ├─ clip_001.mp4 → trimmed/clip_001.mp4
    ├─ clip_002.mp4 → trimmed/clip_002.mp4
    └─ ...
    ↓
2. Organize by Section
    ├─ Section 0: [clip_001, clip_002]
    ├─ Section 1: [clip_003, clip_004]
    └─ ...
    ↓
3. Merge within Sections
    ├─ Section 0 → section_000.mp4
    ├─ Section 1 → section_001.mp4
    └─ ...
    ↓
4. Merge All Sections
    ↓
final_sequence.mp4
```

**トランジション実装**:
```bash
# 2クリップ: xfade
ffmpeg -i clip1.mp4 -i clip2.mp4 \
  -filter_complex "[0][1]xfade=duration=1:offset=5" \
  output.mp4

# 複数クリップ: チェーン
ffmpeg -i clip1.mp4 -i clip2.mp4 -i clip3.mp4 \
  -filter_complex \
  "[0][1]xfade=duration=1:offset=5[v01]; \
   [v01][2]xfade=duration=1:offset=10[out]" \
  -map "[out]" output.mp4
```

### Phase 8: Effects Code Generation

**3エージェント競争**:
```
Context (Phase 1-7結果)
    ↓
3 Agents並列実行
    ├─ Minimalist  → シンプルコード
    ├─ Creative    → 実験的コード
    └─ Balanced    → バランスコード
    ↓
Evaluation
    ├─ Code Quality (30%)
    ├─ Visual Impact (25%)
    ├─ Performance (20%)
    ├─ Creativity (15%)
    └─ Completeness (10%)
    ↓
Winner + Partial Adoptions
    ↓
Code Merging
    ├─ Extract imports
    ├─ Extract components
    ├─ Merge with adoptions
    └─ Generate final code
    ↓
effects.tsx
```

### Phase 9: Remotion Rendering

**レンダリングパイプライン**:
```
Inputs:
    ├─ Video Sequence (Phase 7)
    ├─ Effects Code (Phase 8)
    └─ Audio (Phase 0)
    ↓
Remotion Project Setup
    ├─ src/Composition.tsx
    ├─ src/Effects.tsx
    ├─ src/Root.tsx
    └─ public/ (assets)
    ↓
npx remotion render
    ├─ Composition: MVOrchestra
    ├─ Resolution: 1920×1080
    ├─ FPS: 30
    ├─ Codec: h264
    └─ CRF: 18
    ↓
final_output.mp4
```

---

## データフロー

### Phase間データ受け渡し

```
Phase 0 Output
    ↓ (SharedState)
Phase 1 Input
    ↓
Phase 1 Output (Winner)
    ↓ (SharedState)
Phase 2 Input
    ↓
...
    ↓
Phase 9 Output
```

### Context構築例

```python
def _build_context(phase_num: int) -> Dict[str, Any]:
    context = {}

    # Phase 0
    phase0 = get_phase_data(0)
    if phase0:
        context["audio_analysis"] = phase0

    # Phase 1
    if phase_num >= 2:
        phase1 = get_phase_data(1)
        if phase1 and "winner" in phase1:
            context["story"] = phase1["winner"]

    # Phase 2
    if phase_num >= 3:
        phase2 = get_phase_data(2)
        if phase2 and "winner" in phase2:
            context["sections"] = phase2["winner"]

    # ...

    return context
```

---

## 状態管理

### State Schema

```json
{
  "session_id": "my_session",
  "created_at": "2025-11-16T10:00:00",
  "updated_at": "2025-11-16T12:30:00",
  "phases": {
    "0": {
      "phase_number": 0,
      "status": "completed",
      "started_at": "2025-11-16T10:00:00",
      "completed_at": "2025-11-16T10:00:05",
      "current_result": {...},
      "attempts": [
        {
          "attempt_number": 1,
          "started_at": "2025-11-16T10:00:00",
          "completed_at": "2025-11-16T10:00:05",
          "success": true,
          "result": {...}
        }
      ]
    },
    "1": {
      "phase_number": 1,
      "status": "completed",
      "started_at": "2025-11-16T10:00:10",
      "completed_at": "2025-11-16T10:15:30",
      "current_result": {
        "winner": "award_winner",
        "score": 85,
        "iterations": 2
      },
      "attempts": [...]
    }
  }
}
```

### トランザクション境界

各Phaseの完了時に状態を保存：

```python
# Phase開始
state.mark_phase_started(phase_num)

try:
    # Phase実行
    result = await run_phase(...)

    # Phase完了
    state.mark_phase_completed(phase_num, result, success=True)

except Exception as e:
    # Phase失敗
    state.mark_phase_completed(phase_num, {"error": str(e)}, success=False)
    raise
```

---

## 並列処理

### Async/Await パターン

```python
# 並列ディレクター実行
async def run_all_directors():
    tasks = [run_director(d) for d in directors]
    results = await asyncio.gather(*tasks)
    return results

# 並列クリップ生成（セマフォ制御）
async def generate_all_clips():
    semaphore = asyncio.Semaphore(max_parallel)

    async def generate_with_limit(design):
        async with semaphore:
            return await generate_clip(design)

    tasks = [generate_with_limit(d) for d in designs]
    return await asyncio.gather(*tasks)
```

### リソース制御

**セマフォによる同時実行制限**:
```python
# 最大3並列
semaphore = asyncio.Semaphore(3)

# 使用例
async with semaphore:
    await expensive_operation()
```

**タイムアウト**:
```python
try:
    result = await asyncio.wait_for(
        operation(),
        timeout=300.0  # 5分
    )
except asyncio.TimeoutError:
    logger.error("Operation timed out")
```

---

## エラーハンドリング

### エラー階層

```
Exception
    ├── VideoEditError (Phase 7)
    ├── EffectsGenerationError (Phase 8)
    ├── RemotionRenderError (Phase 9)
    └── MCPGenerationError (Phase 5)
```

### エラー処理戦略

**1. Retry（リトライ）**:
```python
for attempt in range(max_retries):
    try:
        result = await operation()
        break
    except RetryableError as e:
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)  # 指数バックオフ
        else:
            raise
```

**2. Fallback（フォールバック）**:
```python
try:
    result = await primary_method()
except PrimaryError:
    result = fallback_method()
```

**3. Graceful Degradation（段階的縮退）**:
```python
if not evaluator.available():
    logger.warning("Using fallback evaluation")
    result = simple_evaluation()
```

---

## 拡張性

### 新しいPhaseの追加

```python
# 1. Runnerの実装
def run_phase10(session_id: str) -> Dict[str, Any]:
    # Phase 10ロジック
    pass

# 2. Phase登録
PHASE_RUNNERS = {
    0: run_phase0,
    ...
    10: run_phase10
}

# 3. Orchestratorに統合
orchestrator.run_pipeline(start_phase=0, end_phase=10)
```

### 新しいディレクターの追加

```python
# .claude/prompts/phase1_新director.md を追加

# agent_executor.py
PHASE_1_4_DIRECTORS = [
    "corporate",
    ...
    "新director"  # 追加
]
```

### 新しいMCPサーバーの追加

```python
# config/orchestrator_config.json
{
  "mcp": {
    "new_server": {
      "priority": 3,
      "suitable_for": ["style1", "style2"],
      "endpoint": "http://..."
    }
  }
}
```

---

## パフォーマンス最適化

### ボトルネック特定

```python
import time

start = time.time()
result = await operation()
elapsed = time.time() - start

logger.info(f"Operation took {elapsed:.2f}s")
```

### 最適化手法

1. **並列化**: 独立タスクは並列実行
2. **キャッシング**: 重複計算を避ける
3. **レイジー評価**: 必要時のみ計算
4. **リソース制限**: セマフォで同時実行制御

---

## セキュリティ考慮事項

### 入力検証

```python
# ファイルパス検証
if not audio_file.exists():
    raise FileNotFoundError(f"Audio file not found: {audio_file}")

# セッションID検証
if not session_id.isalnum():
    raise ValueError("Invalid session ID")
```

### サンドボックス化

- Claude CLI実行は`--dangerous-skip-permission`フラグ使用
- 外部コマンドは`subprocess`経由で安全に実行

### シークレット管理

- API keyなどは環境変数経由
- 設定ファイルにシークレットを含めない

---

**作成**: 2025-11-16
**バージョン**: 3.0.0
