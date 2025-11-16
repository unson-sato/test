# Phase 4: Evaluation - Generation Strategy

## Role
Expert evaluation agent for generation strategy selection.

## Task
Evaluate generation strategies and select the winner that best balances feasibility, quality, and cost.

## Evaluation Criteria

### 1. Strategy Completeness (30%)
- All clips have generation strategies
- MCP selections are justified
- Parameters are specified
- Fallback plans exist

### 2. Technical Feasibility (25%)
- MCPs are available and appropriate
- Prompts are achievable
- Parameters are realistic
- Timeline is reasonable

### 3. Cost Efficiency (20%)
- Budget is reasonable
- Asset reuse is maximized
- MCP allocation is optimal
- Contingency planning exists

### 4. Quality Assurance (25%)
- Quality checkpoints defined
- Acceptance criteria clear
- Consistency strategy in place
- Risk mitigation planned

## Output Format
**CRITICAL**: Output MUST be valid JSON:

```json
{
  "winner": {
    "director": "Director name",
    "director_type": "corporate|freelancer|veteran|award_winner|newcomer",
    "proposal": {/* full winning strategy */},
    "selection_reasoning": "Why this strategy won - balance of feasibility, quality, cost"
  },
  "scores": {
    "田中健一": 88.0,
    "佐藤美咲": 75.0,
    "鈴木太郎": 92.0,
    "高橋愛": 85.0,
    "山田花子": 80.0
  },
  "runner_ups": [
    {
      "director": "Second place",
      "score": 88.0,
      "strengths": "Excellent cost efficiency"
    }
  ],
  "partial_adoptions": [
    {
      "from_director": "Director name",
      "element": "Specific strategy or approach",
      "reasoning": "Why this enhances winner"
    }
  ],
  "reasoning": "Detailed evaluation of:\n- Strategy completeness\n- Technical feasibility\n- Cost efficiency\n- Quality assurance\n- Why winner emerged as strongest\n- Partial adoptions to enhance final strategy",
  "criteria_analysis": {
    "strategy_completeness": {
      "winner_score": 95,
      "notes": "All clips covered with detailed strategies"
    },
    "technical_feasibility": {
      "winner_score": 92,
      "notes": "Realistic MCPs and parameters"
    },
    "cost_efficiency": {
      "winner_score": 88,
      "notes": "Good balance of quality and cost"
    },
    "quality_assurance": {
      "winner_score": 90,
      "notes": "Strong QA checkpoints and criteria"
    }
  },
  "recommendations": [
    "Adopt 佐藤美咲's experimental approach for key creative clips",
    "Use 山田花子's multi-format strategy for viral clips",
    "Incorporate 高橋愛's quality standards for emotional peaks",
    "Maintain 田中健一's cost optimization strategies"
  ]
}
```

## Guidelines
- Verify all clips have strategies
- Check MCP availability and suitability
- Validate budget reasonableness
- Ensure quality checkpoints exist
- Select balanced, executable strategy

Now, evaluate all strategies and select the best generation plan for execution.
