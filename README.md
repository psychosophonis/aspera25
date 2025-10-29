# ASPERA 2025 Conference Navigator

Clean, modernist single-page web application for navigating the ASPERA 2025 Conference program.

## Features

- **Visual Event Categorization**: Color-coded panels and presentations
- **Panel Descriptions**: Concise summaries using authors' terminology
- **Reading Mode**: Full-screen overlay for comfortable reading
- **Responsive Design**: Optimized for mobile and desktop
- **Search & Filter**: Full-text search, day/venue filtering
- **Form/Content Separation**: All content in editable JSON file

## Files

- `index.html` - Single-file application (HTML, CSS, JavaScript)
- `conference-data.json` - All conference content (editable)
- `DEPLOYMENT.md` - GitHub Pages deployment guide with QR code instructions
- `SUMMARY.md` - Complete overview of features and structure

## Usage

**Local testing:**
1. Place `index.html` and `conference-data.json` in same folder
2. Open `index.html` in browser

**Production deployment:**
1. Follow instructions in `DEPLOYMENT.md`
2. Deploy to GitHub Pages (free, automatic HTTPS)
3. Generate QR codes for venue entrances

## Architecture

**Pure vanilla JavaScript** - No frameworks  
**Tailwind CSS** - Styling via CDN  
**JSON data file** - All content separate from code  
**Static HTML** - No server required

## Event Types

- **Panel Sessions** (Blue) - Multi-paper research panels
- **Presentations** (Cyan) - Single-presenter sessions
- **ASPERA Panels** (Purple) - Special ASPERA sessions
- **Plenary** (Amber) - Keynote presentations
- **Breaks/Meals** (Gray) - Registration, tea, lunch, dinner
- **Screening Lounge** (Pink) - Film screenings

## Editing Content

Edit `conference-data.json` to update:
- Event schedules
- Paper titles and abstracts
- Presenter information
- Panel descriptions

No HTML changes needed. All content managed via JSON.

## Conference Information

**Event**: ASPERA 2025 Conference - Experiments in Screen  
**Dates**: 25-27 November 2025  
**Location**: Wollongong, NSW, Australia  
**Venues**: Rooms 29.G10, 29.G08, 29.G09, 29.G07

## License

Created for ASPERA 2025 Conference
