# ASPERA 2025 Conference Navigator

A minimal, clean single-page application for navigating the ASPERA 2025 Conference program.

## Architecture

- **Pure vanilla JavaScript** - No frameworks, just HTML, CSS, and JavaScript
- **JSON data file** - All conference data in a single, editable JSON file
- **Tailwind CSS** - For clean, modern styling via CDN
- **QRious** - For QR code generation via CDN

## Files

- `index.html` - Main application (single file)
- `conference-data.json` - Conference data (editable)

## Features

### 1. Visual Event Types
Events are color-coded for easy identification:
- **Panel Sessions** (light blue) - Research panels with multiple paper presentations
- **ASPERA Panels** (light purple) - Special ASPERA research/teaching panels
- **Plenary Sessions** (amber) - Keynote presentations
- **Breaks/Meals** (gray) - Registration, tea, lunch, dinner
- **Screening Lounge** (pink) - Film screenings
- **Town Hall** (indigo) - Community meetings

### 2. Search & Filter
- **Full-text search** across all presentations, authors, and abstracts
- **Day filter** - View individual days (Tuesday, Wednesday, Thursday)
- **Venue filter** - Filter by room (29.G10, 29.G08, 29.G09, 29.G07)

### 3. Panel Structure
- **Panel streams** show the theme/topic clearly
- Click **"View Papers"** to see individual presentations within each panel
- Each paper shows: title, presenter(s), and expandable abstract
- Example: "Diversity & the unexpected" panel contains 3 individual papers

### 4. Schedule Display
- Grouped by day and time
- Color-coded venue badges
- Expandable abstracts for detailed information
- Responsive grid layout

### 5. QR Code Generation
- Click "Show QR" next to any time slot
- Generates a QR code linking directly to that session
- Attendees can scan to navigate to the right session at the right time
- URLs include day and time parameters for direct navigation

### 6. Single Day Timetables
- Use the Day filter to view only Tuesday, Wednesday, or Thursday
- Share URLs with day parameter for specific days

## Usage

The app has **two modes** to maintain separation of form (HTML) and content (JSON):

### Mode 1: File Upload (No Server Required)
1. Open `index.html` directly in your browser
2. Click "Choose File" and select `conference-data.json`
3. The app loads and is ready to use

**Pros:** Works immediately, no server needed  
**Cons:** Must manually select JSON file each time

### Mode 2: Web Server (Auto-loads JSON)
Upload both files to any web server in the same directory:

```bash
# Python 3
python3 -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000

# Node.js (with http-server installed)
npx http-server

# PHP
php -S localhost:8000
```

Then visit: `http://localhost:8000`

**Pros:** JSON loads automatically, URLs work for QR codes  
**Cons:** Requires a web server

### Mode 3: GitHub Pages (Recommended for Production)

GitHub Pages is ideal for this application:

1. **Create a GitHub repository**
2. **Upload both files:**
   - `index.html`
   - `conference-data.json`
3. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Source: Deploy from main branch
   - Select root directory
4. **Access your site:**
   - `https://your-username.github.io/your-repo-name/`

**Pros:** 
- Free hosting
- HTTPS automatically
- JSON loads automatically
- Professional URLs for QR codes
- Easy to update (just commit changes to JSON)
- Version control for your data

**Example workflow:**
```bash
git clone https://github.com/your-username/aspera-2025.git
cd aspera-2025
# Edit conference-data.json
git add conference-data.json
git commit -m "Updated session times"
git push
# Changes live in ~1 minute
```

### Editing Conference Data
Edit `conference-data.json` directly. Structure:
```json
{
  "conference": { ... },
  "venues": [ ... ],
  "events": [
    {
      "day": "DAY 25/11/25\\nTUESDAY",
      "time": "1100",
      "venue": "29.G10",
      "content": "Session title and description"
    }
  ],
  "abstracts": [
    {
      "session": "1",
      "presenters": "Name / Institution",
      "title": "Paper Title",
      "abstract": "Full abstract text..."
    }
  ]
}
```

## QR Code Workflow

### For Venues
1. Filter to a specific venue (e.g., 29.G10)
2. Click "Show QR" for each time slot
3. Print QR codes
4. Post at venue entrance
5. Attendees scan to see what's happening in that room

### For Programs
1. Generate QR codes for each time slot
2. Include in printed programs
3. Attendees scan to jump to specific sessions

## URL Parameters

Direct linking with parameters:
- `?day=Tuesday%2C%20Nov%2025&time=1100` - Links to specific time slot

## Browser Requirements

- Modern browser with JavaScript enabled
- No Internet required (all assets load from CDN, but can be made fully offline if needed)

## Customization

### Colors
Venue colors are defined in `getVenueColor()` function:
```javascript
const colors = {
    '29.G10': 'bg-blue-100 text-blue-800',
    '29.G08': 'bg-green-100 text-green-800',
    // ... etc
};
```

### Styling
All Tailwind classes can be modified directly in the HTML.

## No Dependencies

Only external resources (loaded from CDN):
- Tailwind CSS (for styling)
- QRious (for QR generation)

Can be made fully offline by downloading these libraries.

## License

Created for ASPERA 2025 Conference
