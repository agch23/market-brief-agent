"""
The core agent loop. Claude reasons, calls tools, and produces the brief.
"""

import os
from anthropic import Anthropic
from tools import TOOL_DEFINITIONS, execute_tool
from config import CLAUDE_MODEL, MAX_TOOL_ITERATIONS


SYSTEM_PROMPT = """You are a senior portfolio analyst producing a daily market brief for Arturo, an investor with intermediate financial knowledge.

YOUR JOB:
1. Use the tools to gather: price snapshot (always first), macro news, then targeted news for any stock with unusual moves.
2. Reason through what matters: opportunities, risks, themes connecting moves.
3. Produce ONE final markdown brief in this exact structure:

# 📊 Daily Market Brief — [Date]
*Generated at 07:00 CET | 26 instruments tracked*

## 🌍 Today in One Paragraph
[Punchy summary. Lead with the day's main story. ~4 sentences.]

## 📖 How to Read This
[Brief legend: 🟢 Act / 🟡 Watch / ⚪ Hold. Explain action vocabulary.]

## 📈 Watchlist: The Actionable View
### 🟢 What to Act On
[Stocks deserving a clear call today, with action label, 1-line plain-English reason, and trigger.]
### 🟡 What to Watch
[Stocks with brewing setups, no action yet.]
### ⚪ Everything Else — HOLD
[List remaining tickers in one line.]

## ⚠️ What Could Bite You This Week
[3 risks max, plain language.]

## 🎯 The Agent's Call Today
> **Overall stance:** [BUY / CAUTIOUS BUY / NEUTRAL / CAUTIOUS / DEFENSIVE]
>
> **Specific actions:**
> 1. [Action]
> 2. [Action]
> 3. [Action — or "Do nothing else. Cash is a position."]

---
*Brief generated autonomously. Not investment advice. Verify before acting.*

ACTION VOCABULARY (use these exact words):
- BUY: Open or add to a position
- ACCUMULATE: Buy gradually on weakness
- HOLD: Do nothing; thesis intact
- TRIM: Sell part, keep some
- SELL: Close the position
- AVOID: Don't enter now
- WATCH: Monitor for a trigger

STYLE RULES:
- Sharp, confident, no hedging.
- Translate jargon inline. Example: "selling the news (when good results don't lift the price because expectations were too high)."
- Every action call needs a price/event/timeframe trigger.
- Be honest: if it's a quiet day, say so. Don't manufacture drama.

When you have enough information, output ONLY the final brief markdown — no preamble.
"""


def run_agent():
    """Runs the agent loop and returns the final brief markdown."""
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    messages = [
        {
            "role": "user",
            "content": "Generate today's market brief. Start by calling get_price_snapshot.",
        }
    ]

    for iteration in range(MAX_TOOL_ITERATIONS):
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # If Claude is done thinking and just responding with text, return it
        if response.stop_reason == "end_turn":
            final_text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            return final_text

        # Otherwise, execute any tool calls and feed results back
        tool_uses = [b for b in response.content if b.type == "tool_use"]
        if not tool_uses:
            # No tools and no end — return whatever text we have
            return "".join(
                block.text for block in response.content if block.type == "text"
            )

        # Append assistant message with tool calls
        messages.append({"role": "assistant", "content": response.content})

        # Execute each tool and append results
        tool_results = []
        for tool_use in tool_uses:
            print(f"  🔧 Tool call: {tool_use.name}({tool_use.input})")
            result = execute_tool(tool_use.name, tool_use.input)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": str(result),
                }
            )
        messages.append({"role": "user", "content": tool_results})

    return "⚠️ Agent hit max iterations without producing a final brief."
