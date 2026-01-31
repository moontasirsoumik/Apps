// app.js
function calcTapEffects(amountCents) {
  if (amountCents >= 1150) {
    const companyPay = Math.floor(amountCents * 0.25);
    const salaryDeduction = amountCents - companyPay;
    return { companyPay, salaryDeduction };
  }

  const salaryDeduction = 880;
  const companyPay = Math.max(0, amountCents - salaryDeduction);
  return { companyPay, salaryDeduction };
}

function comparePlans(a, b) {
  if (a.companyPay !== b.companyPay) return a.companyPay - b.companyPay;
  if (a.salaryDeduction !== b.salaryDeduction) return b.salaryDeduction - a.salaryDeduction;
  if (a.tapCount !== b.tapCount) return b.tapCount - a.tapCount;
  return b.personalCard - a.personalCard;
}

function optimizePlan(mealCents, benefitCents, remainingTaps = Infinity) {
  const maxEpassiSpend = Math.min(mealCents, benefitCents);
  const allowedTaps = [];

  for (let amount = 890; amount <= 1400; amount += 10) allowedTaps.push(amount);

  const dp = Array(maxEpassiSpend + 1).fill(null);
  dp[0] = { companyPay: 0, salaryDeduction: 0, tapCount: 0, taps: [] };

  for (let s = 0; s <= maxEpassiSpend; s++) {
    if (dp[s] === null) continue;

    for (const tap of allowedTaps) {
      const nextS = s + tap;
      if (nextS > maxEpassiSpend) continue;
      if (dp[s].tapCount + 1 > remainingTaps) continue;

      const { companyPay, salaryDeduction } = calcTapEffects(tap);
      const candidate = {
        companyPay: dp[s].companyPay + companyPay,
        salaryDeduction: dp[s].salaryDeduction + salaryDeduction,
        tapCount: dp[s].tapCount + 1,
        taps: [...dp[s].taps, tap],
      };

      if (dp[nextS] === null || comparePlans(candidate, dp[nextS]) > 0) dp[nextS] = candidate;
    }
  }

  let bestPlan = null;

  for (let s = 0; s <= maxEpassiSpend; s++) {
    if (dp[s] === null) continue;

    const personalCard = mealCents - s;
    const plan = { ...dp[s], personalCard };

    if (bestPlan === null || comparePlans(plan, bestPlan) > 0) bestPlan = plan;
  }

  if (bestPlan && bestPlan.personalCard > 0 && bestPlan.taps.length > 0) {
    const smallestTapIndex = bestPlan.taps.reduce((minIdx, tap, i) => 
      tap < bestPlan.taps[minIdx] ? i : minIdx, 0);
    const smallestTap = bestPlan.taps[smallestTapIndex];

    if (smallestTap < 1400 && smallestTap + bestPlan.personalCard < 1400) {
      const oldTap = bestPlan.taps[smallestTapIndex];
      const newTap = oldTap + bestPlan.personalCard;
      
      const { companyPay: oldCompany, salaryDeduction: oldDeduction } = calcTapEffects(oldTap);
      const { companyPay: newCompany, salaryDeduction: newDeduction } = calcTapEffects(newTap);
      
      bestPlan.taps[smallestTapIndex] = newTap;
      bestPlan.companyPay = bestPlan.companyPay - oldCompany + newCompany;
      bestPlan.salaryDeduction = bestPlan.salaryDeduction - oldDeduction + newDeduction;
      bestPlan.personalCard = 0;
    }
  }

  return bestPlan;
}

function $(id) {
  return document.getElementById(id);
}

function money(cents) {
  return `€${(cents / 100).toFixed(2)}`;
}

function cloneTemplate(id) {
  const t = document.getElementById(id);
  return t.content.firstElementChild.cloneNode(true);
}

function updateLayoutMode() {
  const grid = $("app-grid");
  const resultsVisible = $("results-section").style.display !== "none";
  const stepsVisible = $("payment-taps-section").style.display !== "none";
  grid.classList.toggle("grid--solo", !(resultsVisible || stepsVisible));
}

function showPlanSections(show) {
  const resultsSection = $("results-section");
  const stepsSection = $("payment-taps-section");
  const leftCol = $("left-col");
  const rightCol = $("right-col");

  if (show) {
    resultsSection.style.display = "";
    stepsSection.style.display = "";
    
    // Trigger animation by setting display then forcing reflow
    leftCol.offsetHeight;
    rightCol.offsetHeight;
  } else {
    resultsSection.style.display = "none";
    stepsSection.style.display = "none";
  }
  updateLayoutMode();
}

function flipReorder(container, reorderFn) {
  if (!container) return;

  const children = Array.from(container.children);
  const first = new Map(children.map((el) => [el, el.getBoundingClientRect()]));

  reorderFn();

  for (const el of Array.from(container.children)) {
    const a = first.get(el);
    if (!a) continue;

    const b = el.getBoundingClientRect();
    const dx = a.left - b.left;
    const dy = a.top - b.top;

    if (dx || dy) {
      el.style.transform = `translate(${dx}px, ${dy}px)`;
      el.style.transition = "none";
      el.offsetHeight; // Force reflow
      el.style.transition = "transform 450ms cubic-bezier(0.4, 0, 0.2, 1), opacity 450ms cubic-bezier(0.4, 0, 0.2, 1)";
      el.style.transform = "";
    }
  }
}

function updateResetVisibility() {
  const resetBtn = $("reset-done");
  const paymentPlan = $("payment-plan");
  const anyDone = paymentPlan && paymentPlan.querySelector(".step-card.done");
  resetBtn.style.display = anyDone ? "" : "none";
}

function syncStepsHeight() {
  const left = $("left-col");
  const stepsSection = $("payment-taps-section");
  const stepsBody = $("steps-body");
  if (!left || !stepsSection || !stepsBody) return;

  const isDesktop = window.matchMedia("(min-width: 981px)").matches;
  const stepsVisible = stepsSection.style.display !== "none";
  const resultsVisible = $("results-section").style.display !== "none";

  if (!isDesktop || !stepsVisible || !resultsVisible) {
    stepsSection.style.height = "";
    stepsBody.style.maxHeight = "";
    stepsBody.style.overflow = isDesktop ? "" : "visible";
    return;
  }

  const targetH = Math.round(left.getBoundingClientRect().height);
  stepsSection.style.maxHeight = `${targetH}px`;

  const header = stepsSection.querySelector(".card__header");
  const headerH = header ? Math.round(header.getBoundingClientRect().height) : 0;
  const available = Math.max(180, targetH - headerH);

  stepsBody.style.maxHeight = `${available}px`;
  stepsBody.style.overflow = "auto";
}

function addSummaryCard(container, { label, value, sub, variantClass }) {
  const card = cloneTemplate("tpl-summary-card");
  if (variantClass) card.classList.add(variantClass);

  const labelEl = card.querySelector(".summary-card__label");
  const valueEl = card.querySelector(".summary-card__value");
  const subEl = card.querySelector(".summary-card__sub");

  labelEl.textContent = label;
  valueEl.textContent = value;

  if (sub) {
    card.classList.add("has-sub");
    subEl.textContent = sub;
    
    // Add hint icon only for warn cards
    if (variantClass === "summary-card--warn") {
      const hint = document.createElement("div");
      hint.className = "summary-card__hint";
      hint.setAttribute("aria-hidden", "true");
      hint.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>';
      card.appendChild(hint);
      
      // Add tap to expand/collapse on mobile
      card.addEventListener("click", () => {
        card.classList.toggle("expanded");
      });
    }
  }

  container.appendChild(card);
}

function makeStepCardEpassi({ index, tapCents, companyPayCents, salaryDeductionCents }) {
  const card = cloneTemplate("tpl-step-epassi");
  card.querySelector(".step-card__label").textContent = `EPassi tap #${index}`;
  card.querySelector(".step-card__amount").textContent = money(tapCents);

  const chips = card.querySelectorAll(".step-chips .chip");
  chips[0].textContent = `Company ${money(companyPayCents)}`;
  chips[1].textContent = `Salary ${money(salaryDeductionCents)}`;

  return card;
}

function makeStepCardPersonal({ personalCents }) {
  const card = cloneTemplate("tpl-step-personal");
  card.querySelector(".step-card__label").textContent = "Personal card";
  card.querySelector(".step-card__amount").textContent = money(personalCents);
  card.querySelector(".step-chips .chip").textContent = "Own payment";
  return card;
}

function attachDoneBehavior(card, paymentPlan) {
  const toggle = () => {
    card.classList.toggle("done");

    flipReorder(paymentPlan, () => {
      const all = Array.from(paymentPlan.children);
      all.sort((a, b) => (a.classList.contains("done") ? 1 : 0) - (b.classList.contains("done") ? 1 : 0));
      all.forEach((el) => paymentPlan.appendChild(el));
    });

    updateResetVisibility();
  };

  let startX = 0;
  let startY = 0;
  let isDragging = false;

  const handleDragStart = (x, y) => {
    startX = x;
    startY = y;
    isDragging = false;
    card.style.transition = "none";
    card.style.userSelect = "none";
  };

  const handleDragMove = (x, y) => {
    const currentX = x;
    const currentY = y;
    const diffX = currentX - startX;
    const diffY = currentY - startY;

    if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 5) {
      isDragging = true;
      const progress = Math.max(0, Math.min(1, diffX / 150));
      card.style.setProperty("--swipe-progress", progress);
      card.style.transform = `translateX(${diffX}px)`;
    }
  };

  const handleDragEnd = () => {
    card.style.transition = "";
    card.style.userSelect = "";
    if (isDragging) {
      const swipeProgress = parseFloat(card.style.getPropertyValue("--swipe-progress") || 0);

      if (swipeProgress > 0.4) {
        toggle();
      }
      
      card.style.transform = "";
      card.style.setProperty("--swipe-progress", "");
      isDragging = false;
    }
  };

  // Touch events
  card.addEventListener("touchstart", (e) => {
    handleDragStart(e.touches[0].clientX, e.touches[0].clientY);
  });

  card.addEventListener("touchmove", (e) => {
    handleDragMove(e.touches[0].clientX, e.touches[0].clientY);
  });

  card.addEventListener("touchend", handleDragEnd);

  // Mouse events
  card.addEventListener("mousedown", (e) => {
    handleDragStart(e.clientX, e.clientY);
  });

  card.addEventListener("mousemove", (e) => {
    if (isDragging || (e.buttons === 1 && Math.abs(e.clientX - startX) > 5)) {
      handleDragMove(e.clientX, e.clientY);
    }
  });

  card.addEventListener("mouseup", handleDragEnd);
  card.addEventListener("mouseleave", handleDragEnd);

  card.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      toggle();
    }
  });
}

function renderPlan(plan) {
  showPlanSections(!!plan);

  const summaryGrid = $("plan-summary");
  const paymentPlan = $("payment-plan");

  summaryGrid.innerHTML = "";
  paymentPlan.innerHTML = "";
  $("reset-done").style.display = "none";

  if (!plan) {
    syncStepsHeight();
    return;
  }

  addSummaryCard(summaryGrid, {
    label: "Company contribution",
    value: money(plan.companyPay),
    variantClass: "summary-card--good",
  });

  addSummaryCard(summaryGrid, {
    label: "Salary deduction",
    value: money(plan.salaryDeduction),
    sub: `Total paid: ${money(plan.salaryDeduction + plan.personalCard)}`,
    variantClass: "summary-card--warn",
  });

  addSummaryCard(summaryGrid, {
    label: "Personal card",
    value: money(plan.personalCard),
    variantClass: "summary-card--info",
  });

  addSummaryCard(summaryGrid, {
    label: "EPassi taps used",
    value: String(plan.tapCount),
  });

  const benefitRaw = $("remaining-benefit").value.trim();
  const tapsRaw = $("remaining-taps").value.trim();

  if (benefitRaw !== "" && tapsRaw !== "") {
    const benefit = Math.max(0, Number(benefitRaw));
    const taps = Math.max(0, Number(tapsRaw));

    if (!Number.isNaN(benefit) && !Number.isNaN(taps)) {
      const spentCents = plan.taps.reduce((acc, t) => acc + t, 0);
      const remainingBenefitCents = Math.max(0, Math.round(benefit * 100) - spentCents);
      const remainingTaps = Math.max(0, taps - plan.tapCount);

      addSummaryCard(summaryGrid, {
        label: "Remaining balance",
        value: money(remainingBenefitCents),
        variantClass: "summary-card--info",
      });

      addSummaryCard(summaryGrid, {
        label: "Remaining taps",
        value: String(remainingTaps),
      });
    }
  }

  plan.taps.forEach((tap, i) => {
    const { companyPay, salaryDeduction } = calcTapEffects(tap);
    const card = makeStepCardEpassi({
      index: i + 1,
      tapCents: tap,
      companyPayCents: companyPay,
      salaryDeductionCents: salaryDeduction,
    });
    attachDoneBehavior(card, paymentPlan);
    paymentPlan.appendChild(card);
  });

  if (plan.personalCard > 0) {
    const card = makeStepCardPersonal({ personalCents: plan.personalCard });
    attachDoneBehavior(card, paymentPlan);
    paymentPlan.appendChild(card);
  }

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      syncStepsHeight();
      updateResetVisibility();
    });
  });
}

function onOptimize() {
  const mealTotal = parseFloat($("meal-total").value) || 0;
  if (mealTotal <= 0) {
    alert("Please enter a valid meal total.");
    return;
  }

  const remainingBenefit = Math.max(0, parseFloat($("remaining-benefit").value) || 294);
  const tapsRaw = $("remaining-taps").value;
  const remainingTaps = tapsRaw === "" ? Infinity : Math.max(0, parseInt(tapsRaw, 10) || 0);

  const mealCents = Math.round(mealTotal * 100);
  const benefitCents = Math.round(remainingBenefit * 100);

  renderPlan(optimizePlan(mealCents, benefitCents, remainingTaps));
}

function onResetDone() {
  const paymentPlan = $("payment-plan");
  if (!paymentPlan) return;

  flipReorder(paymentPlan, () => {
    const cards = Array.from(paymentPlan.querySelectorAll(".step-card"));
    cards.forEach((card) => card.classList.remove("done"));
    cards.forEach((card) => paymentPlan.appendChild(card));
  });

  updateResetVisibility();
}

function onClearPlan() {
  $("plan-summary").innerHTML = "";
  $("payment-plan").innerHTML = "";
  showPlanSections(false);
  updateResetVisibility();
  requestAnimationFrame(() => syncStepsHeight());
}

$("optimize-btn").addEventListener("click", onOptimize);
$("reset-done").addEventListener("click", onResetDone);
$("clear-plan").addEventListener("click", onClearPlan);

window.addEventListener("resize", () => {
  updateLayoutMode();
  syncStepsHeight();
});

const leftColEl = $("left-col");
if (leftColEl && "ResizeObserver" in window) {
  const ro = new ResizeObserver(() => requestAnimationFrame(() => syncStepsHeight()));
  ro.observe(leftColEl);
}

showPlanSections(false);
requestAnimationFrame(() => syncStepsHeight());
