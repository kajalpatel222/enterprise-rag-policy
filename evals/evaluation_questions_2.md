# Evaluation Questions - Version 2

This set is intentionally broader than Version 1. It tests cross-document reasoning,
exact keyword retrieval, multi-step answers, no-answer behavior, and policy conflicts.
It is reserved for a future evaluation run.

| ID | Question | Category | Expected evidence or behavior |
| --- | --- | --- | --- |
| EQ2-01 | A new employee is starting today. What happens on Day 1, and what security principle should govern their system access? | Cross-document | `hr_policy.txt` - Onboarding Process; `compliance_manual.txt` - Information Security Policy |
| EQ2-02 | An employee wants to work remotely from outside their country while handling personal data. What approval and data-transfer safeguards apply? | Cross-document | `hr_policy.txt` - Remote Work Policy; `compliance_manual.txt` - Cross-Border Data Transfers |
| EQ2-03 | A P1 incident involves personal data exposed through an API. What are the response, containment, regulatory-notification, and reporting requirements? | Cross-document | `compliance_manual.txt` - Incident Response Policy and Data Privacy; `tech_docs.txt` - SLA and Uptime |
| EQ2-04 | A developer receives HTTP 429 while using an OAuth access token. What does the error mean, how should they retry, and how long is the token valid? | Cross-document | `tech_docs.txt` - Rate Limiting, Error Codes Reference, API Authentication |
| EQ2-05 | When an employee leaves ACME, what must happen to system access, and how long should employee personal data be retained afterward? | Cross-document | `compliance_manual.txt` - Information Security Policy and Data Retention Schedules |
| EQ2-06 | What steps are required before approving a high-risk vendor that handles personal data and transfers it outside the EEA? | Cross-document | `compliance_manual.txt` - Third-Party Vendor Management and Cross-Border Data Transfers |
| EQ2-07 | What protections apply to a privileged administrator who works remotely? | Cross-document | `compliance_manual.txt` - Access Control; `hr_policy.txt` - Remote Work Policy |
| EQ2-08 | Compare the operational recovery plan for Tier 1 systems with the backup schedule and backup region. | Multi-part | `compliance_manual.txt` - Business Continuity and Disaster Recovery |
| EQ2-09 | What must a production deployment pass before full rollout, and what happens if the canary error rate is too high? | Exact process | `tech_docs.txt` - Deployment Guide |
| EQ2-10 | A webhook endpoint returns a non-2xx response. How many times will delivery be retried, what backoff is used, and how should the signature be validated? | Exact process | `tech_docs.txt` - Webhooks |
| EQ2-11 | What does `X-ACME-Signature` protect, and what should happen to an unverified webhook? | Keyword-based | `tech_docs.txt` - Webhooks; preserve the exact header name and HMAC-SHA256 term |
| EQ2-12 | What do `Retry-After` and `X-RateLimit-Reset` tell a developer after a rate-limit response? | Keyword-based | `tech_docs.txt` - Rate Limiting; preserve both exact header names |
| EQ2-13 | What is the difference between `RTO` and `RPO` for Tier 1 systems? | Keyword-based | `compliance_manual.txt` - Business Continuity and Disaster Recovery; preserve both acronyms |
| EQ2-14 | When is `MFA` required, and what password controls apply to employees? | Keyword-based | `compliance_manual.txt` - Information Security Policy; preserve `MFA` and password requirements |
| EQ2-15 | Why would a vendor security assessment use `SIG Lite` or `CAIQ`? | Keyword-based | `compliance_manual.txt` - Third-Party Vendor Management; preserve both exact terms |
| EQ2-16 | What does Article 33 require after a personal-data breach, and how does that differ from the deadline for an employee GDPR data request? | Cross-document | `compliance_manual.txt` - Incident Response Policy and Data Subject Rights |
| EQ2-17 | What are the two different annual audit activities ACME performs, and how often does each occur? | Multi-part | `compliance_manual.txt` - Audit and Compliance Monitoring |
| EQ2-18 | What are the remote-work rules for an employee who has completed Day 90 but not the 6-month probationary period? | Conflict | Cite `hr_policy.txt` - Onboarding Process and Remote Work Policy; do not choose a rule without noting the conflict |
| EQ2-19 | Does ACME provide a home-office equipment stipend? | No-answer | Refuse because the corpus does not contain this information |
| EQ2-20 | What is the payroll cutoff date for submitting employee expenses? | No-answer | Refuse because the corpus does not contain this information |

## Evaluation Focus

- Cross-document questions should cite every relevant policy section.
- Keyword questions should preserve exact technical names, headers, acronyms, and terms.
- Multi-part questions should include every requested deadline, action, or exception.
- No-answer questions should not be answered from unrelated benefits or HR content.
- Conflict questions should identify the conflict instead of silently selecting one policy.
