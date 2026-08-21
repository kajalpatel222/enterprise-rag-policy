# Evaluation Questions - Version 1

Use these questions to evaluate retrieval and faithfulness after each RAG iteration.

| ID | Question | Category | Expected evidence or behavior |
| --- | --- | --- | --- |
| EQ-01 | How many paid annual-leave days do full-time employees receive? | Direct | `hr_policy.txt` - Annual Leave Policy |
| EQ-02 | How many remote-work days are allowed each week? | Direct | `hr_policy.txt` - Remote Work Policy |
| EQ-03 | What benefits are available through the employee assistance program? | Direct | `hr_policy.txt` - Compensation and Benefits |
| EQ-04 | How long does ACME have to fulfill a GDPR data-subject request? | Direct | `compliance_manual.txt` - Data Privacy and GDPR Compliance |
| EQ-05 | What are the recovery-time and recovery-point objectives for Tier 1 systems? | Direct | `compliance_manual.txt` - Business Continuity and Disaster Recovery |
| EQ-06 | What does HTTP 429 mean, and what should a developer do next? | Exact term | `tech_docs.txt` - Rate Limiting and Error Codes Reference |
| EQ-07 | How long is an API access token valid? | Exact term | `tech_docs.txt` - API Authentication |
| EQ-08 | Which encryption standard is required for data at rest? | Exact term | `compliance_manual.txt` - Information Security Policy |
| EQ-09 | What is the password-length requirement? | Exact term | `compliance_manual.txt` - Information Security Policy |
| EQ-10 | What happens when a P1 security incident is reported? | Multi-part | `compliance_manual.txt` - Incident Response Policy; `tech_docs.txt` - SLA and Uptime |
| EQ-11 | What must happen to a terminated employee's system access, and by when? | Direct | `compliance_manual.txt` - Information Security Policy |
| EQ-12 | What is the process for approving a high-risk vendor that handles personal data? | Multi-step | `compliance_manual.txt` - Third-Party Vendor Management |
| EQ-13 | Can an employee work remotely from outside their country of employment? | Direct | `hr_policy.txt` - Remote Work Policy |
| EQ-14 | What is ACME's payroll schedule? | No-answer | Refuse because the corpus does not contain this information. |
| EQ-15 | Does ACME provide employee stock options? | No-answer | Refuse because the corpus does not contain this information. |
| EQ-16 | When does an employee become eligible for remote work: after 90 days or after 6 months? | Conflict | Cite both conflicting HR sections and state that the policy needs clarification. |

## Evaluation Criteria

- The retrieved source must include the expected section for direct and exact-term questions.
- The answer must not introduce facts absent from the retrieved evidence.
- No-answer questions must clearly state that the corpus does not provide the information.
- The conflict question must cite both relevant sections instead of choosing an unsupported answer.
