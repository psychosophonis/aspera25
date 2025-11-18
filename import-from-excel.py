#!/usr/bin/env python3
"""
Hybrid parser: Single source of truth with inline additions
- Participants sheet = master registry
- Other sheets: plain names OR Name (Institution) for new people
- Smart parsing that detects format and looks up existing
"""

import json
import math
import pandas as pd
import re
from pathlib import Path

def is_blank(value):
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False

def clean_text(value, default=""):
    if is_blank(value):
        return default
    return str(value).strip()

def format_time_value(value):
    if is_blank(value):
        return ""
    if isinstance(value, (int, float)):
        return f"{int(value):04d}"
    text = str(value).strip()
    if text.isdigit() and len(text) <= 4:
        return text.zfill(4)
    return text

def parse_name_with_institution(name_str):
    """
    Parse 'Name (Institution)' or just 'Name'
    Returns: (name, institution or None)
    """
    if is_blank(name_str):
        return "", None
    name_str = str(name_str)
    match = re.match(r'^(.+?)\s*\(([^)]+)\)\s*$', name_str.strip())
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return name_str.strip(), None

def parse_names(names_str):
    """Parse 'Name; Name (Institution); Name' into list of name strings"""
    if pd.isna(names_str) or not names_str:
        return []
    return [n.strip() for n in str(names_str).split(';') if n.strip()]

def main():
    xlsx_path = Path("conference-data.xlsx")
    json_path = Path("conference-data.json")
    output_path = Path("conference-data-updated.json")
    warnings = []
    
    if not xlsx_path.exists():
        print(f"❌ Error: {xlsx_path} not found")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        original = json.load(f)
    
    print("📖 Reading Excel workbook...")
    participants_df = pd.read_excel(xlsx_path, sheet_name='Participants')
    sessions_df = pd.read_excel(xlsx_path, sheet_name='Sessions & Papers')
    events_df = pd.read_excel(xlsx_path, sheet_name='Events')
    screenings_df = pd.read_excel(xlsx_path, sheet_name='Screenings')
    
    # =================================================================
    # Build name → institution lookup from Participants (master registry)
    # =================================================================
    print("🔍 Building participant registry...")
    participant_lookup = {}
    for idx, row in participants_df.iterrows():
        name = row.get('Name')
        if is_blank(name):
            excel_row = idx + 2  # header is row 1
            warnings.append(f"Participants sheet row {excel_row} has a blank Name; skipping.")
            continue
        name = clean_text(name)
        inst = row.get('Institution')
        participant_lookup[name] = inst if not is_blank(inst) else None
    
    print(f"   • Loaded {len(participant_lookup)} existing participants")
    
    new_participants = []
    
    def smart_lookup_people(names_list):
        """
        Smart parser:
        1. Check if name exists in Participants registry
        2. If not, check if it has inline institution: Name (Institution)
        3. Add new people to registry automatically
        """
        result = []
        for name_str in names_list:
            if is_blank(name_str):
                continue
            # Parse potential inline institution
            clean_name, inline_inst = parse_name_with_institution(name_str)
            clean_name = clean_text(clean_name)
            if not clean_name:
                continue
            
            # Check registry first
            if clean_name in participant_lookup:
                # Existing person - use registry institution
                result.append({
                    "name": clean_name,
                    "institution": participant_lookup[clean_name]
                })
            else:
                # New person
                if not is_blank(inline_inst):
                    # Has inline institution - use it
                    participant_lookup[clean_name] = inline_inst
                    new_participants.append((clean_name, inline_inst))
                    result.append({
                        "name": clean_name,
                        "institution": inline_inst
                    })
                    print(f"   ➕ New: {clean_name} ({inline_inst})")
                else:
                    # No institution provided
                    participant_lookup[clean_name] = None
                    new_participants.append((clean_name, None))
                    result.append({
                        "name": clean_name,
                        "institution": None
                    })
                    print(f"   ⚠️  New (no institution): {clean_name}")
        
        return result
    
    # =================================================================
    # Rebuild sessions
    # =================================================================
    print("\n🔄 Processing sessions and papers...")
    sessions = {}
    current_session = None
    original_panel_descriptions = (original.get('panel_descriptions') or {})
    
    for _, row in sessions_df.iterrows():
        session_num = row.get('Session #', '')
        
        if isinstance(session_num, str) and session_num.startswith('SESSION'):
            sid = session_num.replace('SESSION', '').strip()
            current_session = sid
            
            presenter_names = parse_names(row.get('Presenters/Authors', ''))
            
            description = clean_text(row.get('Description', ''))
            if not description and original_panel_descriptions:
                description = clean_text(original_panel_descriptions.get(sid, ''))

            sessions[sid] = {
                "type": clean_text(row.get('Type', '')),
                "title": clean_text(row.get('Title', '')),
                "description": description,
                "presenters": smart_lookup_people(presenter_names),
                "papers": []
            }
        
        elif row.get('Type') == 'paper' and current_session:
            author_names = parse_names(row.get('Presenters/Authors', ''))
            
            paper = {
                "title": clean_text(row.get('Title', '')),
                "abstract": clean_text(row.get('Abstract', '')),
                "authors": smart_lookup_people(author_names)
            }
            sessions[current_session]["papers"].append(paper)
    
    # =================================================================
    # Rebuild events
    # =================================================================
    print("\n🔄 Processing events...")
    events = []
    
    for _, row in events_df.iterrows():
        day_val = clean_text(row.get('Day', ''))
        time_val = format_time_value(row.get('Time', ''))
        venue_val = clean_text(row.get('Venue', ''))
        content_val = clean_text(row.get('Content', ''))
        type_val = clean_text(row.get('Type', ''))

        # Skip completely blank rows (prevents phantom days)
        if not any([day_val, time_val, venue_val, content_val, type_val]):
            continue

        event = {
            "day": day_val,
            "time": time_val,
            "venue": venue_val,
            "content": content_val,
            "session_num": None,
            "headshot_url": None,
            "logo_url": None,
            "type": type_val
        }
        
        presenter_names = parse_names(row.get('Presenters', ''))
        if presenter_names:
            event['presenters'] = smart_lookup_people(presenter_names)
        
        if event['type'] == 'plenary' and 'Abstract' in row:
            abstract = clean_text(row.get('Abstract', ''))
            if abstract:
                event['abstract'] = abstract
        
        # Match with original for session_num and affiliation
        for orig_event in original.get('events', []):
            if (orig_event.get('time') == event['time'] and 
                orig_event.get('venue') == event['venue'] and
                orig_event.get('day') == event['day']):
                if 'session_num' in orig_event:
                    event['session_num'] = orig_event['session_num']
                if 'affiliation' in orig_event:
                    event['affiliation'] = orig_event['affiliation']
                break
        
        events.append(event)
    
    # Drop events that reference sessions removed from Excel (but keep screenings with no films)
    filtered_events = []
    for event in events:
        session_num = event.get('session_num')
        if session_num and session_num not in sessions:
            warnings.append(
                f"Event '{event['content']}' ({event['day']} @ {event['time']} in {event['venue']}) "
                f"references missing session {session_num}; event removed."
            )
            continue
        filtered_events.append(event)
    events = filtered_events

    # =================================================================
    # Process screenings
    # =================================================================
    print("\n🔄 Processing screenings...")
    
    current_slot = None
    screening_films = {}
    
    for _, row in screenings_df.iterrows():
        slot_id = row.get('Screening Slot', '')
        
        if not is_blank(slot_id):
            current_slot = str(slot_id).strip()
            if current_slot not in screening_films:
                screening_films[current_slot] = []

        elif current_slot and not is_blank(row.get('Film Title')):
            creative_names = parse_names(row.get('Creatives', ''))
            
            film = {
                "title": clean_text(row.get('Film Title', '')),
                "year": int(row.get('Year', 0)) if not is_blank(row.get('Year')) else None,
                "duration": int(row.get('Duration (mins)', 0)) if not is_blank(row.get('Duration (mins)')) else None,
                "creatives": smart_lookup_people(creative_names)
            }
            screening_films[current_slot].append(film)
    
    # Add films to screening events
    for event in events:
        if event['type'] == 'screening':
            slot_id = f"{event['day']} - {event['time']} - {event['venue']}"
            if slot_id in screening_films:
                event['films'] = screening_films[slot_id]
    
    # =================================================================
    # Build final JSON
    # =================================================================
    output = {
        "conference": original.get('conference', {}),
        "venues": original.get('venues', []),
        "events": events,
        "sessions": sessions,
        "panel_descriptions": {
            sid: session.get('description')
            for sid, session in sessions.items()
            if session.get('description')
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Updated JSON written to: {output_path.resolve()}")
    print(f"\n📊 Summary:")
    print(f"   • {len(participant_lookup)} total participants ({len(new_participants)} new)")
    print(f"   • {len(sessions)} sessions with {sum(len(s.get('papers', [])) for s in sessions.values())} papers")
    print(f"   • {len(events)} events")
    print(f"   • {sum(len(e.get('films', [])) for e in events if e.get('type') == 'screening')} films")

    if warnings:
        print(f"\n⚠️ Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"   - {warning}")
    
    if new_participants:
        print(f"\n💡 Tip: New participants added to registry.")
        print(f"   Next export will show them as name-only in other sheets.")
        missing_inst = [name for name, inst in new_participants if inst is None]
        if missing_inst:
            print(f"\n⚠️  {len(missing_inst)} people added without institutions:")
            for name in missing_inst[:5]:
                print(f"      • {name}")
            if len(missing_inst) > 5:
                print(f"      ... and {len(missing_inst) - 5} more")
            print(f"   Consider adding institutions in Participants sheet before next export.")

if __name__ == "__main__":
    main()
