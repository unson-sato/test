# MV Orchestra v3.0 - Quick Start Guide

このガイドでは、MV Orchestra v3.0を使って最初のミュージックビデオを生成する手順を説明します。

---

## 📋 前提条件

### 必須

- **Python 3.8以上**
- **Claude CLI** (`claude`コマンド)

### オプション（実環境で実行する場合）

- **FFmpeg**: 動画編集 (Phase 7)
- **Remotion**: 最終レンダリング (Phase 9)
- **CLIP (transformers)**: 品質評価 (Phase 6)
- **librosa**: 音声解析 (Phase 0)
- **MCP Server**: 動画生成 (Phase 5)

---

## 🚀 5分でクイックスタート

### ステップ 1: リポジトリクローン

```bash
git clone <repository-url>
cd test
```

### ステップ 2: Claude CLI確認

```bash
# Claude CLIがインストールされているか確認
which claude
# 出力例: /usr/local/bin/claude

# バージョン確認
claude --version
```

### ステップ 3: Mock modeで全パイプライン実行

```bash
# Phase 0-4: デザインフェーズ（Claude CLI使用）
python3 run_orchestrator.py quickstart_session --audio /path/to/song.mp3

# Phase 5-9: 生成・後処理（Mock mode）
python3 run_phase5_9.py quickstart_session --mock
```

**完了！** 🎉

セッションデータは `sessions/quickstart_session/` に保存されます。

---

## 📖 詳細チュートリアル

### シナリオ: "Summer Vibes" MV制作

架空の曲「Summer Vibes」のMVを作成します。

#### Phase 0: 音声解析

```bash
python3 run_orchestrator.py summer_vibes \
  --audio songs/summer_vibes.mp3 \
  --start-phase 0 \
  --end-phase 0
```

**出力例**:
```
Phase 0: Audio Analysis
  ✓ Duration: 180.5s
  ✓ BPM: 128
  ✓ Beats detected: 384
  ✓ Sections: 5 (Intro, Verse, Chorus, Bridge, Outro)
```

**結果確認**:
```bash
cat sessions/summer_vibes/phase0/results.json
```

#### Phase 1: Story & Message Design

```bash
python3 run_orchestrator.py summer_vibes \
  --start-phase 1 \
  --end-phase 1 \
  --threshold 75 \
  --max-iterations 3
```

**出力例**:
```
ITERATION 1/3
  Running 5 directors in parallel...
  ✓ corporate: 12.3s
  ✓ freelancer: 11.8s
  ✓ veteran: 13.1s
  ✓ award_winner: 12.5s
  ✓ newcomer: 11.2s

  Evaluating 5 submissions...
  ✓ Winner: award_winner (score: 85/100)
  ✓ Quality threshold met (85 >= 75)

Phase 1 completed
  Winner: award_winner
  Score: 85/100
  Iterations: 1
```

**結果確認**:
```bash
# 勝者の提案を確認
cat sessions/summer_vibes/phase1/results.json | jq '.winner'
```

#### Phase 2-4: 残りのデザインフェーズ

```bash
python3 run_orchestrator.py summer_vibes \
  --start-phase 2 \
  --end-phase 4 \
  --threshold 70
```

**各Phaseの出力**:
- **Phase 2**: セクション分割（Intro, Verse, Chorus, etc.）
- **Phase 3**: クリップ分割（各セクション内の詳細シーン）
- **Phase 4**: 生成戦略（MCPサーバー選択、スタイル指定）

#### Phase 5: MCP Clip Generation

```bash
# Mock mode（テスト）
python3 run_phase5_9.py summer_vibes \
  --start-phase 5 \
  --end-phase 5 \
  --mock

# 実環境（MCP必要）
python3 run_phase5_9.py summer_vibes \
  --start-phase 5 \
  --end-phase 5 \
  --no-mock
```

**Mock mode出力**:
```
Phase 5: MCP Clip Generation
  Generating 25 clips...
  ✓ clip_001: 0.1s (mock)
  ✓ clip_002: 0.1s (mock)
  ...
  ✓ clip_025: 0.1s (mock)

  Generation complete: 25/25 successful
```

**実環境出力**:
```
Phase 5: MCP Clip Generation
  Generating 25 clips (max 3 parallel)...
  ✓ clip_001: 45.2s (kamuicode_anime)
  ✓ clip_002: 38.7s (runway_gen3)
  ✓ clip_003: 42.1s (kamuicode_anime)
  ...

  Generation complete: 25/25 successful
  Total time: 8m 32s
```

#### Phase 6: CLIP Quality Evaluation

```bash
python3 run_phase5_9.py summer_vibes \
  --start-phase 6 \
  --end-phase 6 \
  --mock
```

**出力例**:
```
Phase 6: CLIP Quality Evaluation
  Evaluating 25 clips...

  Initial evaluation:
    Passing: 22 clips (88%)
    Failing: 3 clips (12%)

  Regenerating failing clips...
    clip_003: Attempt 1/2 (score: 65 → 78) ✓
    clip_012: Attempt 1/2 (score: 68 → 72) ✓
    clip_019: Attempt 1/2 (score: 62 → 75) ✓

  FINAL RESULTS
    Passing: 25/25 (100%)
    Quality rate: 100%
```

#### Phase 7: Video Editing

```bash
python3 run_phase5_9.py summer_vibes \
  --start-phase 7 \
  --end-phase 7 \
  --mock
```

**出力例**:
```
Phase 7: Video Editing
  Step 1: Trimming clips...
    ✓ Trimmed 25/25 clips

  Step 2: Organizing by section...
    Section 0 (Intro): 3 clips
    Section 1 (Verse): 8 clips
    Section 2 (Chorus): 6 clips
    Section 3 (Bridge): 4 clips
    Section 4 (Outro): 4 clips

  Step 3: Merging within sections...
    ✓ Section 0: 15.2s
    ✓ Section 1: 45.8s
    ✓ Section 2: 32.4s
    ✓ Section 3: 28.1s
    ✓ Section 4: 18.5s

  Step 4: Merging all sections...
    ✓ Final sequence: 180.0s (5 sections)

  Editing complete!
```

**トランジション付き**:
```bash
python3 run_phase5_9.py summer_vibes \
  --start-phase 7 \
  --end-phase 7 \
  --no-mock \
  --transition-duration 0.5 \
  --transition-type crossfade
```

#### Phase 8: Effects Code Generation

```bash
python3 run_phase5_9.py summer_vibes \
  --start-phase 8 \
  --end-phase 8 \
  --mock
```

**出力例**:
```
Phase 8: Effects Code Generation
  Running 3 agents...
  ✓ minimalist: 8.3s
  ✓ creative: 9.1s
  ✓ balanced: 8.7s

  Evaluating code quality...
    minimalist: 75/100
    creative: 82/100
    balanced: 88/100

  Winner: balanced
  Partial adoptions: 1
    - KaleidoscopeEffect from creative

  Merging code...
  ✓ Effects code saved to sessions/summer_vibes/phase8/effects.tsx
```

**生成されたコード確認**:
```bash
cat sessions/summer_vibes/phase8/effects.tsx
```

#### Phase 9: Remotion Final Rendering

```bash
python3 run_phase5_9.py summer_vibes \
  --start-phase 9 \
  --end-phase 9 \
  --mock
```

**出力例**:
```
Phase 9: Remotion Final Rendering
  Setting up Remotion project...
  ✓ Effects code copied
  ✓ Composition created
  ✓ Assets copied

  Rendering...
  ✓ Render complete: 180.0s
  ✓ File size: 52.3 MB
  ✓ Render time: 0.1s (mock)

  FINAL OUTPUT
    sessions/summer_vibes/phase9/final_output.mp4
```

**実環境レンダリング**:
```bash
python3 run_phase5_9.py summer_vibes \
  --start-phase 9 \
  --end-phase 9 \
  --no-mock
```

実環境では10-20分かかります。

---

## 🎬 全パイプライン一括実行

### Phase 0-4（デザイン）

```bash
python3 run_orchestrator.py my_project --audio song.mp3
```

### Phase 5-9（生成・後処理）

```bash
# Mock mode
python3 run_phase5_9.py my_project --mock

# 実環境
python3 run_phase5_9.py my_project --no-mock
```

---

## ⚙️ 高度な設定

### 品質重視設定

```bash
python3 run_orchestrator.py high_quality \
  --audio song.mp3 \
  --threshold 85 \
  --max-iterations 5 \
  --verbose
```

### 高速設定

```bash
python3 run_orchestrator.py fast \
  --audio song.mp3 \
  --threshold 60 \
  --max-iterations 1
```

### カスタムClaude CLI

```bash
python3 run_orchestrator.py custom \
  --audio song.mp3 \
  --claude-cli /custom/path/to/claude
```

### Phase範囲指定

```bash
# Phase 3-5のみ実行
python3 run_orchestrator.py partial --start-phase 3 --end-phase 4
python3 run_phase5_9.py partial --start-phase 5 --end-phase 5
```

---

## 📊 結果の確認

### セッション状態確認

```bash
python3 -c "
from core import PipelineState
state = PipelineState('my_project')
summary = state.get_summary()
print('Progress:', summary['progress']['progress_percentage'], '%')
print('Completed phases:', summary['progress']['completed_phases'])
"
```

### Phase結果確認

```bash
# Phase 1結果
cat sessions/my_project/phase1/results.json | jq '.'

# Phase 9最終出力
ls -lh sessions/my_project/phase9/final_output.mp4
```

### ログ確認

```bash
# Verboseモードでログ詳細表示
python3 run_orchestrator.py my_project --audio song.mp3 -v
```

---

## 🔧 トラブルシューティング

### Claude CLI not found

```bash
# インストール確認
which claude

# パス指定
python3 run_orchestrator.py test --claude-cli /usr/local/bin/claude
```

### セッションが見つからない

```bash
# セッション一覧
ls sessions/

# 新規セッション作成
python3 run_orchestrator.py new_session --audio song.mp3
```

### Phase失敗

```bash
# 失敗したPhaseから再開
python3 run_orchestrator.py my_project --start-phase 3 --end-phase 4

# Verbose modeでエラー詳細確認
python3 run_orchestrator.py my_project --start-phase 3 --end-phase 4 -v
```

### メモリ不足

```bash
# 並列数を減らす（config/orchestrator_config.jsonで設定）
{
  "agent_executor": {
    "max_parallel": 2  # デフォルト: 5
  }
}
```

---

## 💡 ベストプラクティス

### 1. まずMock modeでテスト

```bash
# Mock modeで動作確認
python3 run_phase5_9.py test --mock

# 問題なければ実環境実行
python3 run_phase5_9.py test --no-mock
```

### 2. Phase単位で確認

```bash
# 1 Phaseずつ実行して結果確認
python3 run_orchestrator.py project --start-phase 1 --end-phase 1
cat sessions/project/phase1/results.json

python3 run_orchestrator.py project --start-phase 2 --end-phase 2
# ...
```

### 3. 品質閾値を調整

```bash
# 最初は低めの閾値でテスト
python3 run_orchestrator.py test --threshold 60

# 満足したら高品質設定に
python3 run_orchestrator.py final --threshold 85 --max-iterations 5
```

### 4. セッション管理

```bash
# プロジェクト名にバージョン含める
python3 run_orchestrator.py project_v1 --audio song.mp3
python3 run_orchestrator.py project_v2 --audio song.mp3

# 実験用セッション
python3 run_orchestrator.py exp_fast --threshold 50 --max-iterations 1
python3 run_orchestrator.py exp_quality --threshold 90 --max-iterations 5
```

---

## 📚 次のステップ

1. **[README.md](README.md)**: 全体概要
2. **[ARCHITECTURE.md](ARCHITECTURE.md)**: システムアーキテクチャ
3. **[README_PHASE5_9.md](README_PHASE5_9.md)**: Phase 5-9詳細

---

## ❓ FAQ

### Q1: Phase 0-4だけ実行できますか？

**A**: はい、可能です。

```bash
python3 run_orchestrator.py design_only --audio song.mp3
# Phase 5-9は後で実行
python3 run_phase5_9.py design_only --mock
```

### Q2: 既存セッションを再利用できますか？

**A**: はい、セッションは永続化されます。

```bash
# 最初の実行
python3 run_orchestrator.py reusable --audio song.mp3

# 後で続きから実行
python3 run_phase5_9.py reusable --mock
```

### Q3: 特定のPhaseだけやり直せますか？

**A**: はい、Phase範囲を指定してください。

```bash
# Phase 3だけやり直し
python3 run_orchestrator.py redo --start-phase 3 --end-phase 3
```

### Q4: Mock modeと実環境の違いは？

**A**:
- **Mock mode**: 外部依存なし、高速、テスト用
- **実環境**: 実際のMCP/ffmpeg/Remotion使用、時間かかる、本番用

### Q5: エラーが出たらどうすればいい？

**A**: Verbose modeで詳細確認してください。

```bash
python3 run_orchestrator.py debug --audio song.mp3 -v 2>&1 | tee debug.log
```

---

**作成**: 2025-11-16
**バージョン**: 3.0.0

Happy MV Creation! 🎬✨
