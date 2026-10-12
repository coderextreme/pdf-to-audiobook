# Project: PDF to Audiobook Web with OAuth & Distinct Batch Conversions

Extend the PDF-to-Audiobook application (based on https://github.com/coderextreme/pdf-to-audiobook-web/) into a production-grade web application with OAuth support and a fix for batch conversion output naming.

## 1. Core Objectives & Scope
- Web-native port and extension of the desktop PDF-to-Audiobook converter.
- Support document ingestion: PDF (.pdf), EPUB (.epub), Plain Text (.txt, .text), and Markdown (.md).
- Implement OAuth authentication (Google OAuth, GitHub OAuth, and guest session fallback) with persistent user profiles and conversion history.
- Fix the batch conversion bug where batch jobs generated identically named output files with identical/overwritten contents. Each input file must produce a distinctly named output file with isolated audio synthesis.

## 2. Key Features & Requirements

### A. OAuth Authentication
- Header authentication status bar showing avatar, display name, email, and provider badge.
- Interactive OAuth modal supporting Google OAuth, GitHub OAuth, and an offline guest mode.
- In-memory token management and session persistence with clean sign-out.
- Queue jobs and converted audio files tied to the authenticated user account.

### B. Batch Conversion Engine (Bug Fix)
- Problem to eliminate: Batch conversions sharing a single output filename or shared closure state, causing files to overwrite one another.
- Automated distinct naming:
  - Sanitize and derive each file's base name: `<basename>_audiobook.mp3`.
  - Enforce collision prevention within the batch by appending incrementing indices (`<basename>_(1)_audiobook.mp3`, etc.).
  - Completely isolate text extraction and TTS generation per file so each output contains distinct audio matching its source document.
  - Multi-file selection and folder import (`webkitdirectory`).
  - Batch progress table with individual progress bars, editable output names, and playback buttons.
  - "Download All as ZIP" archive packaging all converted files under their distinct names.

### C. Single File Conversion Tab
- Document picker with instant word count and text preview.
- Voice selection with Kokoro acoustic profiles (`af_heart`, `af_bella`, `af_sarah`, `am_adam`, `am_michael`, `bf_emma`, `bm_george`).
- Conversion speed multipliers (0.75x to 2.0x).
- Real-time progress updates through extraction, synthesis, and audio encoding.

### D. Audio Player & Queue
- Bottom persistent audio player bar with scrubber, 10s skip controls, speed toggle, volume mute, and direct download.
- Global queue and conversion history panel tracking pending, running, completed, and error states.

### E. Design & Styling
- Precision studio dark theme (`#0e0e0f` base, `#161618` surfaces, `#2e2e33` borders).
- Neon amber accents (`#f5a623`) with monospace status details and clean typography.

