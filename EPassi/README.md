# EPassi Lunch Payment Optimizer

A responsive single-page web app that helps you split a lunch payment into the best set of EPassi taps (and any remainder on your personal card) to maximize the employer contribution while respecting EPassi tap rules and your remaining limits.

## What it does

You enter:

* **Meal total (€)** (required)
* **Remaining EPassi benefit (€)** (optional; defaults to **€294** if empty)
* **Remaining EPassi taps** (optional)

Then the app generates:

* A **Payment plan summary** (company contribution, salary deduction, personal card, taps used)
* Optional **Remaining after this** cards (remaining balance + remaining taps) if both limits were provided
* A **Payment steps** list as tappable cards you can mark **Done** (done items move to the bottom)

## Rules and constraints

* Valid tap values are generated in **€0.10 increments** from **€8.90 to €14.00**
* Total EPassi spend cannot exceed **min(meal total, remaining benefit)**
* If you provide remaining taps, the plan will use **no more than that number of taps**
* Any leftover meal amount is paid using a **personal card**
* Remaining balance and remaining taps are **never shown as negative** (clamped to 0)

## How optimization works

The optimizer searches all valid tap combinations (within the limits) and picks the best plan using this priority:

1. **Maximize total company contribution**
2. If tied: **minimize total salary deduction**
3. If tied: **minimize number of taps**
4. If tied: **minimize personal card remainder**

It uses **dynamic programming** to guarantee the globally best result under the constraints.

## UI behavior

* **Desktop layout:** Inputs + Plan on the left, Steps on the right
  The **Steps card matches the combined height** of Inputs + Plan (Steps scrolls internally only when needed on desktop).
* **Mobile layout:** Sections stack vertically; **only the page scrolls**.
* Tap any step card to mark it **Done** → it fades and moves to the bottom.
* **Reset done** appears only after at least one step is marked done.
* **Clear plan** clears the current plan and returns to the initial state.

## Project files

* `index.html` — structure + templates
* `styles.css` — styling, layout, responsive behavior
* `app.js` — optimization logic + rendering + interactions

## How to use

1. Open `index.html` in a browser.
2. Enter your **Meal total**.
3. Optionally enter **Remaining benefit** and **Remaining taps**.
4. Click **Optimize**.
5. Follow **Payment steps**, tapping each as you complete it.
6. Use **Reset done** (only when needed) or **Clear plan** to start over.

## Notes

* Plans are computed fresh each time; no data is stored or synced automatically.
* If you want persistence (remembering the last plan and done states), that can be added with localStorage later.
