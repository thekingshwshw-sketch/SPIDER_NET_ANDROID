# SPIDER NET — Monthly accounting periods specification

## Approved configuration
- Custom period start and end dates.
- Carry-forward stock using an actual counted and approved closing quantity.
- Display accounting/accrual profit and real liquidity as separate measures.
- Reserve amount manually entered for every closing.
- Partner shares read from configured partner records; default currently 50/50.

## Accounting invariants
1. Every original sale/receivable has one immutable origin period once assigned.
2. Every payment has a collection date/period and explicit allocations to the original receivable items whenever the source is known.
3. A legacy payment without allocation remains visibly unresolved/inferred; FIFO may be shown as a provisional analysis but must never be represented as a confirmed invoice allocation.
4. A prior-period receivable collection increases the receiving cash/wallet account and reduces receivables. It does not create current-period sales revenue.
5. A prior-period bill payment reduces cash/wallet and the old liability. It does not record the expense again in the payment period.
6. Period profit is derived from accounting journal rows inside that period's exact date boundaries; do not use the app's all-time profit estimate as monthly profit.
7. Liquidity is calculated from real opening balances plus actual cash/account movements during the period. It is not the same as profit.
8. Distributions are partner equity movements and cash outflows, not operating expenses.
9. Reserve is an appropriation/retention decision, not an expense.
10. A stock-count variance is not hidden: show book quantity, counted quantity, variance, cost impact, reason, preparer and approver.
11. The closing snapshot is immutable after approval; later corrections use dated, auditable adjustments in an open period.
12. Closed periods cannot be edited/deleted silently. Any controlled correction preserves the original and records who/when/why.
13. Opening balances must originate from an approved prior close or an explicitly confirmed initial physical reconciliation.

## Period states
- `OPEN`: transactions are allowed within the date range.
- `REVIEW`: close checklist and reconciliations are being prepared.
- `CLOSED`: signed/approved close snapshot exists; source period is protected.
- `LOCKED`: administrative hard-lock following review/export.

No overlapping active date ranges. Period gaps must be visible as unassigned-date ranges rather than silently forced into a neighboring period.

## Period snapshot contents
- Period ID, name, start/end, status, timestamps and prior period reference.
- Opening and closing trial-balance/account balances.
- Opening/closing physical cash by supported payment account.
- Receivables by POS and original invoice/delivery item, including origin period, collected-to-date and open amount.
- Payables/bills by origin period, paid-to-date and remaining.
- Inventory by SKU/category and location (main store, each wallet, and consignment where records support it), book quantity, physical quantity, variance and unit cost.
- Period income statement, actual cash flow and non-cash movements.
- Reserve decision, profit proposed for distribution, approved distribution and actual settlement per partner.
- Exceptions/unresolved legacy items and audit log references.

## Close workflow
1. Validate date boundaries and preceding period continuity.
2. Review all source transactions dated inside the period.
3. Identify out-of-period and undated transactions.
4. Reconcile cash and each available wallet/payment channel independently.
5. Review POS receivables and allocate payments to original invoice items.
6. Review payables, recurring bills and partner-paid items.
7. Count inventory by category and stock location.
8. Explain/approve count variances; post auditable inventory adjustments once.
9. Calculate period profit from the double-entry records.
10. Calculate actual cash available after obligations and required working liquidity.
11. Enter reserve manually.
12. Calculate distribution ceiling as the lesser of distributable profit after reserve and cash available after protected obligations/working liquidity.
13. Confirm partner shares and record proposed versus actually paid distributions separately.
14. Save a close snapshot, lock source period, and prepare the next period's opening balances.

## Current-scope warnings
The current database aggregates transfer/wallet balances into one account and does not maintain a separate actual balance for every named wallet. A wallet balance feature needs source-level wallet opening balances and reconciled movements before it can be claimed as a true cash balance. Main-store stock can be derived from the current stock movement model, but full location-by-location physical count requires a clear count process for wallet stock and consignment-held stock too.

## Acceptance scenarios
- A November receivable of 10,000 with 2,000 paid in November and 3,000 collected in December remains a November debt, carries a 5,000 open balance, adds 3,000 to December receipts and adds zero to December revenue.
- Paying a November recognized 25,000 rent liability in December reduces December cash and the liability, without a second December rent expense.
- A closing count difference is displayed and cannot be silently ignored; the approved count becomes next period's opening physical stock.
- Current-period accrual profit and current-period cash movement appear separately.
- Partner distribution is limited by approved distributable profit and available liquidity; it is never included in operating expenses.
- A closed period refuses ordinary edits/deletes; a correction is a separate, traceable adjustment.
- Existing v1 backups still load without losing records; unknown/malformed fields are preserved or flagged.
