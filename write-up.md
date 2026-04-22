# Write-Up: Daily Reflection Tree — Design Rationale

**Assignment:** DT Fellowship — Daily Reflection Tree  
**Author:** Candidate Submission  
**Date:** April 2026

---

## 1. Why These Questions

The hardest design constraint was this: every question must have fixed options that a real person at 7pm — tired, distracted, possibly defensive — would find honest. Options that are too obviously "good" produce self-congratulatory selections. Options that are too clinical produce confused ones.

**The weather metaphor (A1_OPEN)** is not decorative. It's a known technique in therapeutic interviewing called *externalizing*: instead of asking "how did you feel?", we ask the person to describe the day as if it were an object. This reduces defensiveness. "Stormy" is easier to admit than "I felt like a victim." The metaphor also communicates immediately to the decision node — stormy/overcast maps cleanly to external locus signals without the employee ever seeing the word "locus."

**The setback question (A1_Q_SETBACK_*)** is the crux of Axis 1. Rotter's original locus of control scale (1954) focused not on success attribution but on failure attribution — specifically whether people locate the cause of negative outcomes inside or outside themselves. I designed this question as two versions (INT/EXT) that are surfaced differently based on the prior routing — so both types of employees get a question calibrated to their already-revealed tendency.

**The "unglamorous work" framing (A2_Q_CONTRIB)** is deliberate. Organ's Organizational Citizenship Behavior literature (1988) is specific: OCB is discretionary effort that *goes beyond formal requirements*. If I asked "did you work hard today?", everyone would say yes. The specific frame of "wasn't required" forces the employee to consider whether they gave beyond their job description.

**The "score-keeping" question (A2_Q_ENTITLE)** uses Campbell et al.'s insight that entitlement is invisible to its holder — it feels like fairness-seeking. So rather than asking "were you entitled?", the question asks about the *scoreboard*: were you keeping one? That's close enough to the phenomenon that people who don't have this pattern won't recognize themselves in it.

**The radius question (A3_OPEN)** uses the visual framing of a "frame" to invoke perspective-taking naturally. Batson's 2011 work on empathy distinguishes cognitive perspective-taking (imagining another's view) from affective empathy. I chose cognitive — "who is in the frame" — because it's actionable in a single day's reflection. Affective empathy is harder to surface in a survey-style tool.

---

## 2. How I Designed the Branching

### The Core Trade-Off: Depth vs. Completion Rate

A more granular tree would produce better personalization. But a reflection tool used at the end of a tiring day faces a hard user-experience constraint: if it takes more than 8 minutes, people abandon it. I designed for a 4-question path, which tests at approximately 5-7 minutes in pilot walkthroughs.

The key branching philosophy: **branch on signal, not on content.** Each decision node routes on whether the previous answer indicated internal or external locus (Axis 1), contribution or entitlement (Axis 2), self or other orientation (Axis 3). The employee never sees this classification. They just experience a question that feels slightly more relevant to what they said earlier.

### The Interpolation Strategy

Reflection and question nodes use `{node_id.answer}` interpolation deliberately. When a reflection node says "You described today as '{A1_OPEN.answer}'", it creates a micro-mirror effect — the employee hears their own word reflected back before receiving an insight. This is a technique from Motivational Interviewing (Miller & Rollnick) called *reflective listening* — which increases the likelihood that the insight lands, because it's grounded in the person's own framing.

### What I Traded Off

I chose not to build recursive sub-branches within each axis (e.g., 3-deep question chains for each detected signal). This would have required 50+ nodes and would likely exceed usable session length. Instead, I front-loaded the opening question as a "first filter" and used the second question within each axis to add nuance.

I also chose not to include per-question signal accumulation except where it was meaningful for branching. The summary node uses a composite key (`axis1.dominant + axis2.dominant + axis3.dominant`) to select from 8 pre-written insights — rather than dynamic assembly — to preserve the "no LLM" constraint.

---

## 3. Psychological Sources

| Axis | Primary Source | What I Used |
|------|---------------|-------------|
| Axis 1: Locus | Rotter (1954), *Social Learning and Clinical Psychology* | Internal vs. external locus classification; failure attribution as the key diagnostic |
| Axis 1: Mindset | Dweck (2006), *Mindset: The New Psychology of Success* | Effort vs. fixed-talent framing in success attribution options |
| Axis 2: Entitlement | Campbell, Bonacci, et al. (2004), *Psychological Entitlement: Interpersonal Consequences and Validation of a New Self-Report Measure* | The "scoreboard" framing for entitlement as invisible fairness-seeking |
| Axis 2: OCB | Organ (1988), *Organizational Citizenship Behavior: The Good Soldier Syndrome* | Definition of discretionary effort beyond formal requirements |
| Axis 3: Transcendence | Maslow (1969), *The Farther Reaches of Human Nature* | Self-transcendence as the healthy apex of development; "what does the situation need from me?" |
| Axis 3: Perspective-taking | Batson (2011), *Altruism in Humans* | Cognitive perspective-taking as the actionable form of empathy in daily work |
| Branching design | Miller & Rollnick (2012), *Motivational Interviewing, 3rd Ed.* | Reflective listening, externalizing language, non-shaming reframes |

---

## 4. What I'd Improve With More Time

**1. A "Carry-Forward" Question.** The current tree ends after 3 axes and a summary. A fourth node — "What's one thing you'll do differently tomorrow?" with fixed options specific to the user's axis profile — would close the loop from reflection to action. Without it, the tool risks becoming therapeutic without being developmental.

**2. Weekly Pattern Detection.** If signals are stored per-session, a simple aggregation layer (no LLM needed — just tallies) could surface patterns like "you've been on the external side of Axis 1 four days this week" and offer a targeted question variant on the fifth day. This requires persistent state, not AI.

**3. Non-Binary Signal Scoring.** Currently, options are routed as either INT or EXT. A weighted scoring system (e.g., some options score 0.5 for internal rather than binary 0/1) would produce more nuanced routing and reduce false categorization from single-answer anomalies. Still fully deterministic — just more gradient.

**4. Axis Sequence Adaption Based on Week Context.** Monday reflections might need a different Axis 1 opening than Friday reflections. The *content* of the day varies by week position in ways that affect the optimal question sequence. A date-aware opener (still deterministic — just conditional on day-of-week) would make the tool feel more contextually alive.

---

*The tree is the product. This write-up is the trace of how it was built.*
