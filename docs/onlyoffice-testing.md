# OnlyOffice Integration Testing Guide

## Testing Checklist

Use this comprehensive checklist to verify the OnlyOffice integration is working correctly.

## Pre-Testing Setup

### Prerequisites Verification

- [ ] Docker installed and running
- [ ] Docker Compose installed
- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] Git repository cloned
- [ ] At least 3GB free RAM
- [ ] Ports 8000, 8080, and 3000/5173 available

### Installation Steps

```bash
# 1. Clone repository (if not already)
cd /Users/sabuj.mondal/ats-resume-scorer

# 2. Run setup script
./setup-onlyoffice.sh    # On Mac/Linux
# OR
setup-onlyoffice.bat     # On Windows

# 3. Verify OnlyOffice is running
docker ps | grep onlyoffice
```

## Unit Tests

### 1. Docker Container Tests

#### Test 1.1: Container Status
```bash
# Should show onlyoffice-documentserver running
docker ps

# Expected output:
# CONTAINER ID   IMAGE                            STATUS
# xxxxx          onlyoffice/documentserver:latest Up X minutes
```
- [ ] Container is running
- [ ] Status shows "Up" with no restarts
- [ ] Port 8080:80 is mapped

#### Test 1.2: Container Logs
```bash
# View logs
docker-compose logs onlyoffice-documentserver

# Should see:
# - No error messages
# - "docservice: server started" or similar
```
- [ ] No critical errors in logs
- [ ] Service started successfully
- [ ] No port binding errors

#### Test 1.3: OnlyOffice Welcome Page
```bash
# Open in browser
open http://localhost:8080/welcome

# Or use curl
curl -I http://localhost:8080/welcome
```
- [ ] Welcome page loads (HTTP 200)
- [ ] OnlyOffice logo visible
- [ ] Version information displayed

### 2. Backend API Tests

#### Test 2.1: Health Check
```bash
# Test health endpoint
curl http://localhost:8000/api/onlyoffice/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "onlyoffice_server": "http://localhost:8080",
  "message": "OnlyOffice Document Server is accessible"
}
```
- [ ] Returns HTTP 200
- [ ] Status is "healthy"
- [ ] Message confirms accessibility

#### Test 2.2: Document Upload
```bash
# Create test document
echo "Test document" > /tmp/test.txt
curl -X POST http://localhost:8000/api/onlyoffice/upload/test123 \
  --data-binary @/tmp/test.txt
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Document uploaded successfully",
  "session_id": "test123"
}
```
- [ ] Returns HTTP 200
- [ ] Success is true
- [ ] Session ID returned

#### Test 2.3: Config Generation
```bash
# Request editor config
curl -X POST http://localhost:8000/api/onlyoffice/config/test123
```

**Expected Response Structure:**
```json
{
  "documentType": "word",
  "document": {
    "fileType": "docx",
    "key": "...",
    "title": "test123.docx",
    "url": "http://localhost:8000/api/onlyoffice/download/test123",
    "permissions": { ... }
  },
  "editorConfig": {
    "callbackUrl": "http://localhost:8000/api/onlyoffice/callback",
    "mode": "edit",
    "user": { ... }
  },
  "token": "..."
}
```
- [ ] Returns HTTP 200
- [ ] Has documentType field
- [ ] Has document.url field
- [ ] Has editorConfig.callbackUrl
- [ ] Has token field (JWT)

#### Test 2.4: Document Download
```bash
# Download test document
curl -O http://localhost:8000/api/onlyoffice/download/test123
```
- [ ] Returns HTTP 200
- [ ] File downloads successfully
- [ ] Content-Type is correct
- [ ] File size > 0

### 3. Frontend Component Tests

#### Test 3.1: OnlyOffice Component Loads
1. Start frontend: `cd frontend && npm run dev`
2. Open browser: `http://localhost:3000`
3. Check console for errors

- [ ] No JavaScript errors in console
- [ ] OnlyOffice component file found
- [ ] No missing dependencies errors

#### Test 3.2: Editor Page Navigation
1. Navigate to `/editor` (or upload a resume first)
2. Check page loads

- [ ] Page loads without errors
- [ ] Tabs are visible
- [ ] OnlyOffice Editor tab is present
- [ ] OnlyOffice is default/active tab

#### Test 3.3: OnlyOffice Script Loading
1. Open browser DevTools Network tab
2. Navigate to editor page
3. Check for OnlyOffice API script

- [ ] Script loads from `http://localhost:8080/web-apps/apps/api/documents/api.js`
- [ ] Script loads successfully (HTTP 200)
- [ ] No CORS errors

## Integration Tests

### 4. End-to-End Document Editing

#### Test 4.1: Upload Document
1. Go to homepage
2. Click "Upload Resume" or similar
3. Select a DOCX file (test resume)
4. Wait for upload to complete

- [ ] File uploads successfully
- [ ] Progress indicator shows
- [ ] Success message appears
- [ ] Redirected to results or editor page

#### Test 4.2: Open Editor
1. From results page, click "Edit Resume"
2. Wait for editor to load

- [ ] Editor page loads
- [ ] OnlyOffice Editor tab is active
- [ ] Loading spinner shows "Loading OnlyOffice Editor..."

#### Test 4.3: Editor Initialization
1. Wait for editor to fully load
2. Document should appear

- [ ] Loading spinner disappears
- [ ] Document content visible
- [ ] Toolbar with Word features visible
- [ ] No error messages

**Timing:** Should load within 5-10 seconds

#### Test 4.4: Document Editing
1. Click in document
2. Type some text
3. Use formatting tools (bold, italic, etc.)
4. Insert a bullet list
5. Change font size

- [ ] Can type in document
- [ ] Text appears immediately
- [ ] Formatting toolbar works
- [ ] Bold/italic/underline work
- [ ] Lists can be created
- [ ] Font changes apply
- [ ] No lag or freezing

#### Test 4.5: Auto-Save
1. Edit document
2. Wait 10 seconds
3. Check backend logs for callback

```bash
# Check backend logs
# Should see: "Received callback: status=2"
```

- [ ] Backend receives save callback
- [ ] Status is 2 (ready for saving)
- [ ] Document URL provided
- [ ] File saved to backend/data/
- [ ] No errors in logs

#### Test 4.6: Tab Switching
1. Edit in OnlyOffice tab
2. Switch to "Preview" tab
3. Switch to "Structure Editor" tab
4. Switch back to OnlyOffice

- [ ] Preview tab shows document
- [ ] Structure Editor shows content
- [ ] OnlyOffice tab still works
- [ ] No data loss between tabs
- [ ] Each tab displays correctly

### 5. Error Handling Tests

#### Test 5.1: OnlyOffice Server Down
1. Stop OnlyOffice: `docker-compose down`
2. Try to open editor
3. Check error handling

- [ ] Error message appears
- [ ] Troubleshooting tips shown
- [ ] Fallback to Preview tab offered
- [ ] No browser crash
- [ ] User can still navigate away

#### Test 5.2: Network Timeout
1. Block OnlyOffice port temporarily
2. Try to load editor
3. Check timeout handling

- [ ] Timeout error caught
- [ ] User-friendly message shown
- [ ] Retry option available (if implemented)
- [ ] Doesn't hang indefinitely

#### Test 5.3: Invalid Document
1. Upload a non-DOCX file (e.g., image)
2. Try to edit
3. Check error handling

- [ ] Error detected
- [ ] Appropriate message shown
- [ ] Backend logs error
- [ ] Frontend doesn't crash

### 6. Performance Tests

#### Test 6.1: Large Document
1. Upload a large resume (5+ pages, 50KB+)
2. Open in OnlyOffice
3. Edit the document

- [ ] Document loads (may take 10-15 seconds)
- [ ] Editing is responsive
- [ ] Scrolling works smoothly
- [ ] No browser slowdown
- [ ] Auto-save still works

**Benchmark:**
- Load time: < 15 seconds
- Typing lag: < 100ms
- Save callback: < 5 seconds

#### Test 6.2: Multiple Sessions
1. Open editor in first browser tab
2. Open same document in second tab (different session)
3. Edit in both tabs

- [ ] Both editors work independently
- [ ] No conflicts
- [ ] Both can save
- [ ] Session IDs are different

#### Test 6.3: Memory Usage
```bash
# Check Docker stats
docker stats onlyoffice-documentserver
```

- [ ] Memory usage < 2GB under normal use
- [ ] CPU usage reasonable (< 50% idle)
- [ ] No memory leaks over time

## Security Tests

### 7. Authentication Tests

#### Test 7.1: JWT Verification
1. Request config with valid session
2. Request config with invalid session
3. Check responses

- [ ] Valid session returns config
- [ ] Invalid session handled gracefully
- [ ] JWT token present in response
- [ ] Token is properly signed

#### Test 7.2: Direct File Access
```bash
# Try to access file directly
curl http://localhost:8000/backend/data/test123.docx
```

- [ ] Returns 404 or 403 (access denied)
- [ ] Cannot list directory
- [ ] Files not exposed publicly

#### Test 7.3: CORS Protection
```bash
# Try request from unauthorized origin
curl -H "Origin: http://evil.com" \
  http://localhost:8000/api/onlyoffice/health
```

- [ ] CORS headers checked
- [ ] Unauthorized origin blocked
- [ ] Only allowed origins work

### 8. Callback Tests

#### Test 8.1: Save Callback
1. Edit document in OnlyOffice
2. Wait for auto-save (5 seconds)
3. Monitor backend logs

```bash
# Should see callback logged
tail -f backend.log
```

- [ ] Callback received (status: 2)
- [ ] Document URL in callback
- [ ] Backend downloads document
- [ ] File saved correctly
- [ ] Response sent (error: 0)

#### Test 8.2: Callback Authentication
1. Send test callback without JWT
2. Check if rejected

```bash
curl -X POST http://localhost:8000/api/onlyoffice/callback \
  -H "Content-Type: application/json" \
  -d '{"status": 2, "key": "test"}'
```

- [ ] Backend validates callback
- [ ] JWT checked (if configured)
- [ ] Unauthorized requests logged

## Browser Compatibility Tests

### 9. Cross-Browser Testing

#### Test 9.1: Chrome
- [ ] Editor loads and works
- [ ] All features functional
- [ ] No console errors
- [ ] Performance acceptable

#### Test 9.2: Firefox
- [ ] Editor loads and works
- [ ] All features functional
- [ ] No console errors
- [ ] Performance acceptable

#### Test 9.3: Safari
- [ ] Editor loads and works
- [ ] All features functional
- [ ] No console errors
- [ ] Performance acceptable

#### Test 9.4: Edge
- [ ] Editor loads and works
- [ ] All features functional
- [ ] No console errors
- [ ] Performance acceptable

### 10. Mobile Testing (Optional)

#### Test 10.1: Mobile Browser
- [ ] Page loads on mobile
- [ ] Editor is visible
- [ ] Basic editing works
- [ ] Touch controls work

**Note:** Mobile experience may be limited compared to desktop.

## Production Readiness Tests

### 11. Configuration Tests

#### Test 11.1: Environment Variables
```bash
# Check .env file exists
cat .env

# Should contain:
# - ONLYOFFICE_SERVER_URL
# - ONLYOFFICE_JWT_SECRET
# - BACKEND_URL
# - CORS_ORIGINS
```

- [ ] All required variables present
- [ ] JWT secret is strong (not default)
- [ ] URLs are correct
- [ ] CORS properly configured

#### Test 11.2: Data Directory
```bash
# Check data directory exists and is writable
ls -la backend/data/
touch backend/data/test.txt
rm backend/data/test.txt
```

- [ ] Directory exists
- [ ] Directory is writable
- [ ] Files can be created
- [ ] Files can be deleted

### 12. Load Testing (Optional)

#### Test 12.1: Concurrent Users
1. Open 5 editor tabs simultaneously
2. Edit different documents
3. Monitor system resources

- [ ] All editors work
- [ ] No conflicts
- [ ] Acceptable performance
- [ ] System stable

#### Test 12.2: Sustained Usage
1. Keep editor open for 30 minutes
2. Edit periodically
3. Monitor for issues

- [ ] No memory leaks
- [ ] Auto-save continues working
- [ ] No disconnections
- [ ] Performance stays consistent

## Troubleshooting Validation

### 13. Documentation Tests

#### Test 13.1: Quick Start Guide
Follow `ONLYOFFICE_QUICKSTART.md` step by step:

- [ ] All commands work
- [ ] Instructions clear
- [ ] Setup completes successfully
- [ ] Time estimate accurate (~5 minutes)

#### Test 13.2: Full Setup Guide
Follow `docs/onlyoffice-setup.md`:

- [ ] Installation section works
- [ ] Configuration section clear
- [ ] Troubleshooting section helpful
- [ ] All examples work

#### Test 13.3: Architecture Documentation
Review `docs/onlyoffice-architecture.md`:

- [ ] Diagrams accurate
- [ ] Flows documented correctly
- [ ] Matches actual implementation

## Test Results Summary

### Environment
- Date: _________________
- Tester: _________________
- OS: _________________
- Docker Version: _________________
- Python Version: _________________
- Node Version: _________________

### Results
- Total Tests: ___ / 100+
- Passed: ___
- Failed: ___
- Skipped: ___

### Critical Issues Found
1. ________________________________
2. ________________________________
3. ________________________________

### Non-Critical Issues Found
1. ________________________________
2. ________________________________
3. ________________________________

### Overall Assessment
- [ ] Ready for production
- [ ] Ready with minor fixes
- [ ] Needs significant work
- [ ] Not ready

### Notes
_____________________________________________
_____________________________________________
_____________________________________________

## Automated Testing (Future)

### Suggested Automated Tests

```python
# Example: pytest test suite

def test_onlyoffice_health():
    """Test OnlyOffice health endpoint"""
    response = requests.get("http://localhost:8000/api/onlyoffice/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_document_upload():
    """Test document upload"""
    files = {"file": open("test.docx", "rb")}
    response = requests.post(
        "http://localhost:8000/api/onlyoffice/upload/test123",
        files=files
    )
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_config_generation():
    """Test config generation"""
    response = requests.post(
        "http://localhost:8000/api/onlyoffice/config/test123"
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "document" in data
    assert "editorConfig" in data
```

## Continuous Integration

### GitHub Actions (Example)

```yaml
name: OnlyOffice Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Start OnlyOffice
        run: docker-compose up -d

      - name: Wait for OnlyOffice
        run: |
          timeout 180 bash -c 'until curl -s http://localhost:8080/welcome > /dev/null; do sleep 5; done'

      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/test_onlyoffice.py

      - name: Run frontend tests
        run: |
          cd frontend
          npm install
          npm test
```

---

## Conclusion

This comprehensive testing checklist ensures the OnlyOffice integration is:
- ✅ Properly installed
- ✅ Functioning correctly
- ✅ Secure
- ✅ Performant
- ✅ Production-ready

**Recommendation:** Complete at least sections 1-6 before deploying to production.

---

**Questions or Issues?** See `docs/onlyoffice-setup.md` for troubleshooting help.
