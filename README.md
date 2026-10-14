# Healthcare Admin Navigator (non-diagnostic)

An AI assistant for members of a (fictional) health insurer, **Nordlicht Health**. It helps with the
administrative side of healthcare: plan coverage, bills and statements, and appointment preparation.
It **never** diagnoses, recommends treatment, advises on medication or interprets symptoms, and it
redirects urgent messages to emergency help.

> **Central PM question:** How do you build an assistant that is genuinely helpful on admin
> questions and reliably safe on everything else?

Project 8 of the AI Agents Project (neuefische AI Product Management bootcamp).
All data is synthetic and was provided by the bootcamp; it was not generated, edited or extended.

---

## How it works

```
Member message
   │
   ▼
SCOPE GUARD (two layers)
   1. keyword safety net for emergencies
   2. LLM classifier with 4 labels
   │
   ├── urgent_redirect     → fixed template: call 112, or a crisis line   (no LLM)
   ├── redirect            → fixed template: pharmacist / paediatrician / doctor + an admin offer   (no LLM)
   ├── answer_with_caveat  → RAG answer + caveat
   └── answer              → RAG answer with policy section citations, e.g. [S4.7]
```

For admin answers, the assistant combines three sources:

- **Retrieval** over the full policy documents of the member's plan (never the plan summaries).
- **Facts computed in Python**: member deductible, network status, recomputed bill amounts, appointments.
- **LLM generation** that may only use those sources and must cite the policy sections.

Date of birth and address are never sent to the language model (data minimisation).

---

## Key EDA findings (`01_eda.ipynb`)

| Area | Finding | So the agent will… |
|---|---|---|
| Boundary prompts | 33 test messages, imbalanced (13 redirect, 9 answer, 6 answer_with_caveat, 5 urgent). Some urgent messages look like admin requests (BP19), and wording can point the wrong way (BP03 vs. BP33). | check urgency first and classify by intent, not by keywords |
| Policies vs. summaries | The plan summaries contradict the full policies in 4 numbers and 3 rules. | use only the full policies and the glossary |
| Billing documents | 4 of 13 EOBs have wrong amounts (D12, D13, D14, D15); 2 invoices ask for more than the EOB (D10, D11). | recompute every amount instead of repeating it |
| Members and network | One appointment is out of network (S05); one member has no deductible data (M-1005). | warn about out-of-network providers and say when data is missing |
| Personal data | All 15 billing documents contain name, date of birth, address and member ID, plus health information. | keep date of birth and address away from the LLM |

---

## Results (`02_build_and_evaluate.ipynb`, `results/`)

**Scope guard, 33 boundary prompts**

| Metric | Result |
|---|---|
| Accuracy | 94% (31/33) |
| Recall `urgent_redirect` | 100% (5/5), also with the LLM alone |
| Recall `redirect` | 100% (13/13), including 4 manipulation attempts |
| Safety-critical errors | 0 |

The two errors (BP07, BP29) are both in the `answer_with_caveat` class and go in opposite directions.

**Policy questions, 16 questions**

| Metric | Result |
|---|---|
| Correct answers (LLM judge) | 88% (14/16) |
| Correct answers (after human review) | 94% (15/16) |
| Expected policy section retrieved | 94% (15/16) |
| Expected policy section cited | 81% (13/16) |

**Simulated user test of the refusals** (3 fictional personas played by an LLM, not real people)

| Case | v1 | v2, run 1 | v2, run 2 |
|---|---|---|---|
| Urgent | 2.0 | 4.0 | 3.7 |
| Role play | 1.7 | 2.0 | 2.0 |
| Medication | 1.3 | 2.0 | 1.7 |

Only the improvement of the urgent message is consistent across both runs. The medication refusal
stays low because the personas wanted a dose, which the assistant will never give.

---

## Failure log

| Problem | What happened | Fix |
|---|---|---|
| Model retired | `llama-3.3-70b-versatile` was no longer available on Groq | switched to `openai/gpt-oss-120b` |
| Rate limit (HTTP 429) | the free tier allows 8,000 tokens per minute for this model | automatic wait and retry; a smaller model for the judge |
| Citation formats | the model wrote `【S4.7】`, invisible characters or `[**S7**]` | `clean_answer()` normalises citations |
| Leaked field names | the model cited internal names such as `[Fact: deductible_remaining_eur = 350]` | prompt rule + cleaning step |
| Hallucination | "12 sessions per condition" (two policy sentences merged) | reported; next step: require exact rule wording |
| Judge error | the LLM judge marked a correct answer (PQ11) as wrong | human review of all judgements |

---

## Privacy by design

- **Special category data:** health data is special category data under GDPR Art. 9 (see also policy S10).
- **Data minimisation:** the LLM receives only what an answer needs: the plan, deductible, network status, the pseudonymous member ID and, for bill questions, the services and amounts on the bills (which are health data). Name, date of birth and address are never sent.
- **Data flow:** member message → scope guard → retrieval and Python facts → LLM (Groq API) → answer.
  A production version would need a data processing agreement and EU hosting for the LLM provider.
- **Retention:** this prototype does not store conversations; the `results/` folder contains only evaluation output. The LLM provider's own retention policy would need to be checked before production.

---

## Project structure

```
healthcare-admin-navigator/
├── BRIEF.md                      # the task
├── data/                         # the fixed dataset (synthetic)
├── 01_eda.ipynb                  # exploratory data analysis
├── 02_build_and_evaluate.ipynb   # smoke test, evaluations, simulated user test
├── navigator.py                  # the assistant
├── evaluate.py                   # evaluation scripts
├── results/                      # saved evaluation results
├── requirements.txt
└── .gitignore                    # excludes .env and .venv
```

---

## How to run

1. Create and activate a virtual environment (Python 3.13):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Create a file called `.env` in the project folder with your Groq API key:
   ```
   GROQ_API_KEY=your_key_here
   ```
3. Open the notebooks in order: `01_eda.ipynb` (no API calls) and `02_build_and_evaluate.ipynb`.
   **Note:** running all of notebook 02 makes about 80 LLM calls and takes around 20 minutes on the free tier.
4. Try the assistant in a notebook cell:
   ```python
   import navigator as nv
   nv.show(nv.respond("Does my plan cover physiotherapy?", member_id="M-1002"))
   ```

---

## Limitations and next steps

- The test sets are small (33 + 16 cases), so one error changes a metric by 3 to 6 points.
- The keyword safety net was written after seeing the urgent test messages; the LLM-only result is the fair one.
- The `answer_with_caveat` class is fuzzy; it needs clearer criteria and new test examples.
- The user test was simulated; the next step is a test with real members.
- The smoke test in `results/smoke_test.md` was run with version 1 of the refusal templates.
