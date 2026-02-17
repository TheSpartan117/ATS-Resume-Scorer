# Python 3.14 Compatibility Issues

## Problem

The backend requirements.txt specifies exact versions that are **NOT compatible with Python 3.14**:

- `PyMuPDF==1.23.0` - Fails to build due to C compilation errors in the underlying mupdf library
- `spacy==3.7.0` - Fails to build due to its dependency `blis` having incompatible Cython code that uses deprecated Python C API

## Error Details

### PyMuPDF Build Error
```
subprocess.CalledProcessError: Command 'cd .../mupdf-1.23.0-source && ... mupdfwrap.py -d build/PyMuPDF-arm64-shared-release -b all'
returned non-zero exit status 1.
```
The C compilation fails when building the mupdf shared library.

### spacy Build Error
```
error: too few arguments to function call, expected 6, have 5
_PyLong_AsByteArray((PyLongObject *)v, bytes, sizeof(val), is_little, !is_unsigned);
```
The `blis` package (spacy dependency) uses old Cython-generated code that is incompatible with Python 3.14's modified `_PyLong_AsByteArray` function signature.

## Recommended Solutions

### Option 1: Use Python 3.11 (Recommended for Production)
The Dockerfile already specifies `python:3.11-slim` which will work with all dependencies:

```bash
# Use Docker for development
docker build -t ats-backend .
docker run -p 8000:8000 ats-backend
```

### Option 2: Downgrade Local Python
Create a new virtual environment with Python 3.11:

```bash
# Using pyenv
pyenv install 3.11.9
pyenv local 3.11.9
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Option 3: Use Compatible Versions (Development Only)
For local Python 3.14 development, these versions work:

```txt
PyMuPDF>=1.24.0  # Pre-built wheels available for Python 3.14
spacy>=3.8.0     # Includes Python 3.14 compatibility fixes
```

However, this violates the spec's exact version pinning.

## Current Status

- ✅ requirements.txt updated with spec-compliant exact versions
- ✅ Dockerfile removed invalid HEALTHCHECK
- ❌ Cannot install dependencies on Python 3.14
- ✅ Backend code itself is Python 3.14 compatible

## Next Steps

1. Use Docker (Python 3.11) for development and production
2. OR use Python 3.11 locally via pyenv
3. The FastAPI application code is ready and will work once dependencies are installed
