# AI Context Profiles

The AI context system renders structured data from the tracker into markdown
profiles tuned for different research tasks. Each profile is self-contained —
paste it into any AI chat without needing other sheets or documents.

Profiles are not a replacement for AI decision-making. They give an AI the
right facts; you ask the right question.

---

## Profiles

### Specs / Compatibility `[M1]`
`GET /api/ai-context/specs`

All assets with a Specs record. Full technical fields: socket, form factor,
RAM gen, PCIe gen, chipset, TDP, capacity, slot counts, compatibility notes.

**Use for:**
> "Does the NH-D15 clear DDR5 on the B850?"
> "What M.2 slots are still available in PCB2-V2?"
> "Is the RTX 5070 Ti compatible with the Lancool II case?"

---

### Build Planning `[M1]`
`GET /api/ai-context/build/{project_key}`

Full specs for all assets currently assigned to a project. Includes state,
PSU headroom calculation (sum TDP vs PSU rating), available slot counts,
and compatibility notes for every component.

**Use for:**
> "What GPU would work in PCB2-V2 without needing a PSU upgrade?"
> "Which M.2 slot should I put the boot drive in on the B850?"

---

### Upgrade Planning `[M1]`
`GET /api/ai-context/upgrade/{project_key}`

Current build specs + all Planned assets for the same project + cost delta.
Shows what each planned part replaces and the net new spend.

**Use for:**
> "Is the 9800X3D worth it over the 12600K for gaming workloads?"
> "What's the total cost of the PCB2-V2 upgrade and what am I getting for it?"

---

### HomeLab `[M2]`
`GET /api/ai-context/homelab`

All HomeLab project assets. SBC specs, storage configuration, power draw
estimates (idle and peak), network roles, and running cost at current rate.

**Use for:**
> "Can the RPI5 handle Plex 4K transcoding alongside Docker services?"
> "What's my homelab drawing at idle and what does it cost annually?"
> "Would adding an x86 node make sense for my current workloads?"

---

### Purchasing / Warranty `[M2]`
`GET /api/ai-context/purchasing`

Planned assets with current prices, budget remaining per project, warranty
expiry dates, and retailer details for active assets.

**Use for:**
> "What should I prioritise buying before Prime Day?"
> "Which assets have warranty expiring in the next 6 months?"
> "Am I within budget for the PCB2-V2 upgrade?"

---

## UI Flow

The "Generate AI Context" button appears:
- In the top nav (global, profile picker)
- On each Project Summary card (pre-selects Build Planning for that project)
- On the Specs table (pre-selects Specs/Compat)

Selecting a profile opens a modal showing:
1. Profile name and description
2. Rendered markdown preview (scrollable)
3. **Copy to clipboard** button
4. **Download .md** button

The copy button is the primary action — paste directly into Claude, ChatGPT,
or any AI chat.

---

## Format

All profiles are rendered as fenced markdown tables. No prose padding, no
preamble, no section headers beyond what the AI needs to parse the data.

The goal is maximum signal, minimum noise. An AI reading the profile should
be able to answer a compatibility question without clarifying questions.

Example (Specs profile, partial):

```markdown
| part_uid | name | socket_interface | form_factor | tdp_watt | ram_gen | pcie_gen | chipset | slots_used | slots_total | compat_notes |
|---|---|---|---|---|---|---|---|---|---|---|
| PCB2V2-CPU-001 | AMD Ryzen 7 9800X3D | AM5 | — | 120W | DDR5 | PCIe 5.0 | B850/X870 | — | — | 3D V-Cache. Requires DDR5. AM5 socket. |
| PCB2V2-MOB-001 | MSI MAG B850 Tomahawk Max WIFI DDR5 | AM5 | ATX | — | DDR5 | PCIe 5.0 x16 | B850 | 2/4 | 4 | DDR5 only. 2× M.2 PCIe 5.0. Verify BIOS for 9800X3D. |
| PCB2V2-GPU-001 | MSI RTX 5070 Ti Shadow 3X OC 16GB | PCIe 5.0 x16 | 3-slot | 300W | — | PCIe 5.0 | — | 1 | 1 | ~340mm length. Needs 3× 8-pin or 1× 16-pin. |
```

---

## Adding a New Profile

Profiles are rendered by `services/ai_context.py`. Each profile is a
function that:
1. Queries the DB for the relevant assets/specs
2. Renders them as a markdown table
3. Returns a string

Adding a new profile:
1. Add a function in `services/ai_context.py`
2. Add a route in `routers/io.py`
3. Add it to the profile picker in `templates/partials/ai-context-modal.html`

No other changes needed.
