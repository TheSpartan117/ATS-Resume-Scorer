"""
Role taxonomy system for experience-level based scoring.

Provides comprehensive role definitions across all major career categories
with experience-level-specific keywords and requirements.
"""
from typing import Dict, List, Tuple
from enum import Enum


class ExperienceLevel(str, Enum):
    """Experience levels for role-based scoring"""
    ENTRY = "entry"          # 0-2 years
    MID = "mid"              # 3-5 years
    SENIOR = "senior"        # 6-10 years
    LEAD = "lead"            # 10+ years, Lead/Principal
    EXECUTIVE = "executive"  # C-level, VP


class RoleCategory(str, Enum):
    """Major role categories"""
    TECH = "tech"
    PRODUCT = "product"
    DESIGN = "design"
    BUSINESS = "business"
    DATA = "data"
    OPERATIONS = "operations"
    FINANCE = "finance"
    HR = "hr"
    LEGAL = "legal"
    CUSTOMER = "customer"
    CREATIVE = "creative"


# Comprehensive role definitions
ROLE_DEFINITIONS: Dict[str, Dict] = {
    # TECH ROLES
    "software_engineer": {
        "name": "Software Engineer",
        "category": RoleCategory.TECH,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["python", "javascript", "java", "git", "api", "sql", "testing"],
            ExperienceLevel.MID: ["architecture", "microservices", "ci/cd", "aws", "docker", "agile", "mentoring"],
            ExperienceLevel.SENIOR: ["system design", "scalability", "performance", "leadership", "technical strategy"],
            ExperienceLevel.LEAD: ["architectural decisions", "team leadership", "roadmap", "engineering culture"],
            ExperienceLevel.EXECUTIVE: ["cto", "vp engineering", "engineering strategy", "organizational"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "built", "implemented", "coded", "debugged", "tested", "deployed", "contributed", "fixed", "wrote", "created", "learned"],
            ExperienceLevel.MID: ["architected", "designed", "optimized", "scaled", "mentored", "led", "refactored", "automated", "engineered", "delivered", "integrated", "improved"],
            ExperienceLevel.SENIOR: ["spearheaded", "pioneered", "transformed", "strategized", "influenced", "drove", "established", "directed", "championed", "innovated", "led", "shaped"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "strategized", "led", "architected", "drove", "owned", "defined", "shaped", "built", "orchestrated"],
            ExperienceLevel.EXECUTIVE: ["directed", "established", "transformed", "led", "defined", "shaped", "built", "scaled", "drove", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },
        "required_skills": ["programming", "version control", "problem solving"],
        "preferred_sections": ["github", "portfolio", "technical projects"]
    },
    "data_scientist": {
        "name": "Data Scientist",
        "category": RoleCategory.DATA,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["python", "sql", "statistics", "machine learning", "pandas", "visualization"],
            ExperienceLevel.MID: ["predictive modeling", "feature engineering", "a/b testing", "tensorflow", "pytorch"],
            ExperienceLevel.SENIOR: ["ml strategy", "data architecture", "team leadership", "business impact"],
            ExperienceLevel.LEAD: ["data science roadmap", "ml infrastructure", "mentorship", "strategic insights"],
            ExperienceLevel.EXECUTIVE: ["chief data officer", "data strategy", "ai/ml strategy"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["statistics", "programming", "data analysis"],
        "preferred_sections": ["github", "kaggle", "publications"]
    },
    "devops_engineer": {
        "name": "DevOps Engineer",
        "category": RoleCategory.TECH,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["linux", "docker", "jenkins", "git", "scripting", "monitoring"],
            ExperienceLevel.MID: ["kubernetes", "terraform", "ci/cd pipelines", "aws", "azure", "automation"],
            ExperienceLevel.SENIOR: ["infrastructure strategy", "sre", "disaster recovery", "cost optimization"],
            ExperienceLevel.LEAD: ["platform engineering", "devops culture", "tooling strategy"],
            ExperienceLevel.EXECUTIVE: ["infrastructure leadership", "cloud strategy"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["automation", "cloud platforms", "containers"],
        "preferred_sections": ["certifications", "github"]
    },

    # PRODUCT ROLES
    "product_manager": {
        "name": "Product Manager",
        "category": RoleCategory.PRODUCT,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["roadmap", "user stories", "agile", "wireframes", "stakeholders", "analytics"],
            ExperienceLevel.MID: ["product strategy", "kpis", "market research", "go-to-market", "prioritization"],
            ExperienceLevel.SENIOR: ["product vision", "cross-functional leadership", "revenue growth", "strategic partnerships"],
            ExperienceLevel.LEAD: ["product portfolio", "organizational strategy", "executive stakeholders"],
            ExperienceLevel.EXECUTIVE: ["cpo", "vp product", "product organization", "company strategy"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["product strategy", "stakeholder management", "data-driven decisions"],
        "preferred_sections": ["product launches", "metrics", "impact"]
    },
    "technical_product_manager": {
        "name": "Technical Product Manager",
        "category": RoleCategory.PRODUCT,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["api", "sql", "technical requirements", "engineering collaboration"],
            ExperienceLevel.MID: ["system architecture", "technical roadmap", "api design", "platform products"],
            ExperienceLevel.SENIOR: ["technical strategy", "developer experience", "platform scalability"],
            ExperienceLevel.LEAD: ["technical product vision", "engineering partnerships"],
            ExperienceLevel.EXECUTIVE: ["technical product strategy", "platform leadership"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["technical background", "api knowledge", "engineering collaboration"],
        "preferred_sections": ["technical projects", "github"]
    },

    # DESIGN ROLES
    "ux_designer": {
        "name": "UX Designer",
        "category": RoleCategory.DESIGN,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["wireframes", "prototypes", "user research", "figma", "sketch", "usability"],
            ExperienceLevel.MID: ["design systems", "user testing", "information architecture", "accessibility"],
            ExperienceLevel.SENIOR: ["design strategy", "design leadership", "cross-functional collaboration"],
            ExperienceLevel.LEAD: ["design org", "design culture", "design vision"],
            ExperienceLevel.EXECUTIVE: ["head of design", "design strategy", "brand experience"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["user research", "prototyping", "design tools"],
        "preferred_sections": ["portfolio", "case studies", "design process"]
    },
    "ui_designer": {
        "name": "UI Designer",
        "category": RoleCategory.DESIGN,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["visual design", "figma", "sketch", "typography", "color theory"],
            ExperienceLevel.MID: ["design systems", "interaction design", "responsive design", "accessibility"],
            ExperienceLevel.SENIOR: ["visual design strategy", "brand consistency", "design leadership"],
            ExperienceLevel.LEAD: ["design systems architecture", "design team leadership"],
            ExperienceLevel.EXECUTIVE: ["creative director", "design vision"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["visual design", "design systems", "figma/sketch"],
        "preferred_sections": ["portfolio", "dribbble", "behance"]
    },
    "product_designer": {
        "name": "Product Designer",
        "category": RoleCategory.DESIGN,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["ux", "ui", "user research", "prototyping", "figma"],
            ExperienceLevel.MID: ["end-to-end design", "design thinking", "data-informed design", "design systems"],
            ExperienceLevel.SENIOR: ["product strategy", "design leadership", "cross-functional", "impact metrics"],
            ExperienceLevel.LEAD: ["design vision", "product design org", "design culture"],
            ExperienceLevel.EXECUTIVE: ["head of product design", "design strategy"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["ux/ui", "user research", "product thinking"],
        "preferred_sections": ["portfolio", "case studies", "metrics"]
    },

    # BUSINESS ROLES
    "marketing_manager": {
        "name": "Marketing Manager",
        "category": RoleCategory.BUSINESS,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["campaigns", "social media", "content", "analytics", "seo", "email marketing"],
            ExperienceLevel.MID: ["marketing strategy", "budget management", "roi", "brand", "demand generation"],
            ExperienceLevel.SENIOR: ["go-to-market", "revenue growth", "team leadership", "marketing automation"],
            ExperienceLevel.LEAD: ["marketing organization", "growth strategy", "marketing ops"],
            ExperienceLevel.EXECUTIVE: ["cmo", "vp marketing", "brand strategy", "revenue strategy"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["marketing strategy", "analytics", "campaign management"],
        "preferred_sections": ["campaigns", "growth metrics", "roi"]
    },
    "sales_manager": {
        "name": "Sales Manager",
        "category": RoleCategory.BUSINESS,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["prospecting", "cold calling", "crm", "pipeline", "quota attainment"],
            ExperienceLevel.MID: ["account management", "negotiation", "revenue growth", "team leadership", "forecasting"],
            ExperienceLevel.SENIOR: ["sales strategy", "enterprise sales", "strategic accounts", "team development"],
            ExperienceLevel.LEAD: ["sales organization", "revenue operations", "go-to-market strategy"],
            ExperienceLevel.EXECUTIVE: ["cro", "vp sales", "sales strategy", "revenue growth"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["sales", "negotiation", "crm", "pipeline management"],
        "preferred_sections": ["quota attainment", "revenue", "client wins"]
    },
    "business_analyst": {
        "name": "Business Analyst",
        "category": RoleCategory.BUSINESS,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["requirements gathering", "sql", "excel", "documentation", "stakeholders"],
            ExperienceLevel.MID: ["process optimization", "data analysis", "business intelligence", "reporting"],
            ExperienceLevel.SENIOR: ["business strategy", "cross-functional", "change management", "strategic insights"],
            ExperienceLevel.LEAD: ["business analysis practice", "methodology", "team leadership"],
            ExperienceLevel.EXECUTIVE: ["strategy", "business transformation"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["analysis", "sql", "stakeholder management"],
        "preferred_sections": ["process improvements", "cost savings", "efficiency"]
    },

    # OPERATIONS
    "operations_manager": {
        "name": "Operations Manager",
        "category": RoleCategory.OPERATIONS,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["process improvement", "project management", "logistics", "inventory"],
            ExperienceLevel.MID: ["operations strategy", "vendor management", "cost optimization", "team leadership"],
            ExperienceLevel.SENIOR: ["operational excellence", "supply chain", "cross-functional", "strategic planning"],
            ExperienceLevel.LEAD: ["operations organization", "operational transformation"],
            ExperienceLevel.EXECUTIVE: ["coo", "vp operations", "operational strategy"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["operations", "process optimization", "project management"],
        "preferred_sections": ["cost savings", "efficiency improvements", "process metrics"]
    },

    # FINANCE
    "financial_analyst": {
        "name": "Financial Analyst",
        "category": RoleCategory.FINANCE,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["financial modeling", "excel", "forecasting", "budgeting", "variance analysis"],
            ExperienceLevel.MID: ["financial planning", "fp&a", "business partnering", "reporting"],
            ExperienceLevel.SENIOR: ["financial strategy", "strategic planning", "stakeholder management", "insights"],
            ExperienceLevel.LEAD: ["finance team leadership", "financial planning", "business strategy"],
            ExperienceLevel.EXECUTIVE: ["cfo", "vp finance", "financial strategy"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["financial analysis", "modeling", "excel"],
        "preferred_sections": ["certifications", "models", "accuracy"]
    },
    "accountant": {
        "name": "Accountant",
        "category": RoleCategory.FINANCE,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["bookkeeping", "journal entries", "reconciliations", "gaap", "quickbooks"],
            ExperienceLevel.MID: ["financial statements", "audit", "tax", "compliance", "erp systems"],
            ExperienceLevel.SENIOR: ["accounting processes", "team leadership", "sox compliance", "close process"],
            ExperienceLevel.LEAD: ["accounting organization", "controller", "accounting strategy"],
            ExperienceLevel.EXECUTIVE: ["cfo", "vp finance", "financial operations"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["accounting", "gaap", "financial reporting"],
        "preferred_sections": ["cpa", "certifications", "audit experience"]
    },

    # HR
    "hr_manager": {
        "name": "HR Manager",
        "category": RoleCategory.HR,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["recruiting", "onboarding", "hris", "employee relations", "compliance"],
            ExperienceLevel.MID: ["talent acquisition", "performance management", "compensation", "benefits"],
            ExperienceLevel.SENIOR: ["hr strategy", "organizational development", "culture", "change management"],
            ExperienceLevel.LEAD: ["hr organization", "people strategy", "talent strategy"],
            ExperienceLevel.EXECUTIVE: ["chro", "vp hr", "people strategy", "organizational strategy"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["hr", "recruiting", "employee relations"],
        "preferred_sections": ["certifications", "hiring metrics", "retention"]
    },
    "recruiter": {
        "name": "Recruiter",
        "category": RoleCategory.HR,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["sourcing", "screening", "ats", "linkedin", "candidate experience"],
            ExperienceLevel.MID: ["full-cycle recruiting", "hiring managers", "metrics", "employer branding"],
            ExperienceLevel.SENIOR: ["recruiting strategy", "team leadership", "diversity", "hiring goals"],
            ExperienceLevel.LEAD: ["talent acquisition org", "recruiting operations"],
            ExperienceLevel.EXECUTIVE: ["vp talent", "talent strategy"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["recruiting", "sourcing", "ats"],
        "preferred_sections": ["hiring metrics", "time-to-fill", "candidate satisfaction"]
    },

    # CUSTOMER SUCCESS
    "customer_success_manager": {
        "name": "Customer Success Manager",
        "category": RoleCategory.CUSTOMER,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["customer onboarding", "support", "retention", "crm", "customer satisfaction"],
            ExperienceLevel.MID: ["account management", "upselling", "renewals", "customer health", "churn reduction"],
            ExperienceLevel.SENIOR: ["cs strategy", "team leadership", "cross-functional", "customer advocacy"],
            ExperienceLevel.LEAD: ["cs organization", "customer success operations"],
            ExperienceLevel.EXECUTIVE: ["vp customer success", "customer strategy", "retention strategy"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["customer success", "relationship management", "crm"],
        "preferred_sections": ["retention rates", "nps", "customer satisfaction"]
    },

    # LEGAL
    "corporate_lawyer": {
        "name": "Corporate Lawyer",
        "category": RoleCategory.LEGAL,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["contracts", "legal research", "compliance", "corporate law"],
            ExperienceLevel.MID: ["m&a", "due diligence", "corporate governance", "intellectual property"],
            ExperienceLevel.SENIOR: ["legal strategy", "risk management", "regulatory", "team leadership"],
            ExperienceLevel.LEAD: ["legal department", "general counsel", "legal operations"],
            ExperienceLevel.EXECUTIVE: ["general counsel", "chief legal officer", "legal strategy"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["legal", "contracts", "compliance"],
        "preferred_sections": ["bar admission", "cases", "transactions"]
    },

    # CREATIVE
    "content_writer": {
        "name": "Content Writer",
        "category": RoleCategory.CREATIVE,
        "typical_keywords": {
            ExperienceLevel.ENTRY: ["copywriting", "content creation", "blog posts", "seo", "editing"],
            ExperienceLevel.MID: ["content strategy", "brand voice", "editorial", "content marketing"],
            ExperienceLevel.SENIOR: ["content leadership", "editorial strategy", "team management"],
            ExperienceLevel.LEAD: ["content organization", "content operations"],
            ExperienceLevel.EXECUTIVE: ["head of content", "content strategy"]
        },
        "action_verbs": {
            ExperienceLevel.ENTRY: ["developed", "created", "implemented", "managed", "supported", "executed", "analyzed", "collaborated", "coordinated", "assisted", "built", "tested"],
            ExperienceLevel.MID: ["led", "designed", "improved", "optimized", "managed", "drove", "developed", "delivered", "collaborated", "achieved", "architected", "scaled"],
            ExperienceLevel.SENIOR: ["led", "established", "drove", "transformed", "shaped", "directed", "influenced", "built", "scaled", "pioneered", "spearheaded", "championed"],
            ExperienceLevel.LEAD: ["directed", "established", "transformed", "led", "drove", "shaped", "owned", "built", "defined", "scaled", "orchestrated", "revolutionized"],
            ExperienceLevel.EXECUTIVE: ["established", "transformed", "directed", "shaped", "led", "built", "scaled", "drove", "defined", "orchestrated", "pioneered", "revolutionized"]
        },
        "scoring_weights": {
            "keywords": 0.40,
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,
            ExperienceLevel.MID: 4,
            ExperienceLevel.SENIOR: 6,
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        "required_skills": ["writing", "editing", "content strategy"],
        "preferred_sections": ["portfolio", "published work", "writing samples"]
    }
}


def get_all_roles() -> List[Tuple[str, str]]:
    """Get all available roles as (role_id, display_name) tuples."""
    return [(role_id, data["name"]) for role_id, data in ROLE_DEFINITIONS.items()]


def get_roles_by_category(category: RoleCategory) -> List[Tuple[str, str]]:
    """Get roles filtered by category."""
    return [
        (role_id, data["name"])
        for role_id, data in ROLE_DEFINITIONS.items()
        if data["category"] == category
    ]


def get_role_scoring_data(role_id: str, level: ExperienceLevel) -> Dict:
    """Get scoring criteria for specific role and level."""
    if role_id not in ROLE_DEFINITIONS:
        return None

    role_data = ROLE_DEFINITIONS[role_id]
    return {
        "name": role_data["name"],
        "category": role_data["category"],
        "keywords": role_data.get("keywords", {}).get(level, []),  # Legacy support
        "typical_keywords": role_data.get("typical_keywords", {}).get(level, []),
        "action_verbs": role_data.get("action_verbs", {}).get(level, []),
        "scoring_weights": role_data.get("scoring_weights", {}),
        "metrics_expected": role_data.get("metrics_expected", {}).get(level, 3),
        "required_skills": role_data.get("required_skills", []),
        "preferred_sections": role_data.get("preferred_sections", [])
    }
