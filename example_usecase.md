# HorizonCast — What problem we solve (from scratch)

This document explains the business problem in plain language, built from zero.

---

## Start from nothing: you run a thing that sells stuff

Imagine you run a small bakery. You sell croissants. Every morning you decide: **how many should I bake?**

- Bake **too few** → you sell out by 10am, people leave unhappy, you lose sales. That is a **stockout**.
- Bake **too many** → at the end of the day you throw some away. That is **waste** (same idea as “holding” inventory you did not need).

That tension is the core problem. It is not “predict tomorrow’s sales.” It is **“how much should I prepare so I balance waste vs lost sales?”** That is an **inventory / planning** problem. A number alone does not answer it.

---

## Step 1: you have history (that is the only honest input)

Say last week you sold:

| Day | Croissants sold |
|-----|-----------------|
| Mon | 40 |
| Tue | 38 |
| Wed | 42 |
| Thu | 41 |
| Fri | 55 |
| Sat | 60 |
| Sun | 45 |

You want a guess for **next Saturday**.

Naive guess: “last Saturday was 60, so 60.”  
Sometimes that works. Often it does not, because weather, events, holidays, and random noise move real demand.

So people use models (averages, trends, machine learning) to get a **better central guess**. That is useful, but it is only half the story.

---

## Step 2: the real mistake is treating one number as “the truth”

Suppose a tool says: **“Forecast for next Saturday: 52 croissants.”**

You still do not know:

- Could it easily be **70**? (busy weekend)
- Could it easily be **35**? (rain, competing event)

If you stock **52** and demand is **70**, you stock out.  
If you stock **52** and demand is **35**, you waste.

**The business problem is not “what is the single best guess?”**  
It is **“how wrong might we be, and in what direction does that hurt us?”**

Stockouts and waste do not cost the same. In your head you might think: “losing a sale hurts more than throwing one croissant.” That is exactly what **asymmetric cost** means. HorizonCast is built around that idea: not only “how much might we sell?” but **“what decision is sensible given how wrong we might be and what each kind of wrong costs?”**

---

## Step 3: what actually helps is a range you can trust, not vibes

Instead of only “52,” imagine the system says:

- **Best guess (point forecast):** 52  
- **90% prediction interval:** **40 to 68**  
  Meaning: in repeated similar situations, this kind of interval is designed to **contain the true outcome about 9 times out of 10** (that is what “90% coverage” is trying to mean in practice).

Now your decision is clearer:

- If you hate stockouts more than waste, you might stock toward the **upper** end of the range (or above it).
- If waste is expensive (perishable, strict margins), you might stock toward the **lower** end.

**The product problem we solve:** turn messy history into **(1) a good central forecast** plus **(2) an honest uncertainty band** plus **(3) a way to connect that to dollars** (holding vs stockout), so a planner (or software) can choose stock levels without pretending “52 is exact.”

---

## Step 4: tie it to money with a tiny numeric example

Suppose:

- **Holding / waste cost:** $0.10 per croissant you make but do not sell (or throw).
- **Stockout cost:** $0.50 per croissant you could have sold but did not have (lost margin, annoyed customer, etc.).

You are choosing how many to bake: call that **Q** (quantity prepared).

True demand **D** is unknown. Suppose it turns out **D = 60**.

| You bake (Q) | Sold (min(Q,D)) | Stockout (shortage) | Waste (surplus) | Cost = 0.5×shortage + 0.1×surplus |
|--------------|-----------------|----------------------|-----------------|-------------------------------------|
| 52 | 52 | 8 | 0 | 8×0.5 = **$4.00** |
| 60 | 60 | 0 | 0 | **$0.00** |
| 68 | 60 | 0 | 8 | 8×0.1 = **$0.80** |

So “the forecast said 52” is not enough: **52 was a bad operational target** if stockouts are expensive and demand was actually 60.

If the interval said “40 to 68,” a stockout-averse policy might pick **68** and pay **$0.80** instead of **$4.00** in this scenario.

That is the business lever: **better decisions under uncertainty**, not prettier charts.

---

## Step 5: what HorizonCast is, in one sentence

**HorizonCast helps organizations that sell or move physical things (or anything with volatile demand) decide how much to prepare, ship, or staff by combining demand forecasts with uncertainty and cost asymmetry—so you stop optimizing the wrong thing (only accuracy on paper) and start reducing the costs that show up in operations (stockouts vs waste).**

---

## Why “machine learning” shows up at all

Because real businesses do not have “last week’s seven numbers.” They have:

- thousands of SKUs,
- stores,
- prices,
- promotions,
- seasonality,
- missing data,

and a human cannot hold that in their head. Models (like gradient boosted trees) learn patterns from that scale. **But the reason we care about those patterns is still the bakery problem:** choose quantities under uncertainty with asymmetric costs.

---

## Summary

| Without this framing | With it |
|----------------------|--------|
| One number (“52”) | Point forecast **plus** an uncertainty band |
| Optimize only for “accuracy” | Connect forecasts to **holding vs stockout** dollars |
| Planner overrides the model | Intervals support **defensible** stock targets |

This file is a standalone explanation of the **use case**; it does not replace technical or API documentation elsewhere in the repo.
