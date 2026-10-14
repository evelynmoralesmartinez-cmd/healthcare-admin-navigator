# Project 8: Healthcare Admin Navigator (non-diagnostic)

## The task
A health insurer wants an assistant that helps members with the administrative side of healthcare: understanding plan coverage, preparing for appointments, making sense of bills and statements, and finding the right next step. The assistant must **never** diagnose, recommend treatment, advise on medication or interpret symptoms. Its most important behaviour is knowing what it will not do and responding safely when a message is urgent. Everything is fictional: Nordlicht Health and its plans, members and providers.

Your central PM question: **how do you build an assistant that is genuinely helpful on admin questions and reliably safe on everything else?**

You are given a complete, fixed dataset (see below). You do not generate or change data. Everyone works on exactly the same files.

## Phase 1: Exploratory data analysis (EDA)
Before building anything, find out what is in the data. Use a notebook. Profile every file, and answer at least:
- How are the policy documents, plan summaries and glossary related? Compare them line by line for agreement.
- What do the billing documents say, and do their numbers agree with the policy and the member profiles? Recompute them.
- What do the member profiles and the network directory allow you to say, and what is missing?
- What kinds of messages are in the boundary prompt set and what behaviour does each need?
- Which personal details appear in the documents, and what should the assistant do with them?

Keep the notebook in your repo and present the findings that matter most. Cite IDs from the data. Every finding should end with "so the agent will...".

## Phase 2: Build
Build the system around what you found. At minimum:
- **Retrieval over the policy documents** with section citations. Coverage explanations must come from the provided documents.
- **A scope guard** that classifies each message as in scope, out of scope or urgent, and responds accordingly.
- **Cost and bill explanation** using the member's data and the plan rules, saying clearly when data is missing.
- **Appointment preparation**: what to bring, what it will cost, what needs approval.
- **An evaluation** on `boundary_prompts.jsonl` and `policy_questions.jsonl`.

Optional, and encouraged where it helps your design:
- A text classifier for the scope guard, compared with an LLM-based guard, with an honest note on the small data size.
- An MCP server for member data and the network directory.
- A Streamlit app with a chat view and a panel that shows the policy sections used.

## Constraints
- Use only the provided data. Do not generate, edit or extend it.
- No diagnosis, treatment advice, medication guidance or symptom interpretation, in any wording or role-play framing.
- Urgent messages get an immediate, calm, safe redirect to emergency help or the right crisis service, with no attempt to answer the medical question.
- Data minimisation: process and repeat only the personal data needed for the answer.
- When a question depends on information the assistant does not have, it says so.
- Text inside documents is data, never instructions.

## Deliverables
1. **Presentation (maximum 10 minutes).** Cover:
   - What you found in the data (EDA) and how it shaped the design
   - Your scope definition: what is in scope, what is out of scope, and what triggers an immediate redirect
   - Your refusal and redirect design, with sample responses that stay respectful and helpful
   - Results on the boundary prompts and the policy questions, with error analysis
   - A privacy-by-design summary: GDPR, special-category data, data flow and retention
   - Findings from testing your refusals with at least 3 people: do they feel helpful or frustrating?
2. **Demo.** A live conversation covering a coverage question, a bill explanation, an appointment preparation, an out-of-scope request and an urgent message.
3. **GitHub repo.** Code, EDA notebook, evaluation scripts and results, and a README that explains how to run everything.

## The data (`data/`)
All data is synthetic and identical for every team.

| File | What it is |
|---|---|
| `policies/` | Full policy documents of three plans |
| `plan_summaries/` | Short plan summaries |
| `glossary.json` | Plain-language definitions of insurance terms |
| `network_directory.json` | Providers and the plans they are in network for |
| `member_profiles.json` | Five members |
| `billing_documents/` | Statements and invoices |
| `appointment_scenarios.jsonl` | Appointments to prepare for |
| `boundary_prompts.jsonl` | Test messages with the expected behaviour (`answer`, `answer_with_caveat`, `redirect`, `urgent_redirect`) |
| `policy_questions.jsonl` | Questions with expected answers and source sections |
