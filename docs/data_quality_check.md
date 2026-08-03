# Step 2 (Acquire) — Data Quality Check, Post-Microtask 8

Fill in your real numbers from the Microtask 8 queries below. This is the
kind of validation note a Data Analyst attaches to any new data source
before anyone downstream is allowed to trust it.

| Check | Query source | Expected | Actual (fill in) | Pass? |
|---|---|---|---|---|
| Total transactions stored | 8.3 | > 0 | | |
| Overall fraud rate | 8.4 | ~0.05%–0.15% | | |
| CASH_OUT share | 8.5 | ~35% | | |
| PAYMENT share | 8.5 | ~34% | | |
| CASH_IN share | 8.5 | ~22% | | |
| TRANSFER share | 8.5 | ~8% | | |
| DEBIT share | 8.5 | ~1% | | |
| Null amount / name_orig / name_dest / event_time | 8.6 | all 0 | | |
| Fraud rows with balance mismatch | 8.7 | ~60% of fraud rows | | |
| Average event-to-storage lag | 8.8 | < 1 second | | |

**Notes / anything unexpected:**
(write anything that looked off here, and what you think caused it)

---
*Signed off as ready to proceed to Microtask 9 (Faker-enriched customer,
device, and merchant tables) once every row above shows "Pass."*
