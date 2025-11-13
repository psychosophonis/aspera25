# ASPERA Conference System - Technical Reference

## System Overview

Manages conference data via Excel ↔ JSON round-trip with hybrid participant registry.

**Key Feature**: Participants sheet is master registry. Other sheets use name-only format OR inline `Name (Institution)` for new people.

## Workflow

```bash
# 1. Export JSON to Excel
python3 export-to-excel.py

# 2. Edit conference-data.xlsx (4 sheets)

# 3. Import Excel to JSON
python3 import-from-excel.py
# Creates: conference-data-updated.json
# Review, then: mv conference-data-updated.json conference-data.json
```

## Excel Structure (4 Sheets)

1. **Participants** - Master registry (Name | Institution)
2. **Sessions & Papers** - Name-only format
3. **Events** - Name-only format  
4. **Screenings** - Smart format (name-only OR inline)

## Name Formats

**For existing people**: `Jo Law` (looks up institution in Participants)
**For new people**: `Jane Smith (UOW)` (parses institution, adds to Participants)
**Multiple**: `Jo Law; Jane Smith (RMIT); Bob Chen`

## Parser Logic

```python
def parse_name_with_institution(name_str):
    """Returns (name, institution) tuple"""
    match = re.match(r'^(.+?)\s*\(([^)]+)\)\s*$', name_str.strip())
    return (match.group(1).strip(), match.group(2).strip()) if match else (name_str.strip(), None)

def smart_lookup_people(names_list):
    """
    For each name:
    1. Check if exists in Participants registry → use that institution
    2. Else: parse inline institution if present → add to registry
    3. Else: add with null institution → warn
    """
```

**Key behavior**: Participants always wins. If `Jo Law` exists in Participants with UOW, then `Jo Law (RMIT)` in other sheets still uses UOW from Participants.

## Common Tasks

**Fix institution everywhere**:
1. Export
2. Edit Participants: `Jo Law | UOW` → `University of Wollongong`
3. Import → updates all occurrences (session presenter, paper author, event presenter)

**Add screening films**:
1. Export
2. Find screening slot in Screenings sheet (e.g., "TUESDAY - 1100 - 29.G07")
3. Add film rows below with: `Creatives: Jo Law; New Person (RMIT)`
4. Import → Jo Law uses existing institution, New Person added to Participants

## Import Warnings

- `➕ New: Jane Smith (UOW)` - New person with institution (good)
- `⚠️ New (no institution): Bob Jones` - Missing institution, add in Participants

## Technical Notes

**Export**: Extracts all unique people (including from screening films) to Participants. Displays name-only in other sheets.

**Import**: Builds Participants lookup first, then smart-parses all name references. New people automatically added to registry.

**Screenings**: Slot rows have `Screening Slot` filled. Film rows below have empty `Screening Slot` with film data.

**Sessions**: SESSION rows have `Session #` starting with "SESSION". Paper rows have `Type: paper`.

## Data Structure

```json
{
  "sessions": {
    "5": {
      "presenters": [{"name": "Jo Law", "institution": "UOW"}],
      "papers": [
        {
          "title": "Paper Title",
          "authors": [{"name": "Jane Smith", "institution": "RMIT"}]
        }
      ]
    }
  },
  "events": [
    {
      "type": "screening",
      "films": [
        {
          "title": "Film Title",
          "year": 2024,
          "duration": 12,
          "creatives": [{"name": "Director", "institution": "UOW"}]
        }
      ]
    }
  ]
}
```

## Current Data

- 120 participants
- 27 sessions, 66 papers
- 57 events
- 7 empty screening slots
