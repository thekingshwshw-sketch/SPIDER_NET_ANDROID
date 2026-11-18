# SPIDER NET — Data migration and test plan

## Migration rules
- Preserve the v1 database key and all existing source arrays.
- Add new fields/arrays only with defaults that do not create monetary balances or stock quantities.
- Keep old records without period IDs unchanged until the user reviews date-based classification.
- Distinguish `confirmed`, `date_inferred` and `unassigned` period provenance.
- Do not rewrite old payment allocations automatically. Surface unallocated legacy receipts as exceptions.
- Do not rewrite invoice IDs, dates, quantities, prices, costs, partner shares or starting balances.
- Take and verify a JSON backup before any production migration.
- Migration is additive and idempotent. Running it twice must not duplicate data.
- A failed migration must leave the prior stored JSON recoverable and prevent normal writes until recovery is resolved.

## Automated tests
### Periods
- create, edit only while open, review, close and lock;
- reject invalid dates, end before start and overlapping ranges;
- date gaps produce an unassigned warning;
- no transaction can be added in a closed period;
- closed source records cannot be silently edited or deleted.

### Receivables
- create credit delivery and consignment settlement;
- explicit allocation for partial and full collection;
- payment collection period differs from receivable origin period;
- old debt collection is not counted as new revenue;
- generic/unallocated legacy receipts remain flagged and are not reported as verified invoice matches;
- duplicate/double submission does not duplicate a collection.

### Payables and partners
- bill expense recognized in origin period;
- later payment only reduces cash and liability;
- partner-funded expense remains a partner payable until repayment;
- withdrawal/distribution is not an expense;
- approved shares add to 100%; no invented 50/50 if the stored shares differ.

### Inventory
- expected stock is reproducible from movement rows;
- count variance shows book/physical/difference/cost/reason;
- approved count adjustment is posted once;
- next period opening equals approved prior count;
- main store, wallets and consignment are not conflated.

### Reporting and print
- period income statement uses only journal rows within exact boundaries;
- cash flow is separate from accrual profit;
- reports show source period and collection/payment period;
- Arabic RTL layout, narrow phones, keyboard operation, print preview and no-clipping;
- all actions have a registered handler and no unhandled JavaScript exceptions.

### Android
- CI source integration checks;
- Node JavaScript syntax check;
- Playwright regression suite;
- Gradle debug APK build;
- actual Android device check for local persistence, backup/restore picker, print dialog and thermal/A4 printers.
