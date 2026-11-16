# How it works, in plain language

This explains every part of the project without code, so you can explain it confidently in an interview
or a pitch meeting.

---

## The big idea in one analogy

Think of a plant's alarm system.

| Plant world | This project |
|---|---|
| The **alarm** goes off: "K-101 high vibration" | **Detection**: what tools like Neuron 5 already do |
| The **reliability engineer** looks at the trends and asks "which failure mode is this?" | **Diagnosis**: matches symptoms to the FMEA |
| The **alarm response procedure** plus engineering judgement: "do this, this fast" | **Prescription**: actions, priority, work order |

Most plants have automated only the first row. This project automates rows 2 and 3, and always leaves the
final decision with a human.

---

## Part 1: The knowledge (the YAML files)

**`asset_k101.yaml`** is the compressor's **datasheet**: 18 sensors, each with its normal value, normal
noise, and alarm and trip limits. Think of it as the instrument index plus the cause & effect chart.

**`fmea_centrifugal_compressor.yaml`** is the **FMEA**, written so a computer can read it. Each of the 9
failure modes has:

- a **symptom signature**: which sensors move, and in which direction. *Bearing wear → DE vibration up,
  DE bearing temperature up.* Primary symptoms carry weight 1.0, secondary ones less.
- **confirm checks**: how a vibration specialist would prove it.
- **actions** in four horizons: confirm → immediate → corrective → defect elimination.
- **codes**: an ISO 14224 failure mode and mechanism, and SAP damage and cause codes.

This is the part no generic AI company can easily copy. It is reliability engineering knowledge.

---

## Part 2: The data (simulate.py)

Real failure data is confidential, so we **create** realistic compressor data:

- normal behaviour, including a daily ambient-temperature cycle, small load swings, sensor noise and a few
  short process upsets (to try to trick the detector into false alarms)
- then we **inject a fault** that grows along a **P-F curve**: slow at first, then accelerating, just like
  real degradation

Because we injected the fault, we know the right answer. That's what lets us **measure accuracy**.

Important: the fault "physics" in the simulator is written **separately** from the FMEA, and includes side
effects the FMEA doesn't mention. Otherwise the agent would be marking its own exam.

---

## Part 3: Detection (detect.py), "is something really wrong?"

1. **Learn normal** from the first 21 days: for each sensor, its typical value at each hour of the day. This
   removes the daily ambient cycle, like **ambient compensation** on a transmitter.
2. **Smooth** the data over 6 hours, so short process upsets don't count. This works like a filter or
   alarm delay.
3. **Measure how unusual** each sensor is: the **z-score**, "how many normal-noise widths away from normal".
   We use the **median** and **MAD** rather than mean and standard deviation, because one spike can't
   distort them. It's the same reason we use **2oo3 voting** instead of averaging in a SIS.
4. Raise an alert only if a sensor is:
   - **statistically unusual** (z ≥ 6), **and**
   - **meaningful**: it has used at least 4% of its margin to the alarm limit (like an **alarm deadband**),
     **and**
   - moving **towards** its limit (a bearing getting cooler is not deterioration), **and**
   - still true after **1 hour** (persistence, like an alarm on-delay).

Result: 0 false alarms in 60 healthy machines, and every fault caught.

---

## Part 4: Diagnosis (diagnose.py), "which failure mode is it?"

For every failure mode in the FMEA, the agent asks three questions, just as you would:

1. **Support:** are the expected symptoms there, moving the right way? Primary symptoms count more.
2. **Contradiction:** is an expected symptom moving the *wrong* way? That counts against it.
3. **Explained:** how much of the total abnormality does this failure mode explain? If DE vibration, DE
   temperature *and* axial position are all up, bearing wear doesn't explain the axial shift, but
   misalignment does.

`match score = support × (0.2 + 0.8 × explained)`

Each symptom's strength is the **weaker** of "how unusual" (statistics) and "how much alarm margin is used"
(engineering). A change must be both real and meaningful. This single rule fixed the case where a tiny 3 µm
vibration rise was outvoting a big 6.5% efficiency drop.

---

## Part 5: The agent (agent.py), the 10 steps

| Step | What it does | Engineering equivalent |
|---|---|---|
| 1 Check | Is there a persistent anomaly? | Acknowledge the alarm |
| 2 Diagnose | Rank the 9 failure modes | Read the trends against the FMEA |
| 3 Doubt | If the top two are close, ask for a discriminating test | "Get me a vibration spectrum before we decide" |
| 4 Recall | Search work-order history; repeat failure? | Check SAP history; bad-actor review |
| 5 Forecast | Days until alarm and trip at the current trend | "How long have we got?" |
| 6 Decide | Priority P1–P4 from severity, confidence, time to trip, criticality | Risk-based prioritisation |
| 7 Value | Cost of acting now vs running to failure | Business case for the planner |
| 8 Prescribe | Actions in 4 horizons, plus RCA if it's a repeat | Maintenance strategy and defect elimination |
| 9 Draft | SAP PM-style M2 notification | Raise the notification |
| 10 Hand over | Waits for engineer approval | Management of change / human in the loop |

Every step is logged in the **reasoning trace**, so you can show exactly *why* it recommended something.

### Why not just ask ChatGPT?

An LLM on its own can sound confident and be wrong, and it can't show its working against sensor data. In
industry, an unexplained recommendation gets ignored. Here the **engineering decisions are deterministic
and traceable**. The LLM is optional and only rewrites the summary, using facts it is given.

---

## Part 6: History (history.py)

- 132 synthetic work orders over about 5 years for three sister compressors, written the way technicians
  write: *"DE brg high vib + temp"*.
- About 30% of failures are deliberately **not coded**, as in real SAP.
- **TF-IDF text search** finds similar jobs by their words, after expanding plant shorthand (brg → bearing,
  DGS → dry gas seal).
- If the same failure mode hit this machine **2 or more times in 36 months**, it is flagged as a **bad
  actor** and the agent adds "Initiate formal RCA" to the plan.

---

## Part 7: Proving it (evaluate.py)

- 9 failure modes × 10 random variations, plus healthy machines, on **variations never used while tuning**
  (a held-out test).
- 97% correct diagnosis three days after the alert; 100% have the right answer in the top 3.
- The 3 wrong answers were all ones the agent itself flagged as uncertain. That is the behaviour you want:
  **know when you don't know.**
- Weakest case: early misalignment (70%), because it looks like bearing wear or imbalance when only
  vibration has moved. Real vibration engineers face the same problem, which is why the agent asks for a
  spectrum.

---

## Words to use confidently

- **P-F curve / P-F interval:** time from detectable symptom (P) to functional failure (F)
- **Robust z-score (median / MAD):** "how unusual", resistant to spikes
- **FMEA symptom signature:** the fingerprint a failure mode leaves in the data
- **Differential diagnosis:** ranking look-alikes and testing to separate them
- **Bad actor:** equipment with repeat failures, and a candidate for RCA
- **Human in the loop:** AI recommends, an engineer approves
- **Deterministic core:** the same input always gives the same output, so it can be audited
- **Held-out evaluation:** tested on data not used to build or tune it
