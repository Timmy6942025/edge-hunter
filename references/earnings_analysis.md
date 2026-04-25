# Earnings Analysis

## Purpose

Earnings calls are the highest-signal research event for equities. Management has legal obligations to be truthful — but they optimize for narrative as much as accuracy. Your job is to extract the signal from the noise: what's genuinely bullish, what's management spin, and what's a red flag that changes the thesis.

This file integrates into **Step 4 (Targeted Research)** of the reasoning loop. Run `earnings_transcript.py` first, then apply this framework to interpret what you find.

---

## What to Extract from the Call

### 1. Revenue Beat/Miss + Guidance Surprise

The two numbers that move stocks most: did they beat, and what's the forward guide?

| Signal | Interpretation |
|--------|---------------|
| Beat Q/Q guide, raise full-year | Bullish — execution + confidence |
| Beat Q/Q guide, maintain full-year | Neutral — okay but not confident enough to raise |
| Miss Q/Q guide, raise full-year | Watch — short-term miss but long-term confidence |
| Miss Q/Q guide, lower full-year | Bearish — guidance deterioration |

**Key question**: Is the beat/miss a one-time item (cookie-jar reserve) or a genuine structural beat? Check if gross margin expanded alongside revenue — that's real. Revenue beat with margin compression is suspicious.

### 2. Non-GAAP vs GAAP Reconciliation

Companies want you to focus on Non-GAAP (adjusted) earnings because it's always higher. The gap between Non-GAAP and GAAP tells you how much they're hiding in one-time items.

**Red flags**:
- Stock-based compensation (SBC) growing faster than revenue — they're printing earnings with equity
- Large restructuring charges recurring every quarter — not one-time
- Acquisition amortization being added back — they're using M&A to inflate earnings
- Normalized EPS declining while adjusted EPS rises — the gap is growing, not shrinking

**The rule**: If Non-GAAP is rising but GAAP is falling or flat, the company's adjusted earnings are increasingly detached from reality.

### 3. Gross Margin Trajectory

Margin is the single most important long-term driver of equity value. It tells you whether the business has pricing power, operating leverage, or is under cost pressure.

**What to look for**:
- Gross margin expansion without revenue growth = operating leverage (best-case)
- Gross margin compression = cost pressure, pricing power loss, or mix shift to lower-margin products
- Sequential margin trend: 2+ quarters of margin decline is a trend, not noise
- Guidance: are they guiding margin up or down? This is more important than revenue guidance.

**Example**: Amazon's AWS margin improved from ~25% to ~35% over 3 years — that margin expansion drove the stock more than revenue growth.

### 4. Free Cash Flow (FCF) Quality

Earnings can be manipulated. FCF cannot. It's cash actually generated — harder to game.

**What to look for**:
- FCF > Net Income = high quality (they're converting earnings to cash)
- FCF < Net Income = earnings quality issue (accrual-based accounting inflating profits)
- FCF margin trend: is it expanding or compressing?
- Capital expenditure guidance: are they investing for growth or cutting capex to protect margins?
- Working capital changes: inventory build ahead of demand is bullish; inventory accumulation without revenue is a warning

### 5. Segment Performance Breakdown

For diversified companies, overall numbers can hide divisional deterioration. Find the segments.

**What to look for**:
- Which segment is driving results? Is it the core business or a one-time benefit?
- Is the highest-margin segment growing faster than lower-margin segments? (Good)
- Is a formerly high-growth segment slowing? That's the key change to analyze.
- Geographic mix: is growth coming from high-margin or low-margin regions?

**Example**: Apple's Services segment growing from 15% to 25% of revenue drove a multiple re-rating even as iPhone unit sales stagnated.

### 6. Capex Signals

Capex guidance is the most underappreciated signal in earnings calls. It tells you where management thinks the growth is.

- **Raising capex**: Management sees demand — bullish for 12-18 months
- **Cutting capex during growth**: They're protecting margins at the expense of future growth — could indicate demand uncertainty
- **Capex as % of revenue**: Cyclical businesses should have stable capex ratios; rising ratios mean over-investment
- **Data center / AI capex**: Specific line items for AI infrastructure are a leading indicator of future revenue

---

## Management Tone Analysis

### Confident Language (Bullish)

- *We have a clear line of sight to...*
- *We're seeing strong demand across...*
- *We expect [X] to meaningfully contribute to...*
- *We've [hired / built / acquired] the capacity to...*
- *We won share from [specific competitor]*
- *Pricing power remains strong*
- *The pipeline is the strongest we've ever seen*

### Hedging Language (Neutral to Bearish)

- *We believe the market is...* (avoiding direct commitment)
- *We continue to monitor...* (things might get worse)
- *Broad-based* (nothing is specifically strong)
- *The macro environment remains...* (blaming external factors)
- *We remain focused on...* (no new news, status quo)
- *Subject to...* (lots of caveats = low confidence)
- *We are thoughtfully...* (indecision disguised as deliberateness)

**The hedge-to-confidence ratio**: Count hedging phrases vs. confident phrases. If hedging > confident, management's conviction is low — expect guidance to miss or be cut.

### Q&A Red Flags

Analysts on the call are trying to extract truth. Management's responses reveal what they're hiding.

**Warning responses**:
- *I wouldn't characterize it that way* — they're avoiding a specific characterization
- *I'd refer you to...* — they're deflecting rather than answering
- *That's not something we're prepared to speak to* — something is wrong and they know it
- *It's early to say* — every quarter it's early, eventually it's a pattern
- *We haven't made that decision yet* — but you should already have a plan
- *I'd be careful about that comparison* — the comparison is valid and damaging

**Good responses**:
- Specific numbers and timelines (not ranges)
- Attribution to specific customers or products
- Voluntarily offering more detail than asked
- Acknowledging problems with a clear remediation plan

---

## Earnings Manipulation Signals

### Cookie-Jar Reserves

Companies manage earnings by releasing reserves built up in prior slow periods.

**How to detect**:
- Unusually large beat vs. consensus in a quarter that's traditionally weak
- Gross margin suddenly expands despite industry headwinds
- SG&A expenses decline sharply — they built up a reserve in prior quarters
- Restructuring charges appear then disappear in adjacent quarters

### Channel Stuffing

Pushing product to distributors to hit revenue targets, which then gets returned.

**How to detect**:
- Days sales outstanding (DSO) rising while revenue is rising — they're extending credit to push product
- Inventory at distributors rising faster than end-demand (check channel checks)
- Large returns in subsequent quarters
- Deferred revenue declining (they recognized revenue they shouldn't have)

### Bill-and-Hold

Recognizing revenue for products not yet shipped or not yet accepted.

**How to detect**:
- Unusual jump in deferred revenue
- Revenue recognition in advance of contractual milestones
- Customers with extended payment terms mentioned in the 10-K
- Revenue from a small number of large, one-time contracts

### Large One-Time Items

Non-recurring charges or gains that obscure the underlying business.

**How to detect**:
- Restructuring charges in 3+ consecutive quarters — it's recurring, not one-time
- Acquisition-related amortization hidden in operating expenses
- Legal settlements that were clearly foreseeable (not actually one-time)
- Asset impairments that suggest prior overstatements

---

## How to Build a Thesis from an Earnings Call

### Step 1: What's the ONE number that matters most?

Don't try to analyze everything. Identify the single most important metric for this business at this time.

- SaaS company: ARR growth + net revenue retention
- Bank: Net interest margin + charge-off rate
- Manufacturer: Gross margin + book-to-bill ratio
- Retailer: Same-store sales + inventory turnover
- Crypto/commodity: Production growth + all-in sustaining cost

### Step 2: How did actual vs. expected compare?

Calculate the beat/miss on the key metric. Then ask: was this a real beat, or a one-time?

- Real beat: margin expansion + forward guide raise + management tone confident
- One-time beat: margin flat or compressed + guide maintained + SBC growing

### Step 3: What changed from last quarter?

The delta is more important than the absolute number.

- Guidance raised vs. maintained vs. cut
- Margin trend: improving, stable, or deteriorating
- Tone change: more or less confident than last quarter
- New information: management mentioned something they didn't last quarter

### Step 4: What would change the thesis?

Earnings calls often contain the seed of a thesis change. Look for:

- Management discussing a structural change in their competitive position
- New technology or product that changes the TAM
- Customer concentration risks they've never mentioned before
- Supply chain or input cost changes that aren't transitory
- Regulatory or legal developments

---

## Example: Good Earnings Analysis

**Ticker**: NVDA
**Context**: Q4 FY26 earnings

**The ONE number**: Data center revenue growth rate and gross margin trajectory.

**Key findings**:
- Data center revenue: $62.3B (+75% YoY) — absolute growth remains massive
- Gross margin: 73.1% (expanding) — operating leverage is real
- Hyperscaler capex guidance: AMZN $200B, GOOGL $175B — demand visibility intact
- BUT: Q1 FY27 guide of $78B implies +14.5% QoQ — aggressive and vulnerable to miss

**Management tone**: Confident on AI infrastructure demand, but unusually specific about Blackwell production yields (a sign they're managing expectations for a product issue). Hedging language around China export controls — they acknowledged it as a headwind but didn't quantify it.

**Thesis implication**: The beat was real (margin expansion, not SBC), but the guide is aggressive enough that a modest miss changes the risk/reward. The hedge on China is a watch — if it escalates, the growth rate decelerates faster than the market expects.

**What would change the mind**: Q1 revenue < $76B → growth deceleration confirmed, thesis broken. $100B+ hyperscaler capex cut → demand thesis broken.

---

## Integration with the Reasoning Loop

This file feeds **Step 4 (Targeted Research)** — after forming a thesis (Step 2) and identifying unknowns (Step 3), earnings calls are often the decisive data source for equities.

For crypto, commodities, FX, and rates: earnings calls are less relevant. Use the appropriate asset playbook instead.
