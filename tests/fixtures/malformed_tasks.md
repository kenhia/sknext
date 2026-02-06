# Tasks: Malformed Test File

**Feature**: Testing Error Handling
**Branch**: `test-errors`

## Format: `- [ ] [ID] [P?] [Story?] Description`

---

## Phase 1: Valid Phase

- [ ] T001 This is a valid task

---

## Phase 2: Invalid Tasks

- [] T002 Missing space in checkbox
- [ ]T003 No space after checkbox
- [ ] 004 Missing T prefix
- [ ] T05 Too few digits in ID
* [ ] T006 Wrong bullet character
- [  ] T007 Too many spaces in checkbox

---

## Phase 3: Orphaned Content

This is some random text before a task

- [ ] T008 Orphaned task with no section

### Section Without Phase

- [ ] T009 Task in section but no phase header

---

Phase 4: Missing Hash Marks

- [ ] T010 Task under invalid phase

---

## Phase 5 Missing Colon

- [ ] T011 Task under malformed phase header

---

## Phase 6: Nested Issues

### Section A

#### Subsection A1

##### Deep Level 1

###### Deep Level 2 (level 6)

- [ ] T012 Task at excessive nesting depth
