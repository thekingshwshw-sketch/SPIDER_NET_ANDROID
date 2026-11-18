# SPIDER NET — Pre-development audit
Audit date: 2026-11-18
Audited base: `redesign/spider-net-identity-2026-11-08` at `16f5dd890bc26b3911cd452909b5829d84f236a7`
Working branch: `feat/monthly-accounting-periods-2026-11-18`

## 1. Confirmed project structure
- Android wrapper: Kotlin `MainActivity` hosting a local HTML asset in Android WebView.
- Main application: `app/src/main/assets/index.html`, a single-file Arabic RTL HTML/CSS/JavaScript application.
- Local persistence: `localStorage`, database key `spidernet_accounting_v1`, schema marker `version: 1`.
- Android native bridge: JSON backup/restore, PNG export, and Android print integration.
- UI regression suite: Playwright script `tools/ui_regression_test.mjs`.
- CI: repository-root workflow `.github/workflows/build-apk.yml` builds the nested Android app, checks Android bridge wiring and JS syntax, runs Playwright regression checks, builds a debug APK and uploads it.
- No server-side database or device-to-device sync was found. Records are local to the installed app/WebView.

## 2. Existing business data model
The schema currently includes cards, POS, wallets, deliveries, consignment settlements, payments, wallet loads/sales, expenses, bills, partners, partner movements, stock adjustments, cash movements, audit rows, closures and manual journal entries. Default partner shares are 50/50 but are stored as editable partner records.

## 3. Existing accounting behavior
- The accounting workspace derives double-entry operational journal rows from source transactions and combines those with manual balanced journal entries and reversal rows.
- The chart of accounts separates physical cash, aggregate transfers/wallets, POS receivables, inventory, liabilities, partner balances, equity, revenues and expenses.
- Income statement calculations are date-filtered from the derived accounting records.
- Physical cash uses a single configured opening-count date/balance and dated cash movements.
- POS debt is computed from credit deliveries and consignment sales less payments and returns.
- Specific debt payment already supports source-level allocations. Generic POS payment currently permits a general payment and does not persist invoice-by-invoice allocation, so older payments can be assigned FIFO for display.
- Existing stock is cumulative: main stock is opening quantity less deliveries and wallet loads plus adjustments and consignment returns; wallet stock is calculated from wallet opening quantities and loads/sales.
- Bills can be recognized on their original date and paid on a later date; this distinction must be preserved to avoid recognizing the expense twice.

## 4. Existing period-close limitation
The current `closePeriod()` action is a review snapshot only. It accepts `YYYY-MM`, saves cumulative cash/debt/profit-at-snapshot values and explicitly states that it is not a monthly income statement or double-entry closing. It does not create custom date ranges, carry forward counted stock, freeze a period, or separate old/new receivables.

## 5. Important data-safety risks
1. Existing records do not all have explicit period IDs. Date-based classification can be suggested, but must be identified as inferred; no unknown legacy transaction should be silently assigned to a period.
2. Historic payments without allocation references cannot be reliably mapped to exact invoices from their amount alone. Existing FIFO display logic is an estimate, not proof of the original invoice settlement.
3. Stock has multiple locations (main store, wallets, POS consignment). A main-store physical count alone is not a total network inventory count.
4. The current cash opening count is global. Custom period snapshots must not zero balances or duplicate historical cash movements.
5. Expenses and bills are not interchangeable: bill recognition belongs to the period in which the expense/liability arose; later payment reduces the liability and cash, not the later period's expense.
6. Partner withdrawals/distributions are equity movements, not operating expenses. Partner-funded payments and repayments remain separate from capital until approved.
7. A debug APK and automated browser checks do not prove actual printer, document picker, backup/restore or data-retention behavior on the user's Android phone.

## 6. Confirmed design decisions
- Period start/end dates are user-defined.
- Periods must not overlap.
- Stock is carried forward from prior approved physical counts; count variances require an explained, approved adjustment.
- Show accrual/accounting profit and cash availability separately.
- Reserve is entered manually for each closing.
- Partner split starts from the existing stored shares (currently 50/50) and remains configurable.
- Old debt keeps its origin period; cash collection is recorded in the actual collection period and is not new revenue.
- No opening amount, quantity, cost, capital or partner settlement may be invented.

## 7. Development boundary
Work on a feature branch only. Do not merge to `main`, replace the installed app, overwrite user data, or publish a release until the staged implementation, migration tests, financial scenarios and Android device checks are reviewed and accepted.
