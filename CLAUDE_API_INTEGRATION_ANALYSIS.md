# Claude API Integration Analysis

**Date**: 2025-11-16
**Purpose**: Understand the different implementations and workflows

---

## Current Situation

### 1. Local Implementation (Separate Project)
- **Location**: ローカル環境（このリポジトリとは別）
- **Method**: 方法1（tool_result を user メッセージに含める）
- **Mode**: 非対話モード（`claude -p`, `dangerously--skip-permission`）
- **Use Case**: スクリプトからの自動起動

### 2. This Repository
- **Location**: `/home/user/test`
- **Current Implementation**: Claude Code Task ツールベース
- **Class**: `CodexRunner` (core/codex_runner.py)
- **Modes**: mock / claudecode / interactive

---

## Method Comparison

### 方法1: tool_result を user メッセージに含める
```
User: [prompt + previous tool_result]
Assistant: [generates content with tool_use]
→ Loop continues...
```

**Characteristics**:
- tool_result を次の user メッセージに埋め込む
- シンプルなループ構造
- 非対話モードと相性が良い

### 方法2: tool_result を system メッセージとして送る
```
User: [prompt]
Assistant: [generates content with tool_use]
System: [tool_result]
Assistant: [continues...]
```

**Characteristics**:
- tool_result を独立した system メッセージとして扱う
- より標準的な API の使い方
- 会話履歴が自然

---

## Non-Interactive Mode Workflow

```
┌─────────────────────────────────────────┐
│   Automation Script                      │
│   (Python, Bash, etc.)                   │
└──────────────┬──────────────────────────┘
               │
               │ Calls Claude Code
               │ with prompts
               ▼
┌─────────────────────────────────────────┐
│   Claude Code (Non-Interactive)          │
│   claude -p --dangerously-skip-permission│
└──────────────┬──────────────────────────┘
               │
               │ Makes API calls
               ▼
┌─────────────────────────────────────────┐
│   Anthropic API                          │
│   (Claude Model)                         │
└──────────────┬──────────────────────────┘
               │
               │ Returns responses
               ▼
┌─────────────────────────────────────────┐
│   Process Results                        │
│   (Parse, Store, Continue)               │
└─────────────────────────────────────────┘
```

---

## Questions to Clarify

### About Local Implementation

1. **Project Structure**
   - ローカルプロジェクトのディレクトリ構造は？
   - どのファイルが API 呼び出しを管理している？

2. **API Integration**
   - `anthropic` Python SDK を使っている？
   - それとも直接 HTTP リクエスト？

3. **Tool Result Handling**
   - tool_result をどのように user メッセージに埋め込んでいる？
   - ループの終了条件は？

4. **Non-Interactive Mode**
   - `claude -p` に渡すプロンプトファイルはどう生成している？
   - 結果はどう受け取っている？（ファイル？標準出力？）

### About Integration Goals

5. **このリポジトリとの関係**
   - ローカル実装をこのリポジトリにマージしたい？
   - それとも別々に保つ？

6. **Use Case**
   - `CodexRunner` を非対話モードで動かしたい？
   - それとも完全に別の用途？

---

## Possible Implementation Approaches

### Approach A: Add Method 1 to This Repository
このリポジトリに方法1の実装を追加する

**Pros**:
- 統一されたコードベース
- メンテナンスしやすい

**Cons**:
- 既存の `CodexRunner` との統合が必要

### Approach B: Keep Separate Projects
ローカルとこのリポジトリを別々に保つ

**Pros**:
- 独立性が高い
- 異なる用途に最適化できる

**Cons**:
- コードの重複
- 一貫性の維持が困難

### Approach C: Create Shared Library
共通のライブラリを作る

**Pros**:
- 再利用性が高い
- 両方のプロジェクトで使える

**Cons**:
- 初期設定のコスト

---

## Next Steps

1. **ローカル実装の詳細を確認**
   - コード例を見せてもらう
   - API 呼び出し部分を理解する

2. **ワークフローを明確化**
   - 非対話モードでのフロー図を完成させる
   - tool_result の扱い方を具体化

3. **統合戦略を決定**
   - このリポジトリに追加するか
   - 別プロジェクトとして保つか
   - 共通ライブラリを作るか

4. **実装計画を立てる**
   - 必要なファイル・クラスを設計
   - テスト戦略を考える

---

## Code Skeleton (Method 1 Example)

```python
# 方法1の実装イメージ
import anthropic

def run_with_tool_results_in_user_message():
    client = anthropic.Anthropic(api_key="...")

    messages = [
        {"role": "user", "content": "Initial prompt"}
    ]

    while True:
        # API call
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=messages,
            max_tokens=4096,
            tools=[...]  # tool definitions
        )

        # Check if done
        if response.stop_reason != "tool_use":
            break

        # Extract tool uses
        tool_results = []
        for content in response.content:
            if content.type == "tool_use":
                # Execute tool
                result = execute_tool(content.name, content.input)
                tool_results.append({
                    "tool_use_id": content.id,
                    "content": result
                })

        # METHOD 1: Add tool results to next user message
        next_user_message = {
            "role": "user",
            "content": format_tool_results(tool_results)
        }

        # Add assistant response to history
        messages.append({
            "role": "assistant",
            "content": response.content
        })

        # Add user message with tool results
        messages.append(next_user_message)

    return response
```

---

## Notes

- このドキュメントは理解を深めるためのワーキングドキュメント
- 必要に応じて更新・修正していく
- 最終的な実装方針が決まったら、別途設計書を作成
