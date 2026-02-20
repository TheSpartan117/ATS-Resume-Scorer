# OnlyOffice Integration Architecture

## System Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                     ATS Resume Scorer System                           │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                         Frontend Layer                            │ │
│  │                    (React + TypeScript)                           │ │
│  │                                                                    │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌───────────────────┐  │ │
│  │  │                │  │                │  │                   │  │ │
│  │  │  EditorPage    │  │ ResumeEditor   │  │ ResumeViewerTabs  │  │ │
│  │  │  Component     │─▶│  Component     │─▶│    Component      │  │ │
│  │  │                │  │                │  │                   │  │ │
│  │  └────────────────┘  └────────────────┘  └─────────┬─────────┘  │ │
│  │                                                      │            │ │
│  │                                           ┌──────────┴─────────┐ │ │
│  │                                           │                    │ │ │
│  │                                           │ OnlyOfficeEditor   │ │ │
│  │                                           │    Component       │ │ │
│  │                                           │                    │ │ │
│  │                                           └──────────┬─────────┘ │ │
│  └───────────────────────────────────────────────────────┼──────────┘ │
│                                                           │            │
│                                             ┌─────────────┴─────────┐  │
│                                             │  OnlyOffice JS API    │  │
│                                             │  (Loaded from CDN)    │  │
│                                             └─────────────┬─────────┘  │
│                                                           │            │
│         ┌──────────────────────────────────────────────────────────┐  │
│         │                   HTTP/HTTPS + JWT                       │  │
│         └──────────────────────────────────────────────────────────┘  │
│                            │                         │                │
│  ┌─────────────────────────┴──────────┐    ┌────────┴──────────────┐ │
│  │         Backend Layer              │    │   Document Server     │ │
│  │      (FastAPI + Python)            │    │   Layer (Docker)      │ │
│  │                                    │    │                       │ │
│  │  ┌──────────────────────────────┐ │    │  ┌─────────────────┐ │ │
│  │  │   /api/onlyoffice/*          │ │    │  │                 │ │ │
│  │  │                              │ │    │  │   OnlyOffice    │ │ │
│  │  │  - config/{session_id}       │◄├────┼──│   Document      │ │ │
│  │  │  - download/{session_id}     │ │    │  │   Server        │ │ │
│  │  │  - callback                  │ ├────┼─▶│                 │ │ │
│  │  │  - upload/{session_id}       │ │    │  │   Port 8080     │ │ │
│  │  │  - health                    │ │    │  │                 │ │ │
│  │  │                              │ │    │  └─────────────────┘ │ │
│  │  └──────────────────────────────┘ │    │                       │ │
│  │               │                    │    └───────────────────────┘ │
│  │               ▼                    │                               │
│  │  ┌──────────────────────────────┐ │                               │
│  │  │   Document Storage           │ │                               │
│  │  │   backend/data/              │ │                               │
│  │  │                              │ │                               │
│  │  │   - session1.docx            │ │                               │
│  │  │   - session2.docx            │ │                               │
│  │  │   - ...                      │ │                               │
│  │  └──────────────────────────────┘ │                               │
│  └─────────────────────────────────┘                                 │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

## Request Flow Diagrams

### 1. Document Loading Flow

```
User                Frontend              Backend               OnlyOffice
 │                     │                     │                      │
 │  Upload DOCX        │                     │                      │
 ├────────────────────▶│                     │                      │
 │                     │                     │                      │
 │                     │  POST /upload       │                      │
 │                     │  (DOCX file)        │                      │
 │                     ├────────────────────▶│                      │
 │                     │                     │                      │
 │                     │  ◄─────────────────┤                      │
 │                     │  {session_id}       │                      │
 │                     │                     │                      │
 │  Click Edit         │                     │                      │
 ├────────────────────▶│                     │                      │
 │                     │                     │                      │
 │                     │  POST /config/{id}  │                      │
 │                     ├────────────────────▶│                      │
 │                     │                     │                      │
 │                     │                     │  Generate JWT        │
 │                     │                     │  Build config        │
 │                     │                     │                      │
 │                     │  ◄─────────────────┤                      │
 │                     │  {config + JWT}     │                      │
 │                     │                     │                      │
 │                     │  Load OnlyOffice    │                      │
 │                     │  with config        │                      │
 │                     ├─────────────────────┼─────────────────────▶│
 │                     │                     │                      │
 │                     │  GET /download/{id} │  Verify JWT          │
 │                     │  (from OnlyOffice)  │  Load document       │
 │                     │                     ◄──────────────────────┤
 │                     │                     │                      │
 │                     │                     ├─────────────────────▶│
 │                     │                     │  DOCX file           │
 │                     │                     │                      │
 │  ◄─────────────────┬┴─────────────────────┴─────────────────────┤
 │  Document ready    │                   Editor loaded             │
 │                                                                   │
```

### 2. Document Editing and Save Flow

```
User                Frontend              Backend               OnlyOffice
 │                     │                     │                      │
 │  Edit document      │                     │                      │
 ├────────────────────▶│                     │                      │
 │                     │                     │  Editing...          │
 │                     │                     │                      │
 │                     │                     │  (5 seconds pass)    │
 │                     │                     │                      │
 │                     │                     │  POST /callback      │
 │                     │                     │  {status: 2,         │
 │                     │                     │   url: doc_url,      │
 │                     │                     │   key: doc_key}      │
 │                     │                     ◄──────────────────────┤
 │                     │                     │                      │
 │                     │                     │  Download doc        │
 │                     │                     ├─────────────────────▶│
 │                     │                     │                      │
 │                     │                     ◄──────────────────────┤
 │                     │                     │  DOCX content        │
 │                     │                     │                      │
 │                     │                     │  Save to disk        │
 │                     │                     │  backend/data/       │
 │                     │                     │                      │
 │                     │                     ├─────────────────────▶│
 │                     │                     │  {error: 0}          │
 │                     │                     │                      │
 │  Continue editing   │                     │                      │
 ├────────────────────▶│                     │                      │
 │                     │                     │                      │
```

### 3. JWT Authentication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    JWT Authentication                        │
└─────────────────────────────────────────────────────────────┘

Frontend                Backend                OnlyOffice Server
   │                       │                          │
   │  Request config       │                          │
   ├──────────────────────▶│                          │
   │                       │                          │
   │                       │  Build config:           │
   │                       │  {                       │
   │                       │    document: {...},      │
   │                       │    editorConfig: {...}   │
   │                       │  }                       │
   │                       │                          │
   │                       │  Sign with secret:       │
   │                       │  jwt.encode(config,      │
   │                       │    JWT_SECRET)           │
   │                       │                          │
   │                       │  Add token to config:    │
   │                       │  config.token = token    │
   │                       │                          │
   │  ◄────────────────────┤                          │
   │  {config + token}     │                          │
   │                       │                          │
   │  Initialize editor    │                          │
   │  with token           │                          │
   ├───────────────────────┼─────────────────────────▶│
   │                       │                          │
   │                       │                          │  Verify token:
   │                       │                          │  jwt.verify(
   │                       │                          │    token,
   │                       │                          │    JWT_SECRET
   │                       │                          │  )
   │                       │                          │
   │                       │                          │  ✓ Valid
   │                       │                          │
   │  ◄───────────────────┴──────────────────────────┤
   │         Editor loads successfully                │
   │                                                   │
```

## Component Interaction

### Frontend Components Hierarchy

```
EditorPage
  └── ResumeEditor
      └── ResumeViewerTabs
          ├── OnlyOfficeEditor (default tab)
          ├── DocxViewer (preview tab)
          └── TiptapEditor (structure editor tab)
```

### State Management

```
┌─────────────────────────────────────────────────────────────┐
│                      EditorPage State                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  - editorContent: string           (HTML content)           │
│  - currentScore: ScoreResult       (ATS score)              │
│  - originalDocxFile: File          (uploaded DOCX)          │
│  - onlyOfficeSessionId: string     (unique session)         │
│  - isRescoring: boolean            (loading state)          │
│  - isSaving: boolean               (save state)             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
        │
        ├─── Passed to ResumeEditor ────┐
        │                                │
        ▼                                ▼
┌──────────────────────┐    ┌───────────────────────┐
│   ResumeEditor       │    │  ResumeViewerTabs     │
│   Props              │    │  Props                │
├──────────────────────┤    ├───────────────────────┤
│ - value              │    │ - sessionId           │
│ - onChange           │    │ - originalDocx        │
│ - currentScore       │    │ - htmlContent         │
│ - sessionId          │    │ - onHtmlChange        │
│ - originalDocxFile   │    │                       │
└──────────────────────┘    └───────────────────────┘
                                     │
                                     ├─── Tab Selection ────┐
                                     │                       │
                                     ▼                       ▼
                        ┌─────────────────────┐   ┌───────────────────┐
                        │ OnlyOfficeEditor    │   │ Other Editors     │
                        ├─────────────────────┤   ├───────────────────┤
                        │ - sessionId         │   │ - DocxViewer      │
                        │ - onDocumentReady   │   │ - TiptapEditor    │
                        │ - onError           │   │                   │
                        └─────────────────────┘   └───────────────────┘
```

## Data Flow

### Document Upload to Editing

```
┌──────────────┐
│ User uploads │
│    DOCX      │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│ Store in localStorage        │
│ - base64 encoded             │
│ - filename                   │
│ - filetype                   │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ EditorPage loads             │
│ - Decode base64              │
│ - Create File object         │
│ - Generate session ID        │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Upload to OnlyOffice         │
│ POST /api/onlyoffice/upload  │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Save to backend/data/        │
│ {session_id}.docx            │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Initialize editor            │
│ - Request config             │
│ - Load OnlyOffice API        │
│ - Create editor instance     │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ User edits document          │
│ - Real-time editing          │
│ - Auto-save every 5s         │
│ - All Word features          │
└──────────────────────────────┘
```

### Auto-Save Mechanism

```
                    Time: 0s
                       │
                       ▼
            ┌──────────────────┐
            │ User edits       │
            │ document         │
            └────────┬─────────┘
                     │
                     │ Time: 5s
                     ▼
            ┌──────────────────┐
            │ OnlyOffice       │
            │ triggers save    │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ POST /callback   │
            │ status: 2        │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Backend          │
            │ downloads doc    │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Save to disk     │
            │ backend/data/    │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Return success   │
            │ {error: 0}       │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Continue editing │
            │ (no interruption)│
            └──────────────────┘
```

## Security Architecture

### Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Security Layers                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: CORS Protection                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Only allowed origins can access API                   │  │
│  │ Configured in backend CORS middleware                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  Layer 2: JWT Authentication                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ All OnlyOffice requests signed with JWT               │  │
│  │ Secret key shared between backend and OnlyOffice      │  │
│  │ Token verification on every request                   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  Layer 3: Session-Based Access                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Unique session ID per document                        │  │
│  │ No direct file path exposure                          │  │
│  │ Backend controls all file access                      │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  Layer 4: File System Isolation                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Documents stored in controlled directory              │  │
│  │ OnlyOffice runs in Docker container                   │  │
│  │ No direct file system access from frontend            │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "documentType": "word",
    "document": {
      "fileType": "docx",
      "key": "unique-document-key",
      "title": "resume.docx",
      "url": "http://localhost:8000/api/onlyoffice/download/session123",
      "permissions": {
        "edit": true,
        "download": true,
        "comment": true,
        "fillForms": true,
        "modifyFilter": true,
        "modifyContentControl": true,
        "review": true,
        "print": true
      }
    },
    "editorConfig": {
      "callbackUrl": "http://localhost:8000/api/onlyoffice/callback",
      "mode": "edit",
      "lang": "en",
      "user": {
        "id": "session123",
        "name": "User"
      }
    }
  },
  "signature": "HMACSHA256(base64UrlEncode(header) + '.' + base64UrlEncode(payload), secret)"
}
```

## Network Architecture

### Development Environment

```
┌────────────────────────────────────────────────────────────┐
│                    Developer Machine                        │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │              │  │              │  │                 │  │
│  │  Frontend    │  │  Backend     │  │  Docker         │  │
│  │  (Vite)      │  │  (FastAPI)   │  │  (OnlyOffice)   │  │
│  │              │  │              │  │                 │  │
│  │  Port 3000   │  │  Port 8000   │  │  Port 8080      │  │
│  │  or 5173     │  │              │  │                 │  │
│  │              │  │              │  │                 │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘  │
│         │                 │                    │           │
│         └─────────────────┴────────────────────┘           │
│                    localhost network                       │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### Production Environment

```
                        Internet
                           │
                           │ HTTPS
                           ▼
                    ┌────────────┐
                    │  Nginx     │
                    │  Reverse   │
                    │  Proxy     │
                    │  (SSL)     │
                    └──────┬─────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       ┌────────────┐          ┌─────────────┐
       │  Frontend  │          │   Backend   │
       │  (Static)  │          │   (API)     │
       │            │          │             │
       │  Port 80   │          │  Port 8000  │
       └────────────┘          └──────┬──────┘
                                      │
                                      │ Internal
                                      ▼
                              ┌─────────────┐
                              │ OnlyOffice  │
                              │ Document    │
                              │ Server      │
                              │             │
                              │  Port 8080  │
                              │  (internal) │
                              └─────────────┘
```

## Error Handling Flow

```
┌──────────────────────────────────────────────────────────────┐
│                   Error Handling Strategy                     │
└──────────────────────────────────────────────────────────────┘

Error Occurs
     │
     ├─── Frontend Error ────────┐
     │                            │
     │                            ▼
     │                   ┌──────────────────┐
     │                   │ Show error UI    │
     │                   │ with message     │
     │                   └────────┬─────────┘
     │                            │
     │                            ▼
     │                   ┌──────────────────┐
     │                   │ Troubleshooting  │
     │                   │ tips displayed   │
     │                   └────────┬─────────┘
     │                            │
     │                            ▼
     │                   ┌──────────────────┐
     │                   │ Fallback to      │
     │                   │ Preview tab      │
     │                   └──────────────────┘
     │
     ├─── Backend Error ─────────┐
     │                            │
     │                            ▼
     │                   ┌──────────────────┐
     │                   │ Log error        │
     │                   │ with details     │
     │                   └────────┬─────────┘
     │                            │
     │                            ▼
     │                   ┌──────────────────┐
     │                   │ Return error     │
     │                   │ response         │
     │                   └────────┬─────────┘
     │                            │
     │                            ▼
     │                   ┌──────────────────┐
     │                   │ Frontend handles │
     │                   │ error gracefully │
     │                   └──────────────────┘
     │
     └─── OnlyOffice Error ──────┐
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Callback with    │
                         │ error status     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Backend logs     │
                         │ and retries      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ User notified    │
                         │ if needed        │
                         └──────────────────┘
```

## Performance Considerations

### Resource Usage

```
┌─────────────────────────────────────────────────────────────┐
│                    Resource Requirements                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  OnlyOffice Container:                                      │
│  - CPU: 2+ cores recommended                                │
│  - RAM: 2GB minimum, 4GB recommended                        │
│  - Disk: 2GB for application, 10GB+ for documents           │
│  - Network: Low latency to backend                          │
│                                                              │
│  Backend:                                                    │
│  - CPU: 1+ core                                             │
│  - RAM: 512MB minimum                                       │
│  - Disk: Storage for documents                              │
│  - Network: Fast connection to OnlyOffice                   │
│                                                              │
│  Frontend:                                                   │
│  - Browser: Modern browser (Chrome, Firefox, Safari, Edge)  │
│  - Network: Stable connection to backend and OnlyOffice     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Optimization Strategies

1. **Auto-save interval**: 5 seconds (configurable)
2. **Callback timeout**: 30 seconds
3. **Document caching**: Based on modification time
4. **Lazy loading**: OnlyOffice API loaded on demand
5. **Error recovery**: Automatic retry on failures

---

This architecture provides a robust, secure, and scalable solution for document editing in the ATS Resume Scorer application.
