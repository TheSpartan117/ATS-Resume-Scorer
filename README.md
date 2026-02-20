# ATS Resume Scorer

AI-powered resume scoring platform that helps job seekers optimize their resumes for Applicant Tracking Systems. A 100% free, open-source alternative to Resume Worded and Jobscan.

## Features

### Core Functionality
- **AI-Powered ATS Scoring** - Semantic keyword matching with sentence-transformers
- **Multi-Platform ATS Simulation** - Tests against Taleo, Workday, and Greenhouse
- **Grammar & Spelling Check** - Professional-grade validation with LanguageTool
- **Smart Skills Categorization** - Automatic hard/soft skills classification
- **Confidence Scoring** - Statistical confidence intervals for transparency
- **Performance Optimized** - <2s scoring with intelligent caching

### Editing Experience
- **100% Word-Compatible Editing** - OnlyOffice Document Server integration
- **Real-time Editing** - Edit resumes with full Microsoft Word features
- **Multiple View Modes** - OnlyOffice Editor, Preview, and Structure Editor
- **Auto-save** - Changes are automatically saved
- **Export Options** - Download as PDF, DOCX, or LaTeX

### Testing & Validation
- **A/B Testing Framework** - Statistical validation of improvements
- **Comprehensive Test Suite** - 100+ unit and integration tests
- **Performance Benchmarks** - Continuous monitoring and optimization
- **Competitor Validation** - Aligned with industry-leading tools

## Quick Start

Get the full Word-like editing experience in 5 minutes:

```bash
# 1. Start OnlyOffice Document Server
docker-compose up -d

# 2. Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 3. Start services
# Terminal 1: Backend
cd backend && python -m uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev

# 4. Open browser
# Navigate to http://localhost:3000
```

See [ONLYOFFICE_QUICKSTART.md](ONLYOFFICE_QUICKSTART.md) for detailed setup.

## Documentation

- [Scoring Methodology](docs/SCORING_METHODOLOGY.md) - How we calculate scores
- [API Documentation](docs/API_DOCUMENTATION.md) - Complete API reference
- [Unified Implementation Plan](docs/UNIFIED_IMPLEMENTATION_PLAN.md) - Development roadmap
- [Phase 4 Validation Report](docs/PHASE4_VALIDATION_REPORT.md) - Testing results
- [Expert Analyses](docs/) - Strategy, market, technical, and data reports

## Technology Stack

### AI & NLP (All Free/Open-Source)
- **sentence-transformers** - Semantic keyword matching
- **KeyBERT** - Keyword extraction
- **spaCy** - Natural language processing
- **language-tool-python** - Grammar checking
- **diskcache** - Performance caching

### Backend
- **FastAPI** - High-performance Python web framework
- **PostgreSQL** - Reliable data storage
- **python-docx / PyMuPDF** - Document parsing

### Frontend
- **React + TypeScript** - Modern, type-safe UI
- **OnlyOffice Document Server** - Professional document editing

## Performance

- First scoring: <2 seconds
- Cached scoring: <500ms
- Memory usage: Optimized for efficiency
- Concurrent requests: Fully supported

## Testing

Run the comprehensive test suite:

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Performance benchmarks
python scripts/performance_benchmark.py

# Competitor validation
python scripts/benchmark_against_competitors.py
```

## Competitive Positioning

### vs Jobscan ($50/month)
- Match accuracy: 90%+ (equivalent to Jobscan)
- ATS simulation: 3 platforms (Jobscan has 4)
- **Price: $0** (Jobscan: $50/month)

### vs Resume Worded ($19/month)
- Semantic matching with AI
- Grammar checking (same quality)
- Real-time editing (unique feature)
- **Price: $0** (Resume Worded: $19/month)

### Unique Advantages
1. **100% Free** - No paywalls, unlimited scans
2. **Open-source** - Transparent algorithms
3. **Privacy-first** - No data retention
4. **Real-time editing** - OnlyOffice integration
5. **Customizable** - Fork, extend, contribute

## Project Status

**Phase:** Phase 4 Complete - Validation & Testing
**Status:** Production Ready

All phases implemented:
- Phase 1: Critical Fixes (Scoring recalibration, semantic matching)
- Phase 2: Critical Features (ATS simulation, skills categorization)
- Phase 3: UI Improvements (Top issues, pass probability)
- Phase 4: Testing & Validation (A/B testing, performance benchmarks)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - See [LICENSE](LICENSE) for details

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/yourusername/ats-resume-scorer/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/ats-resume-scorer/discussions)
