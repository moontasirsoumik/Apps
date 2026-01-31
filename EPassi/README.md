# EPassi Lunch Payment Optimizer

A responsive single-page web app that optimizes how you split a lunch payment into the best set of EPassi taps plus any remainder on your personal card. It maximizes your employer's contribution while respecting EPassi rules and your remaining limits.

## What it does

**Input:**
- **Meal total (€)** *(required)* — the amount you need to pay
- **Remaining EPassi benefit (€)** *(optional)* — your available EPassi balance; defaults to €294 if empty
- **Remaining EPassi taps** *(optional)* — the number of taps you have left

**Output:**
- **Payment plan summary** — company contribution, salary deduction, personal card amount, taps used
- **Optional remaining cards** — remaining balance and remaining taps (shown only if you provide both limits)
- **Payment steps list** — clickable cards for each EPassi tap and personal card payment; mark each **Done** as you complete it

## How the algorithm works

The app uses **dynamic programming** to find the globally optimal payment plan:

1. **Valid tap values** are €8.90 to €14.00 in €0.10 increments (51 options: 890, 900, 910, ..., 1400 cents)
2. **Benefit calculation** per tap:
   - If tap ≥ €11.50: company pays 25% (rounded down), you pay the rest via salary deduction
   - If tap < €11.50: company pays €8.80, you pay the rest via salary deduction (if positive)
3. **Algorithm:**
   - Build a DP table where `dp[s]` = best plan to spend exactly `s` cents on EPassi
   - For each spending amount, try all valid tap values and keep the best result
   - Explore all achievable spend totals and their corresponding personal card remainders
   - Select the globally best plan across all options

4. **Optimization criteria** (in order):
   - **Maximize company contribution** (most important)
   - If tied: **minimize salary deduction**
   - If tied: **minimize number of taps**
   - If tied: **minimize personal card amount**

5. **Consolidation rule:**
   - If the result includes a tiny personal card charge (<€0.14) and an EPassi tap under €14.00, the app automatically merges the personal amount into that tap to eliminate absurd micro-payments

**Result:** The algorithm guarantees the best possible financial outcome for you.

## Rules and constraints

- Valid tap range: **€8.90 to €14.00** in **€0.10 increments** (51 possible values)
- Total EPassi spend ≤ **min(meal total, remaining benefit)**
- Number of taps ≤ **remaining taps** (if provided)
- Any unspent meal amount must be covered by **personal card**
- Remaining balance and taps are **never shown as negative** (clamped to ≥ 0)

## UI behavior

### Desktop (≥981px)
- **Left column:** Inputs card + Payment plan card (animated slide-in from left)
- **Right column:** Payment steps card (animated slide-in from right)
- Sticky topbar stays visible while scrolling content
- Columns animated in with smooth easing on page load

### Mobile (<981px)
- Sections stack vertically
- Page scrolls normally; topbar remains sticky at the top
- No horizontal scroll even when focusing on inputs
- Content fits the device width
- No column animations on mobile (instant load for better UX)

### Interactions
- **Swipe left on any step card** to mark it **Done** → smooth animation, card fades and moves to bottom
- **Mouse drag on desktop** also works as an alternative to swipe for marking cards done
- Visual drag indicator shows swipe progress in real-time
- **Reset done** button appears (only when ≥1 step is marked done) — clears all done marks
- **Clear plan** clears the plan and returns to initial input state
- All animations use smooth easing curves (cubic-bezier) for premium feel
- **Dark & Light mode support** — automatically adapts to system color preference

### Animation details
- **Card reordering:** 450ms smooth transition when done cards move to bottom
- **Column slide-in (desktop):** 800ms easing when page first loads
- **Color scheme:** Automatic dark/light mode based on system preference

## Project files

- `index.html` — HTML structure + template definitions
- `styles.css` — responsive design, dark/light mode support, animations
- `app.js` — DP optimization algorithm, rendering, event handling

## How to use

1. **Open** `index.html` in any modern web browser
2. **Enter meal total** (required) — the amount you need to pay
3. **Optionally enter:**
   - Remaining EPassi benefit (€) — leave blank to default to €294
   - Remaining EPassi taps — leave blank for unlimited taps
4. **Click Optimize** to compute the best payment plan
5. **Review the plan:**
   - Company contribution (how much your employer pays)
   - Salary deduction (amount from your taxed salary)
   - Personal card charge (your out-of-pocket payment)
   - Remaining balance & taps (if both were provided)
6. **Follow the payment steps:**
   - Use each EPassi tap in order
   - Pay the personal card amount (if shown)
   - Tap each step card as you complete it
7. **Start over:** Use **Clear plan** or enter new values and **Optimize** again

### Example scenario

- Meal costs **€23.33**
- You have **€294 remaining EPassi benefit**
- You have **20 remaining taps**

**Optimal result:** €11.50 + €11.80 
- Company pays: ~€6.57
- Salary deduction: ~€17.13
- Personal card: €0 
- Taps used: 2

## Technical notes

- **No data persistence** — plans are computed on-the-fly; refresh clears everything
- **Browser support** — works on all modern browsers (Chrome, Firefox, Safari, Edge)
- **Performance** — DP algorithm computes instantly even for €3000+ meals
