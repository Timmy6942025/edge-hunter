# Professional-Quant Skill

Copy-paste this prompt into **any AI agent** (OpenCode, Claude, GPT, etc.) to install the skill:

```
Clone the professional-quant skill from https://github.com/Timmy6942025/professional-quant and set it up in my .agents directory so it works immediately.

Steps:
1. git clone https://github.com/Timmy6942025/professional-quant.git ~/.agents/skills/professional-quant
2. pip3 install --break-system-packages yfinance vectorbt prophet PyPortfolioOpt numpy pandas
3. Confirm the skill is installed by checking if ~/.agents/skills/professional-quant/SKILL.md exists.

Then tell me "Skill installed. Ready for deep quant analysis."
```

**OpenCode users** can also run:
```bash
opencode install professional-quant
```

---

## After Installation

Ask your agent:
```
Analyze AAPL stock and tell me if I should invest.
```

The agent will automatically use the skill to produce 500+ words of deep analysis with decisive BUY/SELL/HOLD verdict, confidence level, and entry/exit levels. No disclaimers.

## Repository
https://github.com/Timmy6942025/professional-quant
