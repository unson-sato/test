# Phase 5-9: Video Generation & Post-Processing Pipeline

完全な動画生成・後処理パイプライン（Phase 5-9）の実装とドキュメント。

## 概要

Phase 5-9は、設計フェーズ（Phase 1-4）の結果を受けて、実際のミュージックビデオを生成・編集・レンダリングする処理フローです。

### パイプライン構成

```
Phase 5: MCP Clip Generation
    ↓ (生成された動画クリップ)
Phase 6: CLIP Quality Evaluation
    ↓ (品質検証済みクリップ)
Phase 7: Video Editing (Trim & Merge)
    ↓ (編集・統合された動画シーケンス)
Phase 8: Effects Code Generation
    ↓ (Remotionエフェクトコード)
Phase 9: Remotion Final Rendering
    ↓
✓ 完成したミュージックビデオ
```

## Phase別詳細

### Phase 5: MCP Clip Generation

**役割**: Phase 3で設計されたクリップをMCP経由で生成

**主要コンポーネント**:
- `core/mcp_selector.py`: クリップ特性に基づく最適MCPサーバー選択
- `core/mcp_clip_generator.py`: 並列クリップ生成・リトライロジック
- `phase5/runner.py`: Phase 5実行エントリーポイント

**機能**:
- 動的MCPサーバー選択（Kamuicode、Runway Gen-3、Pikaなど）
- セマフォベース並列生成（同時実行数制限）
- 指数バックオフによる自動リトライ
- Mock mode対応（実際のMCP呼び出しなしでテスト可能）

**使用例**:
```python
from phase5 import run_phase5

result = run_phase5(
    session_id="my_session",
    max_parallel=3,
    max_retries=2,
    mock_mode=True  # テスト用
)
```

**出力**:
- `sessions/{session_id}/phase5/clips/`: 生成されたクリップ
- `sessions/{session_id}/phase5/results.json`: 生成結果メタデータ

---

### Phase 6: CLIP Quality Evaluation

**役割**: 生成されたクリップの品質評価と不合格クリップの再生成

**主要コンポーネント**:
- `core/clip_evaluator.py`: CLIP類似度・技術品質チェック
- `phase6/runner.py`: 評価ループと再生成フィードバック

**機能**:
- CLIP類似度スコア（プロンプトとの一致度）
- 技術品質チェック（解像度、フレームレート、コーデック）
- 品質閾値に基づく自動再生成（最大試行回数制限付き）
- Mock mode対応（実際のCLIPモデルなしでテスト可能）

**使用例**:
```python
from phase6 import run_phase6

result = run_phase6(
    session_id="my_session",
    similarity_threshold=0.75,
    technical_threshold=0.70,
    max_regeneration_attempts=2,
    mock_mode=True
)
```

**評価基準**:
- **CLIP Similarity**: プロンプトとの意味的類似度（0.0-1.0）
- **Technical Quality**: 解像度・FPS・コーデック適合性（0.0-1.0）
- **Overall Score**: 加重平均（CLIP 60% + Technical 40%）

**出力**:
- `sessions/{session_id}/phase6/results.json`: 評価結果
- `sessions/{session_id}/phase6/regenerated_clips/`: 再生成されたクリップ

---

### Phase 7: Video Editing (Trim & Merge)

**役割**: クリップを正確な長さにトリミングし、セクション・シーケンス単位でマージ

**主要コンポーネント**:
- `core/video_editor.py`: ffmpegベースのトリミング・マージ処理
- `phase7/runner.py`: 編集パイプライン実行

**機能**:
- **クリップトリミング**: Phase 3設計通りの正確な長さに調整
- **セクション内マージ**: セクション単位でクリップを統合
- **全体統合**: 全セクションを最終シーケンスに結合
- **トランジション**: crossfade、fade、なし（選択可能）
- **並列処理**: 複数クリップの同時トリミング
- Mock mode対応

**使用例**:
```python
from phase7 import run_phase7

result = run_phase7(
    session_id="my_session",
    max_parallel_trims=3,
    transition_duration=0.5,  # 0.5秒のトランジション
    transition_type="crossfade",  # crossfade, fade, none
    mock_mode=True
)
```

**トランジションタイプ**:
- `none`: トランジションなし（単純な結合）
- `crossfade`: クロスフェード（fade transition）
- `fade`: フェードブラック

**出力**:
- `sessions/{session_id}/phase7/trimmed_clips/`: トリミング済みクリップ
- `sessions/{session_id}/phase7/merged_sections/`: セクション別統合動画
- `sessions/{session_id}/phase7/merged_sections/full_sequence.mp4`: 最終シーケンス

---

### Phase 8: Effects Code Generation

**役割**: Remotionエフェクトコードを3つの異なるアプローチで生成・評価・統合

**主要コンポーネント**:
- `core/effects_generator.py`: エフェクトコード生成・評価・マージ
- `core/agent_executor.py`: エージェント実行（Claude CLI経由）
- `phase8/runner.py`: 3エージェントシステム実行
- `.claude/prompts/phase8_*.md`: エージェント用プロンプト

**3つのエージェント**:
1. **Minimalist**: シンプル・高パフォーマンス重視
2. **Creative**: 実験的・視覚的インパクト重視
3. **Balanced**: プロフェッショナル・バランス重視

**機能**:
- 並列エージェント実行
- コード品質分析（複雑度、創造性、パフォーマンス）
- 評価エージェントによる勝者選定
- Partial Adoption（他エージェントの優れた部分を採用）
- TypeScript/Reactコードマージ
- Mock mode対応

**使用例**:
```python
from phase8 import run_phase8

result = run_phase8(
    session_id="my_session",
    mock_mode=True
)
```

**評価基準**:
- **Code Quality** (30%): TypeScript構文、型安全性、保守性
- **Visual Impact** (25%): 視覚的魅力、ストーリーとの整合性
- **Performance** (20%): レンダリング速度、最適化
- **Creativity vs. Practicality** (15%): 革新性と実用性のバランス
- **Completeness** (10%): 網羅性、エッジケース処理

**出力**:
- `sessions/{session_id}/phase8/effects.tsx`: 最終エフェクトコード
- `sessions/{session_id}/phase8/submissions/`: 各エージェントの提出コード
- `sessions/{session_id}/phase8/results.json`: 評価結果

---

### Phase 9: Remotion Final Rendering

**役割**: Remotionを使って最終ミュージックビデオをレンダリング

**主要コンポーネント**:
- `core/remotion_renderer.py`: Remotionプロジェクト構築・レンダリング
- `phase9/runner.py`: 最終レンダリング実行

**機能**:
- Remotionプロジェクト自動構築
- Phase 7動画シーケンス統合
- Phase 8エフェクトコード統合
- オリジナル音声統合
- 高品質レンダリング設定（解像度、FPS、ビットレート）
- Mock mode対応

**使用例**:
```python
from phase9 import run_phase9
from core import RenderConfig

config = RenderConfig(
    composition_id="MVOrchestra",
    width=1920,
    height=1080,
    fps=30,
    codec="h264",
    crf=18,  # 品質（低いほど高品質）
    video_bitrate="8M"
)

result = run_phase9(
    session_id="my_session",
    render_config=config,
    mock_mode=True
)
```

**レンダリング設定**:
- **解像度**: 1920x1080（デフォルト）
- **FPS**: 30（デフォルト）
- **コーデック**: h264（デフォルト）
- **CRF**: 18（18-23が推奨、低いほど高品質）
- **ビットレート**: 8M（デフォルト）

**出力**:
- `sessions/{session_id}/phase9/final_output.mp4`: 完成したミュージックビデオ
- `sessions/{session_id}/phase9/remotion_project/`: Remotionプロジェクト
- `sessions/{session_id}/phase9/results.json`: レンダリング結果

---

## 使用方法

### 基本的な実行

```bash
# 完全なPhase 5-9パイプラインをMock modeで実行
python3 run_phase5_9.py my_session --mock

# 特定のPhase範囲のみ実行
python3 run_phase5_9.py my_session --start-phase 5 --end-phase 7 --mock

# Verbose logging付き
python3 run_phase5_9.py my_session --mock -v
```

### 個別Phase実行

```python
from phase5 import run_phase5
from phase6 import run_phase6
from phase7 import run_phase7
from phase8 import run_phase8
from phase9 import run_phase9

# Phase 5のみ実行
run_phase5("my_session", mock_mode=True)

# Phase 6のみ実行
run_phase6("my_session", mock_mode=True)

# ... 以下同様
```

### 実際の外部依存を使用（Mock mode無効）

**前提条件**:
- Kamuicode MCP serverが利用可能
- CLIPモデルがインストール済み（`pip install transformers torch`）
- ffmpegがインストール済み
- Remotionプロジェクトがセットアップ済み

```bash
# Mock modeを無効化
python3 run_phase5_9.py my_session --no-mock
```

---

## セッション構造

```
sessions/
└── {session_id}/
    ├── state.json                    # セッション状態
    ├── phase5/
    │   ├── clips/                    # 生成クリップ
    │   └── results.json
    ├── phase6/
    │   ├── results.json              # 評価結果
    │   └── regenerated_clips/        # 再生成クリップ
    ├── phase7/
    │   ├── trimmed_clips/            # トリミング済みクリップ
    │   ├── merged_sections/          # セクション別動画
    │   │   └── full_sequence.mp4    # 最終シーケンス
    │   └── results.json
    ├── phase8/
    │   ├── effects.tsx               # 最終エフェクトコード
    │   ├── submissions/              # エージェント別コード
    │   └── results.json
    └── phase9/
        ├── final_output.mp4          # ★完成動画★
        ├── remotion_project/         # Remotionプロジェクト
        ├── results.json
        └── render_logs.txt
```

---

## 技術詳細

### Mock Mode

全てのPhaseはMock modeに対応しており、外部依存なしでテスト可能です。

**Mock modeで模倣される処理**:
- **Phase 5**: MCP API呼び出し（ダミークリップパス返却）
- **Phase 6**: CLIP推論（ランダムスコア生成）
- **Phase 7**: ffmpeg実行（メタデータのみ）
- **Phase 8**: エージェント実行（プレースホルダーコード生成）
- **Phase 9**: Remotionレンダリング（空ファイル作成）

### エラーハンドリング

各Phaseで堅牢なエラーハンドリング:
- リトライロジック（Phase 5, 6）
- フォールバック処理（Phase 7トランジション）
- 詳細なログ出力
- セッション状態への失敗記録

### パフォーマンス最適化

- **並列処理**: Phase 5（クリップ生成）、Phase 7（トリミング）
- **セマフォによる同時実行制限**: リソース消費の制御
- **AsyncIO**: 非同期I/O処理
- **段階的処理**: メモリ効率の良いストリーム処理

---

## トラブルシューティング

### Phase 5: MCP接続エラー

```
Error: MCP server not available
```

**解決策**:
1. Mock modeを使用: `--mock`
2. MCPサーバーの起動確認
3. `config/orchestrator_config.json`のMCP設定確認

### Phase 6: CLIP評価失敗

```
Error: CLIP model not found
```

**解決策**:
1. Mock modeを使用: `--mock`
2. CLIPインストール: `pip install transformers torch`
3. モデルダウンロード確認

### Phase 7: ffmpegエラー

```
Error: ffmpeg not found
```

**解決策**:
1. Mock modeを使用: `--mock`
2. ffmpegインストール: `apt install ffmpeg`（Linux）/ `brew install ffmpeg`（Mac）
3. PATH設定確認

### Phase 8: エージェント実行失敗

```
Error: Prompt file not found
```

**解決策**:
1. `.claude/prompts/phase8_*.md`の存在確認
2. プロンプトファイル権限確認

### Phase 9: Remotionレンダリング失敗

```
Error: remotion not found
```

**解決策**:
1. Mock modeを使用: `--mock`
2. Remotionインストール: `npm install remotion`
3. Remotionプロジェクトセットアップ確認

---

## 今後の改善予定

### 高優先度
- [ ] 実際のMCP統合テスト
- [ ] CLIPモデル統合テスト
- [ ] ffmpeg実行テスト
- [ ] Remotionレンダリングテスト

### 中優先度
- [ ] Unit test追加（pytest）
- [ ] 音声同期の精度向上
- [ ] トランジション種類の追加
- [ ] エフェクトライブラリの拡充

### 低優先度
- [ ] GPU加速対応
- [ ] 分散レンダリング対応
- [ ] リアルタイムプレビュー
- [ ] WebUIの追加

---

## 参考

- **MCP (Model Context Protocol)**: https://github.com/anthropics/mcp
- **CLIP**: https://github.com/openai/CLIP
- **ffmpeg**: https://ffmpeg.org/
- **Remotion**: https://www.remotion.dev/

---

## ライセンス

(プロジェクトライセンスに準拠)

---

**作成日**: 2025-11-16
**最終更新**: 2025-11-16
