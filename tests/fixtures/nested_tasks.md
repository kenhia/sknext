# Tasks: Deep Nesting Test

**Feature**: Testing Nesting Depth Limits
**Branch**: `test-nesting`

## Format: `- [ ] [ID] [P?] [Story?] Description`

---

## Phase 1: Normal Depth

### Level 3 Section

- [ ] T001 Task at normal depth

---

## Phase 2: Deep Nesting

### Level 3 Section

#### Level 4 Subsection

- [ ] T002 Task at level 4

##### Level 5 Deep Section

- [ ] T003 Task at level 5 (MAX_NESTING_DEPTH)

###### Level 6 Very Deep Section

- [ ] T004 Task at level 6 (exceeds MAX_NESTING_DEPTH of 5)

####### Level 7 Extremely Deep

- [ ] T005 Task at level 7 (way beyond limit)

---

## Phase 3: Mixed Depths

### Normal Section

- [ ] T006 Normal task

##### Suddenly Deep

- [ ] T007 Skipped levels (jumped from 3 to 5)

### Back to Normal

- [ ] T008 Normal depth again
