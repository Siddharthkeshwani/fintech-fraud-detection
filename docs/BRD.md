## Business Pronlem
The Digital transaction fraud is escalating faster than static, rule-based detection can adapt.That's why the organization needs a dynamic model which flags fraud in real time without materially increasing flase declines on legitmate customers.


## Target Variable
`is_fraud`(yes/no), should be predicted at the exact moment of authorization - using only the information available at that instant,No later information (like confirmed chargebacks) is allowed in, to avoid data leakage.


## Event window (When does the model have to decide)
It should be real-time, per-transaction scoring,not a forcast over days or weeks


## Define KPIs (A socreboard Number)
- Recall :  Out of all the fraud transactions in data, how many did the model
catched as fraud?
- Precision : Out of all transaction we catched, how many were actually fraud,not legitimate(if it catches too many legitimate, it is blocking the real transactions)

**Technical KPI:** Maximum Recall at controlled Precision floor, optimized using AURPC (not plain accuracy or ROC-AUC), because fraud is a rare-event problem.

**Business KPI:** Net dollars saved = (fraud $ prevented) - (customer friction $ cost from flase declines) -  (model operating cost)


## Cost Assumptions
since this is practice Project we don't have the real bank's real transactions,
so me make a reasonalble pretend numbers.
- Average Loss per missed fraud case : -$400
- Average friction cost per false decline (annoyed real customer): -$15
- Assumption monthly transaction volume for this story: $10,000,000.


## stakeholders
**Fraud Ops/Risk team (primary - catching fraud)** - Are we really catching the thieves,
**Compliance (needs exlainability)** - can we explain why model flagged it's a fraud
**Customer experience (false-positive requirement)** - Are we accendentily catching the legitimate customers.
**Engineering (real-time latency requirement)** - is the model fast enough to decide before the transcation finishes.


## Constraints (Rules we are not allowed to Break)
- Whenevere model says "Fraud" it must also answer the question why?
- we are not allowed to use real people's real private data -  only pretend(synthetic)data, so nobody's real secrets are at risk.

The model must produce an explainable reason code per flagged transaction (via SHAP). Only synthetic/anonymized data is used - no real customer data.


## Defination of Success
A deployed, explainable, monitored fraud-detection model,backed by a quantified business case (ROI), with a natural - language assistant so non-technical stakeholders can ask it questions themselves.
