# MV Orchestra v3.0

**完全自動化ミュージックビデオ生成システム**

AIエージェントのオーケストレーションによる、音楽からミュージックビデオまでの完全自動生成パイプライン。

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎬 概要

MV Orchestraは、音楽ファイルから完成したミュージックビデオを自動生成する、革新的なAIオーケストレーションシステムです。

### 主な特徴

- **🤖 マルチエージェント競争**: 5つの異なるディレクターAIが並列で提案を生成し、最適な案を自動選定
- **🔄 品質フィードバックループ**: 自動評価と反復改善により高品質な結果を保証
- **⚡ 完全並列処理**: 非同期I/Oと並列実行で高速化
- **💾 状態管理**: セッション永続化により中断・再開が可能
- **🧪 Mock Mode**: 外部依存なしでテスト可能
- **📊 Phase 0-9パイプライン**: 音声解析から最終レンダリングまで10フェーズで構成

---

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    MV Orchestra v3.0                         │
│                 完全自動化パイプライン                          │
└─────────────────────────────────────────────────────────────┘

Phase 0: Audio Analysis (librosa)
    ↓ [音声特徴抽出: BPM, ビート, セクション]

Phase 1-4: Design (5 Directors × Multi-Agent Competition)
    ├─ Phase 1: Story & Message Design
    ├─ Phase 2: Section Division
    ├─ Phase 3: Clip Division
    └─ Phase 4: Generation Strategy
    ↓ [評価 → フィードバック → 改善 (最大3回反復)]

Phase 5: MCP Clip Generation (Kamuicode)
    ↓ [動的MCPサーバー選択、並列生成]

Phase 6: CLIP Quality Evaluation
    ↓ [品質評価、不合格クリップの再生成]

Phase 7: Video Editing (ffmpeg)
    ↓ [トリミング、トランジション、マージ]

Phase 8: Effects Code Generation (3 Agents)
    ↓ [Remotionエフェクトコード生成]

Phase 9: Remotion Final Rendering
    ↓ [最終動画レンダリング]

✅ 完成したミュージックビデオ (.mp4)
```

---

## 🚀 クイックスタート

### 前提条件

- Python 3.8以上
- Claude CLI (`claude` コマンドが利用可能)

### インストール

```bash
git clone <repository-url>
cd test
```

### 基本的な使い方

#### 1. デザインフェーズ実行 (Phase 0-4)

```bash
# 音声ファイルから設計まで自動実行
python3 run_orchestrator.py my_session --audio song.mp3
```

#### 2. 生成・後処理フェーズ実行 (Phase 5-9)

```bash
# Mock modeで実行（外部依存なし）
python3 run_phase5_9.py my_session --mock

# 実際のMCP/ffmpeg/Remotionで実行
python3 run_phase5_9.py my_session --no-mock
```

---

## 📖 詳細ドキュメント

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: システムアーキテクチャ詳細
- **[QUICKSTART.md](QUICKSTART.md)**: 詳細なクイックスタートガイド
- **[README_PHASE5_9.md](README_PHASE5_9.md)**: Phase 5-9詳細ガイド

---

## 🎯 Phase別ガイド

### Phase 0: Audio Analysis

音声ファイルの解析（BPM、ビート検出、セクション分割）

```bash
python3 run_orchestrator.py my_session --audio song.mp3 --start-phase 0 --end-phase 0
```

### Phase 1-4: Design Phases

5つのディレクターAIによるマルチエージェント設計競争

**5つのディレクター**:
- 🏢 **Corporate**: 企業的、安定志向
- 💼 **Freelancer**: 自由な発想、実験的
- 🎓 **Veteran**: 経験豊富、伝統的
- 🏆 **Award Winner**: 受賞歴重視、革新的
- 🌟 **Newcomer**: 新人視点、斬新

```bash
# 全デザインフェーズ実行
python3 run_orchestrator.py my_session --start-phase 1 --end-phase 4

# カスタム品質閾値（デフォルト: 70）
python3 run_orchestrator.py my_session --threshold 80 --max-iterations 5
```

**出力例**:
```
Phase 1: Story & Message
  ✓ corporate: 12.3s (score: 75)
  ✓ freelancer: 11.8s (score: 82)
  ✓ veteran: 13.1s (score: 78)
  ✓ award_winner: 12.5s (score: 85)
  ✓ newcomer: 11.2s (score: 72)

  Winner: award_winner (score: 85/100)
  Iterations: 1
```

### Phase 5: MCP Clip Generation

MCP (Model Context Protocol) 経由での動画クリップ生成

**動的MCPサーバー選択**:
- Runway Gen-3 (リアル映像)
- Kamuicode Anime (アニメ調)
- Pika (実験的)

```bash
python3 run_phase5_9.py my_session --start-phase 5 --end-phase 5 --mock
```

### Phase 6: CLIP Quality Evaluation

CLIP類似度と技術品質による自動評価・再生成

**評価基準**:
- CLIP Similarity: 60% (プロンプトとの意味的一致)
- Technical Quality: 40% (解像度、FPS、コーデック)

### Phase 7: Video Editing

ffmpegによるトリミング・トランジション・マージ

**トランジション対応**:
- `crossfade`: クロスフェード
- `fade`: フェードブラック
- `none`: トランジションなし

```bash
python3 run_phase5_9.py my_session --start-phase 7 --end-phase 7
```

### Phase 8: Effects Code Generation

3つのエージェントによるRemotion効果コード生成

**3つのアプローチ**:
- 🎨 **Minimalist**: シンプル、高パフォーマンス
- 🚀 **Creative**: 実験的、視覚的インパクト
- ⚖️ **Balanced**: プロフェッショナル、バランス重視

### Phase 9: Remotion Final Rendering

最終動画レンダリング

**レンダリング設定**:
- 解像度: 1920×1080
- FPS: 30
- コーデック: h264
- CRF: 18 (高品質)

---

## 🔧 設定

### 品質設定

```bash
# 高品質設定（反復多め）
python3 run_orchestrator.py my_session --audio song.mp3 --threshold 85 --max-iterations 5

# 高速設定（反復少なめ）
python3 run_orchestrator.py my_session --audio song.mp3 --threshold 60 --max-iterations 1
```

### MCPサーバー設定

`config/orchestrator_config.json` で設定:

```json
{
  "mcp": {
    "runway_gen3": {
      "priority": 1,
      "suitable_for": ["realistic", "cinematic"]
    },
    "kamuicode_anime": {
      "priority": 2,
      "suitable_for": ["anime", "illustration"]
    }
  }
}
```

---

## 📁 プロジェクト構成

```
test/
├── core/                          # コアコンポーネント
│   ├── orchestrator_agent.py     # メインオーケストレーター
│   ├── agent_executor.py         # エージェント並列実行
│   ├── evaluation_agent.py       # 評価・勝者選定
│   ├── feedback_loop_manager.py  # フィードバックループ
│   ├── pipeline_state.py         # パイプライン状態管理
│   ├── shared_state.py           # セッション状態管理
│   ├── mcp_selector.py           # MCP選択ロジック
│   ├── mcp_clip_generator.py     # MCP動画生成
│   ├── clip_evaluator.py         # CLIP品質評価
│   ├── video_editor.py           # ffmpeg動画編集
│   ├── effects_generator.py      # Remotionエフェクト生成
│   ├── remotion_renderer.py      # Remotionレンダリング
│   └── utils.py                  # ユーティリティ
│
├── phase5/                        # Phase 5実装
│   ├── __init__.py
│   └── runner.py
│
├── phase6-9/                      # Phase 6-9実装
│   └── (同様の構造)
│
├── .claude/prompts/               # エージェントプロンプト
│   ├── phase1_corporate.md       # Phase 1: Corporate
│   ├── phase1_freelancer.md      # Phase 1: Freelancer
│   ├── ...                       # (24個のプロンプト)
│   └── phase8_evaluation.md      # Phase 8: 評価
│
├── sessions/                      # セッションデータ
│   └── {session_id}/
│       ├── state.json            # セッション状態
│       ├── phase0/ ... phase9/   # Phase別出力
│       └── phase9/final_output.mp4  # 完成動画
│
├── run_orchestrator.py            # Phase 0-4実行スクリプト
├── run_phase5_9.py               # Phase 5-9実行スクリプト
├── README.md                     # このファイル
├── ARCHITECTURE.md               # アーキテクチャ詳細
└── QUICKSTART.md                 # クイックスタート
```

---

## 🧪 テスト

### Mock Mode

外部依存なしでテスト:

```bash
# Phase 1-4 (Claude CLIは必要)
python3 run_orchestrator.py test_session --audio dummy.mp3

# Phase 5-9 (完全Mock)
python3 run_phase5_9.py test_session --mock
```

### 実際の依存を使用

```bash
# MCP、CLIP、ffmpeg、Remotionが必要
python3 run_phase5_9.py test_session --no-mock
```

---

## 📊 セッション管理

### セッション構造

```
sessions/{session_id}/
├── state.json                 # 全体状態
├── phase0/
│   └── results.json          # 音声解析結果
├── phase1/
│   ├── iteration_1/          # 反復1
│   │   ├── corporate_context.json
│   │   ├── freelancer_context.json
│   │   └── ...
│   └── results.json          # Phase 1最終結果
├── ...
└── phase9/
    ├── final_output.mp4      # ★完成動画★
    └── results.json
```

### セッション再開

```bash
# 中断したセッションを再開
python3 run_orchestrator.py existing_session --start-phase 3 --end-phase 4
```

---

## 🔍 トラブルシューティング

### よくある問題

**1. Claude CLI not found**
```bash
# Claude CLIがインストールされているか確認
which claude

# パスを明示的に指定
python3 run_orchestrator.py my_session --claude-cli /path/to/claude
```

**2. MCP接続エラー**
```bash
# Mock modeを使用
python3 run_phase5_9.py my_session --mock
```

**3. ffmpegエラー**
```bash
# ffmpegインストール
sudo apt install ffmpeg  # Linux
brew install ffmpeg      # Mac
```

**4. メモリ不足**
```bash
# 並列数を減らす（AgentExecutorの max_parallel）
# config/orchestrator_config.json で設定
```

---

## 🛠️ 開発

### 要件

- Python 3.8+
- Claude CLI
- (オプション) ffmpeg, Remotion, CLIP

### セットアップ

```bash
# 仮想環境
python3 -m venv venv
source venv/bin/activate

# 依存関係（将来追加予定）
# pip install -r requirements.txt
```

### コーディング規約

- Type hints必須
- Docstrings (Google style)
- Async/await for I/O
- Logging使用

---

## 📈 パフォーマンス

### 推定処理時間

| Phase | 処理時間 (Mock) | 処理時間 (実環境) |
|-------|----------------|------------------|
| Phase 0 | 即座 | 5-10秒 |
| Phase 1-4 | 即座 | 各5-15分 |
| Phase 5 | 即座 | 10-30分 |
| Phase 6 | 即座 | 5-10分 |
| Phase 7 | 即座 | 2-5分 |
| Phase 8 | 即座 | 3-8分 |
| Phase 9 | 即座 | 10-20分 |
| **合計** | **< 1分** | **1-3時間** |

### 最適化のポイント

- 並列実行数調整（`max_parallel`）
- 品質閾値調整（`threshold`）
- 反復回数制限（`max_iterations`）

---

## 🤝 貢献

貢献を歓迎します！

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 ライセンス

MIT License

---

## 🙏 謝辞

- **Anthropic**: Claude API & Claude CLI
- **Kamuicode**: MCP video generation
- **OpenAI**: CLIP model
- **FFmpeg**: Video processing
- **Remotion**: Video rendering framework

---

## 📞 サポート

- **Issues**: [GitHub Issues](https://github.com/your-repo/test/issues)
- **Documentation**: [docs/](docs/)

---

**作成**: 2025-11-16
**バージョン**: 3.0.0
**ステータス**: Production Ready 🚀
