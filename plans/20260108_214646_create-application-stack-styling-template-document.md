# Plan: Create Application Stack & Styling Template Document

**Affects:** `/workspace/.data/stack-template.md`

---

## Objective

Create a detailed reference document capturing the FFmpeg Sandbox application's tech stack and visual styling system for use as a template when building other applications.

---

## Document Sections

### 1. Tech Stack Overview
- FastAPI + Pydantic backend
- HTMX + Jinja2 frontend (no heavy JS frameworks)
- uv package manager
- Docker containerization

### 2. Backend Architecture
- FastAPI configuration patterns (main.py)
- Pydantic model organization (3-tier)
- Service layer architecture (14 modules)
- Router structure (3 routers, 47+ endpoints)
- Configuration management (dataclass + YAML)
- Dependencies (7 core packages)

### 3. Frontend Architecture
- Template structure (3 root + 14 partials)
- HTMX patterns used (7 distinct patterns)
- JavaScript module pattern (IIFE closures)
- Form handling via HTMX

### 4. CSS Architecture
- File organization (10 CSS files, ~2,140 lines)
- CSS variable system (12 core variables)
- Theme implementation (10 dark themes)
- Component patterns (buttons, forms, accordions)
- Layout system (flexbox + CSS grid)

### 5. Color Palette Reference
- All 10 themes with hex values
- Variable naming conventions
- Contrast ratios and accessibility

### 6. Reusable Patterns
- HTMX partial response pattern
- Accordion state management
- Theme switching (localStorage + data-attribute)
- Filter chain visualization

---

## Output

Single markdown file: `/workspace/.data/stack-template.md`

Structured for easy consumption by AI agents building new applications.

---

## Implementation

1. Compile agent analysis results
2. Structure into template-friendly format
3. Include code examples for each pattern
4. Write to `.data/stack-template.md`
