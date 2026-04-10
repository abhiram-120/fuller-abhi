
---

MY THINKING PROCESS

i had a tough time deciding what to build as all the 3 look interesting to me 

I started with option 1, the RFP agent. I dropped it after thinking about signal
frequency. A nonprofit issues one or two RFPs per year at most. That means you would
run the agent and find almost nothing most of the time. Thin signal, low utility.

Option 2, contact data agent, solves a real problem but the wrong one first. Finding
the right org matters more than having a phone number for the wrong one. Contact
enrichment belongs as a second layer, not the primary one.

Option 3 maps directly to what we discussed  in the call. 
signals not being insightful enough. The agent does not just return data. It explains
which orgs matter right now and why, using three real-time signal sources
That is the core problem. I built around that.

The hardest decision was the scoring approach. I had three options:

Keyword counter: revenue up plus hiring equals high score. Fast to build. No reasoning.
A salesperson gets a number with no explanation. Useless in practice.

Rule-based scoring: define weights manually. Hiring director = 40 points, revenue
growing = 30 points. Fast to build. Brittle. Does not handle nuance like contradictory
signals or context about the org's cause area.

LLM reasoning: send all signals to Gemini, get a score with a written explanation.
Slower per run, costs more per call. But the output is actually usable. A salesperson or our ai voice agent(which we will build in teh future)
reads why an org scored 87 and knows what to say on the outreach call. That is the
value. I chose this.

I considered LangGraph for the agent framework. again then Dropped it. Fuller Focus described their
system as calling APIs from an LLM. Adding LangGraph adds complexity without adding
intelligence for a five step sequential pipeline. The intelligence is in the prompts especaially when u said protize time over overengineering.

---

WHAT I BUILT

A sequential pipeline that takes a natural language query, extracts its intent, finds
matching nonprofits from ProPublica's 990 database, fetches three real-time signal
sources per org, sends everything to Gemini for scoring with written reasoning, enriches
the top 5 contacts, and outputs a dark HTML report and JSON file.

The HTML report was a deliberate product decision. JSON in a terminal is for engineers.
The person who acts on this output at an agency is a salesperson. They need something
they open in a browser on Monday morning and immediately understand. That is what the
report is.

The data quality badge per org was added specifically because of a real failure mode I
identified: Gemini receives empty signal data and still returns confident-sounding
reasoning. That is hallucination dressed as analysis. The quality badge forces honesty
into the output. Green means all three signals had real content. Red means the score
is based on very little. A user can see at a glance which results to trust.

The mixed signal flag was added for the same reason. Revenue declining but hiring senior
development staff is not obviously a buy signal or a distress signal. It could be either.
Hiding that ambiguity in a confident score would be wrong. The flag surfaces it.

---

HOW I HANDLE AMBIGUITY

Three types of ambiguity appeared during this build. Here is how each was handled.

Ambiguity in the query itself:
A query like "find good nonprofits" gives you nothing useful to search on. The query
parser step extracts sector and signal intent from the query before anything else runs.
If it cannot extract meaningful intent, the agent stops and asks for a more specific
query. It does not run blindly and return irrelevant results.

Ambiguity in the data:
990 data is delayed by 12 to 18 months. An org with growing revenue three years ago
could be struggling today. I treated financial data as a foundation signal, weighted it
lower than hiring and news which are real-time, and labelled the data quality on every
card so the user knows what the score is based on.

Some org names in ProPublica are legal entity names, not brand names. UNITED WAY OF
METROPOLITAN DALLAS INC is the same org as United Way Dallas. The display layer handles
this by showing names as returned from ProPublica without transformation, which is
honest, and the scoring step uses the full name for search which catches variants.

Ambiguity in the signals:
When signals contradict each other, the scorer flags mixed_signal as true and includes
both interpretations in the reasoning. This is visible as a purple badge on the card.
A declining revenue org that is actively hiring development leadership could be a
distressed org making a last attempt to fundraise, or it could be a transitioning org
investing in growth. Both interpretations are shown. The user decides.

When Tavily finds no signal for an org, the agent does not drop the org. It scores it
on available data, sets data_quality to weak, and shows exactly which signals were
missing. The org stays in the output with honest labels rather than being silently
removed or silently inflated.

---

TRADE-OFFS

Speed over accuracy on contact data. Domain lookup via Tavily plus Hunter.io is fast
and free. It is not as accurate as a paid contact database like Apollo or ZoomInfo.
For v1 the trade-off is correct. Confidence labels communicate the limitation.

Breadth over depth. The agent finds 10 orgs per query, not 100. Ten orgs with strong
reasoning is more useful to a salesperson than 100 orgs with no explanation.

LLM scoring over trained model. No historical conversion data exists to train on. LLM
reasoning is the best available option now. Once Fuller Focus has data on which signal
combinations actually converted to customers, this layer gets replaced with a classifier
trained on that data. The architecture i made supports swapping it out.

US only. ProPublica is the cleanest free data source and it covers the US. Going
international in v1 would require a paid data source and more complexity and not a free plan


---

WHAT WORKS

Real financial data from 990 filings. Accurate, verifiable, cross-referenceable.
Hiring signals from job boards for organisations with active job postings.
Gemini reasoning that explains scores honestly, including when data is thin.
HTML report that a non-technical salesperson can open and act on immediately.
JSON output that maps directly into any CRM or spreadsheet workflow.

---

WHAT DOES NOT WORK PERFECTLY

990 data is delayed. This is a data availability constraint, not a code problem.
Hiring signals for small regional nonprofits with no web presence are often empty.
Hunter.io contact rate depends on domain availability and free tier limits.
LLM scoring is consistent but not calibrated against real conversion outcomes.

---

THIS IS A V1 I WOULD ACTUALLY SHIP

It is not perfect. Every limitation is visible in
the output, not hidden. Every trade-off is documented here. The architecture supports
upgrading each component independently as better data sources become available.

---

ON THE FINAL NOTE


I have no nonprofit industry experience. I have not worked at an agency. I am not going
to pretend otherwise. What I have is the ability to take a vague commercial problem,
break it into components, make decisions about each one, and ship something that works.

This agent:
- Runs in one command
- Returns real data from real APIs
- Scores with reasoning not just numbers
- Flags its own uncertainty honestly
- Generates personalised outreach emails
- Sends those emails if you want it to
- Exports to CSV for any CRM
- Documents every trade-off made

That is what I built. The CV is whatever it is.
