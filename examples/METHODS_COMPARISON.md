# Method 1 vs Method 2: 実装比較

## 核心的な違い

### Method 1: tool_result を user メッセージのテキストに含める

```python
# Tool results を文字列としてフォーマット
tool_results_message = """
Tool execution results:

Tool Use ID: toolu_abc123
Result:
Execution successful: 4
------------------------------------------------------------

Please continue based on these results.
"""

# User message に追加
messages.append({
    "role": "user",
    "content": tool_results_message  # <- 文字列
})
```

**メッセージ履歴の例**:
```python
[
    {"role": "user", "content": "Calculate 2+2"},
    {"role": "assistant", "content": [
        {"type": "text", "text": "I'll calculate that."},
        {"type": "tool_use", "id": "toolu_abc123", "name": "execute_python", "input": {...}}
    ]},
    {"role": "user", "content": "Tool execution results:\n\nTool Use ID: toolu_abc123\nResult:\n4\n..."},
    # ...
]
```

---

### Method 2: tool_result を API の標準形式で送る

```python
# Tool results を content blocks としてフォーマット
tool_result_content = [
    {
        "type": "tool_result",
        "tool_use_id": "toolu_abc123",
        "content": "Execution successful: 4"
    }
]

# User message に追加
messages.append({
    "role": "user",
    "content": tool_result_content  # <- リスト of content blocks
})
```

**メッセージ履歴の例**:
```python
[
    {"role": "user", "content": "Calculate 2+2"},
    {"role": "assistant", "content": [
        {"type": "text", "text": "I'll calculate that."},
        {"type": "tool_use", "id": "toolu_abc123", "name": "execute_python", "input": {...}}
    ]},
    {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "toolu_abc123", "content": "4"}
    ]},
    # ...
]
```

---

## 詳細比較

| 項目 | Method 1 | Method 2 |
|------|----------|----------|
| **tool_result の形式** | 文字列（テキスト） | Content block (type: "tool_result") |
| **API 理解** | Claude は文脈から推測 | Claude は構造的に理解 |
| **公式推奨** | ❌ 非標準 | ✅ 公式推奨 |
| **実装の複雑さ** | シンプル | 若干複雑（content block 構造） |
| **デバッグ** | テキストベースで読みやすい | 構造化されているが見づらい |
| **非対話モードとの相性** | 良い（テキストのみ） | やや複雑（JSON構造） |
| **将来の互換性** | 不明（非公式なので） | 安定（公式なので） |

---

## どちらを使うべきか？

### Method 1 を使うケース

✅ **非対話モードでのスクリプト自動化**
- `claude -p` でプロンプトファイルを処理
- テキストベースのやり取りがシンプル

✅ **プロトタイピング・実験**
- 素早く試したい
- 複雑な構造は不要

✅ **既存のテキストベースシステムとの統合**
- ログやメッセージが全てテキスト
- 構造化データの扱いが難しい環境

⚠️ **注意点**:
- Claude が tool_result を正しく認識できない可能性
- 将来のAPI変更で動かなくなる可能性
- 複数の tool_use が同時にある場合、混乱する可能性

---

### Method 2 を使うケース

✅ **本番環境・長期運用**
- 公式サポートあり
- API変更に強い

✅ **複雑な tool 使用**
- 複数の tool を同時に使う
- tool の結果が大きい・複雑

✅ **Anthropic の他の機能との統合**
- Streaming
- Vision
- その他の advanced features

⚠️ **注意点**:
- 非対話モードでの実装が若干複雑
- JSON構造の管理が必要

---

## 実行例の比較

### セットアップ

```bash
# Install dependencies
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY="your-key-here"
```

### Method 1 実行

```bash
cd /home/user/test/examples
python method1_tool_result_in_user.py
```

**予想される出力**:
```
======================================================================
Iteration 1
======================================================================
Calling Claude API...
Stop reason: tool_use

Executing tools...
  - Tool: execute_python
    Input: {
  "code": "2 + 2"
}
    Result: Execution successful: 4...

Added tool results to user message

======================================================================
Iteration 2
======================================================================
Calling Claude API...
Stop reason: tool_use

Executing tools...
  - Tool: read_file
    Input: {
  "path": "README.md"
}
    Result: # MV Orchestra v2.8...

Added tool results to user message

======================================================================
Iteration 3
======================================================================
Calling Claude API...
Stop reason: end_turn
Conversation complete (end_turn)
```

### Method 2 実行

```bash
cd /home/user/test/examples
python method2_tool_result_as_system.py
```

**予想される出力**: （ほぼ同じだが、メッセージ構造が異なる）
```
======================================================================
Iteration 1
======================================================================
Calling Claude API...
Stop reason: tool_use

Executing tools...
  - Tool: execute_python
    Input: {
  "code": "2 + 2"
}
    Result: Execution successful: 4...

Added 1 tool_result blocks to user message

======================================================================
Iteration 2
======================================================================
...
```

---

## メッセージ履歴の完全な例

### Method 1 のメッセージ履歴

```json
[
  {
    "role": "user",
    "content": "Calculate 2+2 using Python, then read README.md"
  },
  {
    "role": "assistant",
    "content": [
      {"type": "text", "text": "I'll calculate that for you."},
      {
        "type": "tool_use",
        "id": "toolu_123",
        "name": "execute_python",
        "input": {"code": "2 + 2"}
      }
    ]
  },
  {
    "role": "user",
    "content": "Tool execution results:\n\nTool Use ID: toolu_123\nResult:\nExecution successful: 4\n------------------------------------------------------------\n\nPlease continue based on these results."
  },
  {
    "role": "assistant",
    "content": [
      {"type": "text", "text": "Great! Now I'll read the README."},
      {
        "type": "tool_use",
        "id": "toolu_456",
        "name": "read_file",
        "input": {"path": "README.md"}
      }
    ]
  },
  {
    "role": "user",
    "content": "Tool execution results:\n\nTool Use ID: toolu_456\nResult:\n# MV Orchestra v2.8...\n------------------------------------------------------------\n\nPlease continue based on these results."
  },
  {
    "role": "assistant",
    "content": [
      {"type": "text", "text": "Perfect! I've completed both tasks. 2+2 equals 4, and I've read the README which describes..."}
    ]
  }
]
```

### Method 2 のメッセージ履歴

```json
[
  {
    "role": "user",
    "content": "Calculate 2+2 using Python, then read README.md"
  },
  {
    "role": "assistant",
    "content": [
      {"type": "text", "text": "I'll calculate that for you."},
      {
        "type": "tool_use",
        "id": "toolu_123",
        "name": "execute_python",
        "input": {"code": "2 + 2"}
      }
    ]
  },
  {
    "role": "user",
    "content": [
      {
        "type": "tool_result",
        "tool_use_id": "toolu_123",
        "content": "Execution successful: 4"
      }
    ]
  },
  {
    "role": "assistant",
    "content": [
      {"type": "text", "text": "Great! Now I'll read the README."},
      {
        "type": "tool_use",
        "id": "toolu_456",
        "name": "read_file",
        "input": {"path": "README.md"}
      }
    ]
  },
  {
    "role": "user",
    "content": [
      {
        "type": "tool_result",
        "tool_use_id": "toolu_456",
        "content": "# MV Orchestra v2.8..."
      }
    ]
  },
  {
    "role": "assistant",
    "content": [
      {"type": "text", "text": "Perfect! I've completed both tasks. 2+2 equals 4, and I've read the README which describes..."}
    ]
  }
]
```

---

## 非対話モードでの使用

### Method 1 + claude -p

```bash
# プロンプトファイルを作成
cat > prompt.txt << 'EOF'
You are an AI assistant that can execute Python code and read files.

Available tools:
- execute_python: Execute Python code
- read_file: Read a file

Please calculate 2+2 using Python.
EOF

# 実行（非対話モード）
claude -p prompt.txt --dangerously-skip-permission
```

Method 1 の方がテキストベースなので、非対話モードと相性が良い

### Method 2 + claude -p

Method 2 でも使えるが、tool_result の構造化データを扱うのが若干複雑

---

## まとめ

- **Method 1**: シンプル、非対話モード向き、非公式
- **Method 2**: 標準的、本番環境向き、公式推奨

あなたのローカル実装が Method 1 を使っているなら、それは **非対話モードとの相性の良さ** が理由として大きいと思われます。

ただし、長期的には **Method 2 への移行** も検討すべきかもしれません。

---

## 次のステップ

1. **ローカルの実装を確認**
   - どちらの方法を使っているか
   - 非対話モードでどう動いているか

2. **このリポジトリへの統合を検討**
   - `CodexRunner` に Method 1/2 のサポートを追加？
   - 別のクラスとして実装？

3. **テスト・検証**
   - 両方の方法で動作確認
   - パフォーマンス・安定性の比較
