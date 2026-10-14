Cisco XDR · HCL proof of value

# XDR Incident Lifecycle

One high-priority incident, two rules, and where the endpoint containment workflow sits. Endpoint tool assumed to be CrowdStrike, as in the build pack.

Automation rule path (instant) Assignment rule and playbook path Needs a person Stops or declined

## 1. Whole lifecycle: creation to closure

Both rules evaluate when the incident is created. The automation rule finishes in seconds. The assignment rule only attaches the playbook, and the analyst then works it to closure.

```mermaid
flowchart TD
  INC(["Incident createdpriority score 800 or above"])
  INC --> AR
  INC --> AS

  subgraph AUTO["AUTOMATION RULE: standalone, runs instantly"]
    direction TB
    AR["Rule condition metscore 800+ and incident created"]
    W1["Workflow: ServiceNowCreate or Update Ticket"]
    W2["Workflow: Webexpost message to room"]
    AR --> W1 --> W2
  end

  subgraph GUIDED["ASSIGNMENT RULE: attaches the playbook"]
    direction TB
    AS["Assignment rule matchessame incidents"]
    PB["Playbook attached:HCL - Standard Response"]
    AS --> PB
  end

  W2 --> PING["Analyst sees Webex messageand opens the incident"]
  PB --> PING

  PING --> P1

  subgraph PLAY["PLAYBOOK: analyst works each phase"]
    direction TB
    P1["IDENTIFICATIONreview summary and assetscheck observable verdictsupdate ticket"]
    P2["CONTAINMENTisolate host, block hasheach with an approval step"]
    P3["ERADICATIONremove malwarereset credentials"]
    P4["RECOVERYlift containmentupdate ticketclose incident"]
    P1 --> P2 --> P3 --> P4
  end

  P4 --> WL(["WORKLOGevery task, approval and note recorded"])

  classDef auto fill:#dff1f8,stroke:#0a7ea8,color:#0b2530,stroke-width:1.5px
  classDef guided fill:#e8e9fb,stroke:#5a5fd0,color:#171a4a,stroke-width:1.5px
  classDef human fill:#fdf0d5,stroke:#b7791f,color:#3a2a05,stroke-width:1.5px
  classDef start fill:#14232c,stroke:#14232c,color:#ffffff
  class AR,W1,W2 auto
  class AS,PB guided
  class PING,P1,P2,P3,P4 human
  class INC,WL start
```

Ticket and Webex happen with no one clicking. Everything from Identification onward is a person making a call, with XDR running the workflows and keeping the record.

## 2. Automation rule path in detail

What the rule does, in order, and what it leaves alone.

```mermaid
flowchart LR
  E(["Incident event"]) --> C{"Condition:score 800+and incident created?"}
  C -- "no" --> X(["Rule does nothing"])
  C -- "yes" --> V{"Workflowsvalidated?"}
  V -- "no" --> X2(["Rule cannot run themfix and validate first"])
  V -- "yes" --> T1["1. ServiceNowCreate or Update Ticket"]
  T1 --> D{"Ticket alreadyexists for incident?"}
  D -- "no" --> N1["Create ticketstatus: Incident Reported"]
  D -- "yes" --> U1["Update same ticket"]
  N1 --> T2["2. Webexpost message"]
  U1 --> T2
  T2 --> OUT(["Ticket existsWebex message postedno endpoint action taken"])

  classDef auto fill:#dff1f8,stroke:#0a7ea8,color:#0b2530,stroke-width:1.5px
  classDef stop fill:#fbe3e1,stroke:#c0392b,color:#4a1410,stroke-width:1.5px
  classDef start fill:#14232c,stroke:#14232c,color:#ffffff
  class C,V,T1,D,N1,U1,T2 auto
  class X,X2 stop
  class E,OUT start
```

Containment is not in this rule on purpose. A rule fires on a score and cannot wait for approval, so a false positive would isolate a host with nobody checking.

## 3. Assignment rule and playbook path in detail

The assignment rule runs once, at creation. After that the playbook is the analyst's checklist, and containment tasks start workflows with an approval gate.

```mermaid
flowchart TD
  NEW(["New incident created"]) --> M{"Assignment rulematches?"}
  M -- "no" --> DEF["Default playbook applies"]
  M -- "yes" --> ATT["HCL - Standard Response attached"]
  ATT --> I1

  subgraph ID["IDENTIFICATION"]
    direction TB
    I1["Review incident summaryand affected assetsmanual"]
    I2["Check observable verdictsmanual"]
    I3["ServiceNow Create or Updateautomated, updates same ticket"]
    I1 --> I2 --> I3
  end

  I3 --> Q{"Real threat?"}
  Q -- "no, false positive" --> CL1["Document and close incident"]
  Q -- "yes" --> C1

  subgraph CO["CONTAINMENT"]
    direction TB
    C1["Isolate affected hostruns CS - Isolate host"]
    C2["Block malicious hashruns CS - Block file hash"]
    C1 --> C2
  end

  C2 --> ER1

  subgraph ER["ERADICATION"]
    direction TB
    ER1["Remove malwaremanual"]
    ER2["Reset credentialsmanual"]
    ER1 --> ER2
  end

  ER2 --> R1

  subgraph RE["RECOVERY"]
    direction TB
    R1{"Host validatedclean?"}
    R2["Lift containmentruns CS - Lift containment"]
    R3["Update ticketdocument lessonsclose incident"]
    R1 -- "yes" --> R2 --> R3
  end

  R1 -- "no" --> ER1
  R3 --> WL(["Worklog complete"])
  CL1 --> WL

  classDef guided fill:#e8e9fb,stroke:#5a5fd0,color:#171a4a,stroke-width:1.5px
  classDef human fill:#fdf0d5,stroke:#b7791f,color:#3a2a05,stroke-width:1.5px
  classDef auto fill:#dff1f8,stroke:#0a7ea8,color:#0b2530,stroke-width:1.5px
  classDef start fill:#14232c,stroke:#14232c,color:#ffffff
  class M,ATT,DEF guided
  class I1,I2,Q,ER1,ER2,R1,R3,CL1 human
  class I3,C1,C2,R2 auto
  class NEW,WL start
```

Blue boxes inside the playbook are workflows that XDR runs when the analyst starts the task. If recovery validation fails, the loop goes back to Eradication instead of lifting containment.

## 4. Containment workflow: Isolate host

This is the new part. The same workflow runs from the playbook task or from the pivot menu on a host in the incident graph.

```mermaid
flowchart TD
  S(["Analyst runs CS - Isolate hostinput: hostname"]) --> F["Find device in CrowdStrikeget device id"]
  F --> FE{"Device found?"}
  FE -- "no" --> N0["Add note: host not found"] --> END0(["End: failed"])
  FE -- "yes" --> PL{"Hostname onprotected list?domain controllers, core servers"}
  PL -- "yes" --> AP2["Approval: senior role"]
  PL -- "no" --> AP1["Approval: analyst or lead"]
  AP1 --> AD{"Approved beforetimeout?"}
  AP2 --> AD
  AD -- "declined or timed out" --> N1["Add note: isolation not approved"] --> END1(["End: no action"])
  AD -- "approved" --> ISO["POST contain actionCrowdStrike network isolation"]
  ISO --> W["Wait 30 to 60 seconds"]
  W --> CHK{"Status is contained?"}
  CHK -- "no, retries left" --> W
  CHK -- "no, retries used up" --> N2["Add note: isolation not confirmed"] --> END2(["End: failed, escalate"])
  CHK -- "yes" --> REC["Add note to incident:who approved, device id, result"]
  REC --> OK(["End: host isolatedworklog updated"])

  classDef auto fill:#dff1f8,stroke:#0a7ea8,color:#0b2530,stroke-width:1.5px
  classDef human fill:#fdf0d5,stroke:#b7791f,color:#3a2a05,stroke-width:1.5px
  classDef stop fill:#fbe3e1,stroke:#c0392b,color:#4a1410,stroke-width:1.5px
  classDef start fill:#14232c,stroke:#14232c,color:#ffffff
  class F,FE,PL,ISO,W,CHK,REC auto
  class AP1,AP2,AD human
  class N0,N1,N2,END0,END1,END2 stop
  class S,OK start
```

The hash block (`CS - Block file hash`) follows the same shape with a hash format check first. `CS - Lift containment` uses the same lookup and then the lift action, and is what resets your lab host after each test.

## 5. Who does what, over time

The sequence for one real incident, from the first alert to closure.

```mermaid
sequenceDiagram
  autonumber
  participant X as Cisco XDR
  participant R as Automation rule
  participant SN as ServiceNow
  participant WX as Webex
  participant A as Analyst
  participant PB as Playbook
  participant CS as CrowdStrike

  X->>X: Incident created, score 800+
  par Automation rule
    X->>R: Rule condition met
    R->>SN: Create or Update ticket
    SN-->>R: Ticket number
    R->>WX: Post incident message
  and Assignment rule
    X->>PB: Attach HCL - Standard Response
  end
  WX-->>A: Message with incident link
  A->>PB: Identification tasks
  PB->>SN: Update same ticket, no duplicate
  A->>PB: Start Containment task
  PB->>A: Approval request
  A-->>PB: Approve
  PB->>CS: Isolate host
  CS-->>PB: Status contained
  PB->>X: Worklog entry
  A->>PB: Eradication tasks, manual
  A->>PB: Start Recovery task
  PB->>CS: Lift containment
  A->>SN: Update ticket
  A->>X: Close incident
  X->>X: Worklog complete
```

## Why the playbook is still needed

|  | Automation rule | Playbook |
| --- | --- | --- |
| Runs | Instantly, once | Across the life of the incident |
| Decides | Only on a condition (score 800+) | The analyst, at each step |
| Manual work | Cannot hold any | Review, eradication, credential resets |
| Approvals | Cannot wait for one | Containment tasks sit behind them |
| Progress | Not tracked | Shows what is done and what is left |
| Evidence | Run history only | Worklog of tasks, approvals and notes |
| Sheet rows it covers | Create a Trigger | Custom Playbook, Lifecycle to Closure, Review Worklog, Complete Containment |

**Two things to watch**

Keep Webex in the rule or the playbook, not both, or the room gets two messages per incident. Assignment rules apply only when an incident is created, so test the full flow with a new incident.