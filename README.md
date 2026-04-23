# Professional-Quant Skill

A professional quantitative trading skill for AI agents. Deep analysis, decisive signals, no disclaimers.

**Always uses current date automatically** (datetime.now()) - never hallucinates dates.

---

## Install

Copy-paste this prompt into **any AI agent** (OpenCode, kilo code, Codex, etc.) to install the skill:

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

## Update

When you make changes to the repo, users can update with one command:
```bash
# Option 1: Run the update script (easiest)
~/.agents/skills/professional-quant/update-skill.sh

# Option 2: Direct git pull
cd ~/.agents/skills/professional-quant && git pull

# Option 3: Re-install fresh (if issues)
git clone https://github.com/Timmy6942025/professional-quant.git ~/.agents/skills/professional-quant --force
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
