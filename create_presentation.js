const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "HotGigs Team";
pres.title = "HotGigs 2026 — Deployment Guide";

// Color palette
const colors = {
  charcoal: "36454F",
  offWhite: "F2F2F2",
  teal: "0D9488",
  red: "DC2626",
  light: "F8FAFB",
  darkGray: "1F2937",
  mediumGray: "6B7280",
  lightGray: "D1D5DB",
};

// Factory functions for shadow (avoid object reuse)
const makeShadow = () => ({
  type: "outer",
  blur: 6,
  offset: 2,
  color: "000000",
  opacity: 0.15,
});

const makeTextOpts = (overrides = {}) => ({
  fontFace: "Calibri",
  fontSize: 14,
  color: colors.darkGray,
  ...overrides,
});

const makeHeadingOpts = (overrides = {}) => ({
  fontFace: "Georgia",
  fontSize: 28,
  bold: true,
  color: colors.charcoal,
  ...overrides,
});

const makeCodeOpts = (overrides = {}) => ({
  fontFace: "Consolas",
  fontSize: 10,
  color: colors.charcoal,
  ...overrides,
});

// SLIDE 1: Title
function addTitleSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.charcoal };

  // Accent bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0,
    y: 0,
    w: 0.15,
    h: 5.625,
    fill: { color: colors.teal },
    line: { type: "none" },
  });

  slide.addText("HotGigs 2026", {
    x: 0.5,
    y: 1.8,
    w: 9,
    h: 1.2,
    fontFace: "Georgia",
    fontSize: 54,
    bold: true,
    color: colors.offWhite,
  });

  slide.addText("Deployment Guide", {
    x: 0.5,
    y: 3.0,
    w: 9,
    h: 0.8,
    fontFace: "Georgia",
    fontSize: 44,
    color: colors.teal,
  });

  slide.addText("Production, Staging & Development Environments", {
    x: 0.5,
    y: 4.0,
    w: 9,
    h: 0.5,
    fontFace: "Calibri",
    fontSize: 18,
    color: colors.offWhite,
    italic: true,
  });
}

// SLIDE 2: Table of Contents
function addTableOfContents() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Table of Contents", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  const items = [
    "Architecture Overview & Infrastructure",
    "Prerequisites, Setup & Deployment Configuration",
    "Multi-Tenant Architecture & Data Management",
    "CI/CD Pipeline, Monitoring & Security",
    "Scaling, Troubleshooting & Operations",
  ];

  slide.addText(
    items.map((item, idx) => ({
      text: item,
      options: {
        bullet: true,
        breakLine: idx < items.length - 1,
        fontSize: 16,
      },
    })),
    {
      x: 1.0,
      y: 1.2,
      w: 8.5,
      h: 4.0,
      fontFace: "Calibri",
      color: colors.darkGray,
    }
  );
}

// SLIDE 3: Architecture Overview
function addArchitectureSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.light };

  slide.addText("Architecture Overview", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  // Frontend box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5,
    y: 1.2,
    w: 1.8,
    h: 1.0,
    fill: { color: colors.teal },
    line: { color: colors.charcoal, width: 2 },
    shadow: makeShadow(),
  });
  slide.addText("Frontend\n(React/Vite)", {
    x: 0.5,
    y: 1.2,
    w: 1.8,
    h: 1.0,
    fontFace: "Georgia",
    fontSize: 11,
    bold: true,
    color: colors.offWhite,
    align: "center",
    valign: "middle",
  });

  // Arrow 1
  slide.addShape(pres.shapes.LINE, {
    x: 2.4,
    y: 1.7,
    w: 0.8,
    h: 0,
    line: { color: colors.charcoal, width: 2 },
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 3.1,
    y: 1.65,
    w: 0.15,
    h: 0.1,
    fill: { color: colors.charcoal },
  });

  // CDN box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 3.3,
    y: 1.2,
    w: 1.8,
    h: 1.0,
    fill: { color: colors.teal },
    line: { color: colors.charcoal, width: 2 },
    shadow: makeShadow(),
  });
  slide.addText("Vercel CDN", {
    x: 3.3,
    y: 1.2,
    w: 1.8,
    h: 1.0,
    fontFace: "Georgia",
    fontSize: 11,
    bold: true,
    color: colors.offWhite,
    align: "center",
    valign: "middle",
  });

  // Backend box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5,
    y: 2.8,
    w: 1.8,
    h: 1.0,
    fill: { color: colors.charcoal },
    line: { color: colors.darkGray, width: 2 },
    shadow: makeShadow(),
  });
  slide.addText("Backend\n(FastAPI)", {
    x: 0.5,
    y: 2.8,
    w: 1.8,
    h: 1.0,
    fontFace: "Georgia",
    fontSize: 11,
    bold: true,
    color: colors.offWhite,
    align: "center",
    valign: "middle",
  });

  // Arrow 2
  slide.addShape(pres.shapes.LINE, {
    x: 2.4,
    y: 3.3,
    w: 0.8,
    h: 0,
    line: { color: colors.charcoal, width: 2 },
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 3.1,
    y: 3.25,
    w: 0.15,
    h: 0.1,
    fill: { color: colors.charcoal },
  });

  // Serverless box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 3.3,
    y: 2.8,
    w: 1.8,
    h: 1.0,
    fill: { color: colors.charcoal },
    line: { color: colors.darkGray, width: 2 },
    shadow: makeShadow(),
  });
  slide.addText("Vercel Serverless", {
    x: 3.3,
    y: 2.8,
    w: 1.8,
    h: 1.0,
    fontFace: "Georgia",
    fontSize: 11,
    bold: true,
    color: colors.offWhite,
    align: "center",
    valign: "middle",
  });

  // Database box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5,
    y: 4.4,
    w: 1.8,
    h: 1.0,
    fill: { color: colors.red },
    line: { color: colors.charcoal, width: 2 },
    shadow: makeShadow(),
  });
  slide.addText("Database\n(SQLAlchemy)", {
    x: 0.5,
    y: 4.4,
    w: 1.8,
    h: 1.0,
    fontFace: "Georgia",
    fontSize: 11,
    bold: true,
    color: colors.offWhite,
    align: "center",
    valign: "middle",
  });

  // Arrow 3
  slide.addShape(pres.shapes.LINE, {
    x: 2.4,
    y: 4.9,
    w: 0.8,
    h: 0,
    line: { color: colors.charcoal, width: 2 },
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 3.1,
    y: 4.85,
    w: 0.15,
    h: 0.1,
    fill: { color: colors.charcoal },
  });

  // Storage box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 3.3,
    y: 4.4,
    w: 1.8,
    h: 1.0,
    fill: { color: colors.red },
    line: { color: colors.charcoal, width: 2 },
    shadow: makeShadow(),
  });
  slide.addText("PostgreSQL/SQLite", {
    x: 3.3,
    y: 4.4,
    w: 1.8,
    h: 1.0,
    fontFace: "Georgia",
    fontSize: 11,
    bold: true,
    color: colors.offWhite,
    align: "center",
    valign: "middle",
  });

  // Vertical connections from Frontend to Backend
  slide.addShape(pres.shapes.LINE, {
    x: 1.4,
    y: 2.2,
    w: 0,
    h: 0.6,
    line: { color: colors.charcoal, width: 2 },
  });

  // Vertical connections from Backend to Database
  slide.addShape(pres.shapes.LINE, {
    x: 1.4,
    y: 3.8,
    w: 0,
    h: 0.6,
    line: { color: colors.charcoal, width: 2 },
  });

  // Legend/Info
  slide.addText("Multi-layer cloud-native architecture with serverless deployment", {
    x: 0.5,
    y: 5.2,
    w: 9,
    h: 0.35,
    fontFace: "Calibri",
    fontSize: 12,
    italic: true,
    color: colors.mediumGray,
  });
}

// SLIDE 4: Prerequisites
function addPrerequisitesSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Prerequisites", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  const requirements = [
    { tool: "Python", version: "3.10+" },
    { tool: "Node.js", version: "18+" },
    { tool: "Git", version: "2.40+" },
    { tool: "Vercel CLI", version: "Latest" },
    { tool: "PostgreSQL", version: "14+ (Production)" },
    { tool: "Docker", version: "Optional (20.10+)" },
  ];

  const tableData = [
    [
      { text: "Tool", options: { bold: true, color: colors.offWhite } },
      { text: "Version Requirement", options: { bold: true, color: colors.offWhite } },
    ],
    ...requirements.map((req) => [
      { text: req.tool },
      { text: req.version },
    ]),
  ];

  slide.addTable(tableData, {
    x: 0.8,
    y: 1.2,
    w: 8.4,
    h: 3.5,
    border: { pt: 1, color: colors.lightGray },
    fill: { color: colors.light },
    valign: "middle",
    fontSize: 13,
  });

  // Header styling
  const headerOptions = {
    fill: { color: colors.charcoal },
    color: colors.offWhite,
    bold: true,
    fontSize: 13,
  };

  slide.addTable(
    [[{ text: "Tool", options: headerOptions }, { text: "Version Requirement", options: headerOptions }]],
    {
      x: 0.8,
      y: 1.2,
      w: 8.4,
      h: 0.35,
      border: { pt: 1, color: colors.lightGray },
      fill: { color: colors.charcoal },
    }
  );
}

// SLIDE 5: Repository Structure
function addRepoStructureSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Repository Structure", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  const structure = [
    "hr_platform/",
    "├── api/v1/           36 API modules, 339 routes",
    "├── agents/           42 AI agents",
    "├── models/           94+ database tables",
    "├── services/         15+ business services",
    "├── frontend/src/     React/TypeScript application",
    "├── tests/            74 unit & integration tests",
    "├── schemas/          Pydantic validation schemas",
    "└── vercel.json       Deployment configuration",
  ];

  slide.addText(
    structure.map((line, idx) => ({
      text: line,
      options: {
        breakLine: idx < structure.length - 1,
        fontSize: 12,
        fontFace: "Consolas",
      },
    })),
    {
      x: 0.8,
      y: 1.2,
      w: 8.4,
      h: 4.0,
      color: colors.darkGray,
      fill: { color: colors.light },
    }
  );
}

// SLIDE 6: Environment Configuration
function addEnvironmentSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Environment Configuration", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  const envVars = [
    { var: "DATABASE_URL", desc: "PostgreSQL/SQLite connection string", env: "All" },
    { var: "JWT_SECRET", desc: "Secret key for JWT token signing", env: "All" },
    { var: "REDIS_URL", desc: "Redis cache connection string", env: "Production" },
    { var: "ANTHROPIC_API_KEY", desc: "Anthropic API credentials", env: "Production" },
    { var: "VERCEL_TOKEN", desc: "Vercel deployment token", env: "CI/CD" },
    { var: "CORS_ORIGINS", desc: "Allowed cross-origin domains", env: "All" },
  ];

  const tableData = [
    [
      { text: "Variable", options: { bold: true, color: colors.offWhite, fontSize: 12 } },
      { text: "Description", options: { bold: true, color: colors.offWhite, fontSize: 12 } },
      { text: "Environment", options: { bold: true, color: colors.offWhite, fontSize: 12 } },
    ],
    ...envVars.map((v) => [{ text: v.var, fontSize: 11 }, { text: v.desc, fontSize: 11 }, { text: v.env, fontSize: 11 }]),
  ];

  slide.addTable(tableData, {
    x: 0.5,
    y: 1.2,
    w: 9,
    h: 3.8,
    colW: [2.2, 4.3, 2.5],
    border: { pt: 1, color: colors.lightGray },
    fill: { color: colors.light },
    valign: "middle",
  });

  // Apply header styling
  slide.addTable(
    [[
      { text: "Variable", options: { bold: true, color: colors.offWhite, fontSize: 12 } },
      { text: "Description", options: { bold: true, color: colors.offWhite, fontSize: 12 } },
      { text: "Environment", options: { bold: true, color: colors.offWhite, fontSize: 12 } },
    ]],
    {
      x: 0.5,
      y: 1.2,
      w: 9,
      h: 0.32,
      colW: [2.2, 4.3, 2.5],
      border: { pt: 1, color: colors.lightGray },
      fill: { color: colors.charcoal },
    }
  );
}

// SLIDE 7: Local Development Setup
function addLocalDevSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Local Development Setup", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  const steps = [
    { num: "1", desc: "Clone repository and checkout main branch" },
    { num: "2", desc: "Install Python 3.10+ and pip dependencies" },
    { num: "3", desc: "Install Node.js 18+ and npm packages" },
    { num: "4", desc: "Configure PostgreSQL/SQLite database" },
    { num: "5", desc: "Run database migrations and seed data" },
    { num: "6", desc: "Start backend (uvicorn) and frontend (vite) dev servers" },
  ];

  steps.forEach((step, idx) => {
    const yPos = 1.2 + idx * 0.6;

    // Step number circle
    slide.addShape(pres.shapes.OVAL, {
      x: 0.6,
      y: yPos,
      w: 0.4,
      h: 0.4,
      fill: { color: colors.teal },
    });

    slide.addText(step.num, {
      x: 0.6,
      y: yPos,
      w: 0.4,
      h: 0.4,
      fontFace: "Georgia",
      fontSize: 14,
      bold: true,
      color: colors.offWhite,
      align: "center",
      valign: "middle",
    });

    // Description
    slide.addText(step.desc, {
      x: 1.2,
      y: yPos,
      w: 8.3,
      h: 0.4,
      fontFace: "Calibri",
      fontSize: 13,
      color: colors.darkGray,
      valign: "middle",
    });
  });
}

// SLIDE 8: Backend Deployment - Vercel
function addBackendDeploymentSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Backend Deployment — Vercel", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  slide.addText("vercel.json Configuration", {
    x: 0.5,
    y: 1.1,
    w: 9,
    fontFace: "Georgia",
    fontSize: 16,
    bold: true,
    color: colors.charcoal,
  });

  const config =
    `{
  "builds": [
    { "src": "api/main.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "api/main.py" }
  ]
}`;

  slide.addText(config, {
    x: 0.5,
    y: 1.5,
    w: 9,
    h: 2.0,
    fontFace: "Consolas",
    fontSize: 10,
    color: colors.charcoal,
    fill: { color: colors.light },
    align: "left",
  });

  slide.addText([
    { text: "FastAPI serverless functions deployed to Vercel's infrastructure", options: { breakLine: true } },
    { text: "Automatic scaling based on request load and traffic patterns", options: { breakLine: true } },
    { text: "Cold start optimized with Python 3.10 runtime", options: {} },
  ], {
    x: 0.5,
    y: 3.8,
    w: 9,
    h: 1.5,
    fontFace: "Calibri",
    fontSize: 12,
    color: colors.darkGray,
  });
}

// SLIDE 9: Frontend Build & Deploy
function addFrontendDeploySlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Frontend Build & Deploy", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  const steps = [
    { title: "Build", desc: "Vite compiles React/TypeScript to optimized static assets" },
    { title: "Output", desc: "Distribution files: frontend/dist/ with tree-shaking & code splitting" },
    { title: "Serving", desc: "Static assets cached on Vercel CDN with SPA routing fallback" },
    { title: "Caching", desc: "Client-side bundle caching with cache-busting hashes" },
  ];

  steps.forEach((step, idx) => {
    const yPos = 1.2 + idx * 1.0;

    // Accent bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5,
      y: yPos,
      w: 0.08,
      h: 0.8,
      fill: { color: colors.teal },
    });

    // Title
    slide.addText(step.title, {
      x: 0.75,
      y: yPos,
      w: 1.5,
      h: 0.35,
      fontFace: "Georgia",
      fontSize: 13,
      bold: true,
      color: colors.charcoal,
      valign: "top",
    });

    // Description
    slide.addText(step.desc, {
      x: 0.75,
      y: yPos + 0.35,
      w: 8.75,
      h: 0.45,
      fontFace: "Calibri",
      fontSize: 12,
      color: colors.mediumGray,
      valign: "top",
    });
  });
}

// SLIDE 10: Database Setup
function addDatabaseSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Database Setup", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  // Production section
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5,
    y: 1.1,
    w: 4.3,
    h: 0.35,
    fill: { color: colors.charcoal },
  });

  slide.addText("Production", {
    x: 0.5,
    y: 1.1,
    w: 4.3,
    h: 0.35,
    fontFace: "Georgia",
    fontSize: 13,
    bold: true,
    color: colors.offWhite,
    valign: "middle",
  });

  const prodText = [
    { text: "PostgreSQL 14+ recommended", options: { bullet: true, breakLine: true } },
    { text: "Connection pooling: pgBouncer or Vercel Postgres", options: { bullet: true, breakLine: true } },
    { text: "Automatic SSL/TLS encryption in transit", options: { bullet: true } },
  ];

  slide.addText(prodText, {
    x: 0.5,
    y: 1.6,
    w: 4.3,
    h: 1.5,
    fontFace: "Calibri",
    fontSize: 11,
    color: colors.darkGray,
  });

  // Development section
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.2,
    y: 1.1,
    w: 4.3,
    h: 0.35,
    fill: { color: colors.teal },
  });

  slide.addText("Development", {
    x: 5.2,
    y: 1.1,
    w: 4.3,
    h: 0.35,
    fontFace: "Georgia",
    fontSize: 13,
    bold: true,
    color: colors.offWhite,
    valign: "middle",
  });

  const devText = [
    { text: "SQLite3 for local development", options: { bullet: true, breakLine: true } },
    { text: "File-based storage: /tmp/hr_platform.db", options: { bullet: true, breakLine: true } },
    { text: "Quick setup, no external dependencies", options: { bullet: true } },
  ];

  slide.addText(devText, {
    x: 5.2,
    y: 1.6,
    w: 4.3,
    h: 1.5,
    fontFace: "Calibri",
    fontSize: 11,
    color: colors.darkGray,
  });

  // Migrations section
  slide.addText("Migrations & Connection Strings", {
    x: 0.5,
    y: 3.3,
    w: 9,
    fontFace: "Georgia",
    fontSize: 13,
    bold: true,
    color: colors.charcoal,
  });

  const migrations = [
    "# PostgreSQL (Production)",
    "postgresql+asyncpg://user:pass@host:5432/hr_platform",
    "",
    "# SQLite (Development)",
    "sqlite+aiosqlite:///./hr_platform.db",
    "",
    "# Alembic migrations auto-run on deployment",
  ];

  slide.addText(
    migrations.map((line, idx) => ({
      text: line,
      options: {
        breakLine: idx < migrations.length - 1,
        fontSize: 10,
        fontFace: "Consolas",
      },
    })),
    {
      x: 0.5,
      y: 3.8,
      w: 9,
      h: 1.6,
      color: colors.charcoal,
      fill: { color: colors.light },
    }
  );
}

// SLIDE 11: Multi-Tenant Configuration
function addMultiTenantSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Multi-Tenant Configuration", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  // Organization types
  const orgTypes = [
    { type: "MSP", color: colors.teal, desc: "Managed Service Provider (HotGigs admin)" },
    { type: "CLIENT", color: colors.charcoal, desc: "End customer company" },
    { type: "SUPPLIER", color: colors.red, desc: "Staffing/recruitment agency" },
  ];

  orgTypes.forEach((org, idx) => {
    const xPos = 0.5 + idx * 3.1;

    slide.addShape(pres.shapes.RECTANGLE, {
      x: xPos,
      y: 1.1,
      w: 2.9,
      h: 0.4,
      fill: { color: org.color },
    });

    slide.addText(org.type, {
      x: xPos,
      y: 1.1,
      w: 2.9,
      h: 0.4,
      fontFace: "Georgia",
      fontSize: 12,
      bold: true,
      color: colors.offWhite,
      align: "center",
      valign: "middle",
    });

    slide.addText(org.desc, {
      x: xPos,
      y: 1.6,
      w: 2.9,
      h: 1.2,
      fontFace: "Calibri",
      fontSize: 11,
      color: colors.darkGray,
    });
  });

  // Isolation mechanism
  slide.addText("Data Isolation Mechanism", {
    x: 0.5,
    y: 3.2,
    w: 9,
    fontFace: "Georgia",
    fontSize: 14,
    bold: true,
    color: colors.charcoal,
  });

  const isolation = [
    { term: "TenantContext", desc: "Request-scoped context binding organization_id to session" },
    { term: "JWT Claims", desc: "org_id embedded in token for authorization checks" },
    { term: "Row-Level Security", desc: "Queries automatically filtered by organization tenant" },
  ];

  isolation.forEach((item, idx) => {
    const yPos = 3.8 + idx * 0.7;

    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5,
      y: yPos,
      w: 0.08,
      h: 0.6,
      fill: { color: colors.teal },
    });

    slide.addText(item.term, {
      x: 0.75,
      y: yPos,
      w: 2.0,
      h: 0.3,
      fontFace: "Georgia",
      fontSize: 11,
      bold: true,
      color: colors.charcoal,
    });

    slide.addText(item.desc, {
      x: 2.9,
      y: yPos,
      w: 6.6,
      h: 0.6,
      fontFace: "Calibri",
      fontSize: 10,
      color: colors.mediumGray,
      valign: "top",
    });
  });
}

// SLIDE 12: Seed Data Management
function addSeedDataSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Seed Data Management", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  slide.addText("Demo Organizations & Users", {
    x: 0.5,
    y: 1.1,
    w: 9,
    fontFace: "Georgia",
    fontSize: 13,
    bold: true,
    color: colors.charcoal,
  });

  const seedData = [
    { org: "HotGigs MSP", type: "MSP (Admin)", users: "3 admin users" },
    { org: "TechCorp Client", type: "CLIENT", users: "2 hiring managers" },
    { org: "StaffPro Supplier", type: "SUPPLIER", users: "2 recruiters" },
  ];

  const tableData = [
    [
      { text: "Organization", options: { bold: true, color: colors.offWhite } },
      { text: "Type", options: { bold: true, color: colors.offWhite } },
      { text: "Demo Users", options: { bold: true, color: colors.offWhite } },
    ],
    ...seedData.map((item) => [{ text: item.org }, { text: item.type }, { text: item.users }]),
  ];

  slide.addTable(tableData, {
    x: 0.5,
    y: 1.5,
    w: 9,
    h: 1.5,
    colW: [3.2, 2.9, 2.9],
    border: { pt: 1, color: colors.lightGray },
    fill: { color: colors.light },
    valign: "middle",
    fontSize: 11,
  });

  slide.addText("Seed Implementation", {
    x: 0.5,
    y: 3.3,
    w: 9,
    fontFace: "Georgia",
    fontSize: 13,
    bold: true,
    color: colors.charcoal,
  });

  const seedInfo = [
    { item: "Location", desc: "vercel_app.py seed_data() function" },
    { item: "Trigger", desc: "Automatic on first deployment or manual via CLI" },
    { item: "Idempotent", desc: "Safe to re-run; checks existing data before inserting" },
    { item: "Demo Access", desc: "Login with admin@hotgigs.local / password123" },
  ];

  seedInfo.forEach((info, idx) => {
    const yPos = 3.8 + idx * 0.65;

    slide.addText(info.item, {
      x: 0.5,
      y: yPos,
      w: 1.8,
      h: 0.6,
      fontFace: "Georgia",
      fontSize: 11,
      bold: true,
      color: colors.teal,
    });

    slide.addText(info.desc, {
      x: 2.5,
      y: yPos,
      w: 7.0,
      h: 0.6,
      fontFace: "Calibri",
      fontSize: 11,
      color: colors.mediumGray,
    });
  });
}

// SLIDE 13: CI/CD Pipeline
function addCICDSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("CI/CD Pipeline", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  // Pipeline stages
  const stages = [
    { stage: "Feature\nBranch", color: colors.teal },
    { stage: "Pull\nRequest", color: colors.teal },
    { stage: "Code\nReview", color: colors.charcoal },
    { stage: "Tests\n(74 tests)", color: colors.charcoal },
    { stage: "Merge\nMain", color: colors.charcoal },
    { stage: "Auto\nDeploy", color: colors.teal },
  ];

  stages.forEach((s, idx) => {
    const xPos = 0.5 + idx * 1.5;

    slide.addShape(pres.shapes.RECTANGLE, {
      x: xPos,
      y: 1.2,
      w: 1.3,
      h: 0.8,
      fill: { color: s.color },
      line: { color: colors.charcoal, width: 1 },
    });

    slide.addText(s.stage, {
      x: xPos,
      y: 1.2,
      w: 1.3,
      h: 0.8,
      fontFace: "Georgia",
      fontSize: 10,
      bold: true,
      color: colors.offWhite,
      align: "center",
      valign: "middle",
    });

    // Arrow to next stage
    if (idx < stages.length - 1) {
      slide.addShape(pres.shapes.LINE, {
        x: xPos + 1.35,
        y: 1.56,
        w: 0.12,
        h: 0,
        line: { color: colors.charcoal, width: 2 },
      });

      slide.addShape(pres.shapes.RECTANGLE, {
        x: xPos + 1.42,
        y: 1.53,
        w: 0.08,
        h: 0.06,
        fill: { color: colors.charcoal },
      });
    }
  });

  // Test results
  slide.addText("Test Results & Quality Metrics", {
    x: 0.5,
    y: 2.4,
    w: 9,
    fontFace: "Georgia",
    fontSize: 14,
    bold: true,
    color: colors.charcoal,
  });

  const metrics = [
    { metric: "Total Tests", value: "74", color: colors.teal },
    { metric: "Pass Rate", value: "97%", color: colors.teal },
    { metric: "Code Coverage", value: "85%+", color: colors.teal },
  ];

  metrics.forEach((m, idx) => {
    const xPos = 0.5 + idx * 3.0;

    slide.addShape(pres.shapes.RECTANGLE, {
      x: xPos,
      y: 3.0,
      w: 2.8,
      h: 1.2,
      fill: { color: colors.light },
      line: { color: colors.teal, width: 2 },
    });

    slide.addText(m.value, {
      x: xPos,
      y: 3.15,
      w: 2.8,
      h: 0.5,
      fontFace: "Georgia",
      fontSize: 28,
      bold: true,
      color: m.color,
      align: "center",
    });

    slide.addText(m.metric, {
      x: xPos,
      y: 3.7,
      w: 2.8,
      h: 0.4,
      fontFace: "Calibri",
      fontSize: 11,
      color: colors.mediumGray,
      align: "center",
    });
  });

  slide.addText("GitHub Actions automates all stages; deployment occurs automatically on merge to main", {
    x: 0.5,
    y: 4.5,
    w: 9,
    h: 1.0,
    fontFace: "Calibri",
    fontSize: 11,
    italic: true,
    color: colors.mediumGray,
  });
}

// SLIDE 14: Monitoring & Health Checks
function addMonitoringSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Monitoring & Health Checks", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  slide.addText("Status Endpoint: /api/v1/status", {
    x: 0.5,
    y: 1.1,
    w: 9,
    fontFace: "Georgia",
    fontSize: 13,
    bold: true,
    color: colors.charcoal,
  });

  const statusCode =
    `GET /api/v1/status
{
  "status": "healthy",
  "timestamp": "2026-03-08T15:30:00Z",
  "loaded_modules": 42,
  "failed_modules": 0,
  "total_routes": 339
}`;

  slide.addText(statusCode, {
    x: 0.5,
    y: 1.6,
    w: 9,
    h: 1.5,
    fontFace: "Consolas",
    fontSize: 9,
    color: colors.charcoal,
    fill: { color: colors.light },
    align: "left",
  });

  slide.addText("Monitoring Capabilities", {
    x: 0.5,
    y: 3.3,
    w: 9,
    fontFace: "Georgia",
    fontSize: 13,
    bold: true,
    color: colors.charcoal,
  });

  const monitoring = [
    { item: "Module Loading", desc: "Tracks dynamically loaded API modules (42 agents)" },
    { item: "Route Verification", desc: "Validates all 339 routes are registered and accessible" },
    { item: "Failure Tracking", desc: "Reports failed module imports for debugging" },
    { item: "Uptime Monitoring", desc: "Integration with Vercel Analytics for performance metrics" },
  ];

  monitoring.forEach((m, idx) => {
    const yPos = 3.8 + idx * 0.65;

    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5,
      y: yPos,
      w: 0.08,
      h: 0.6,
      fill: { color: colors.teal },
    });

    slide.addText(m.item, {
      x: 0.75,
      y: yPos,
      w: 2.0,
      h: 0.3,
      fontFace: "Georgia",
      fontSize: 11,
      bold: true,
      color: colors.teal,
    });

    slide.addText(m.desc, {
      x: 2.9,
      y: yPos,
      w: 6.6,
      h: 0.6,
      fontFace: "Calibri",
      fontSize: 10,
      color: colors.mediumGray,
    });
  });
}

// SLIDE 15: Security Checklist
function addSecuritySlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Security Checklist", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  const checklist = [
    { check: "JWT Configuration", item: "HS256 algorithm with 32-byte secret minimum" },
    { check: "CORS Settings", item: "Whitelist approved origins; deny wildcard origins" },
    { check: "Role-Based Access", item: "RBAC enforced at API level with @require_role" },
    { check: "Password Hashing", item: "bcrypt with 12-round salt cost" },
    { check: "Organization Isolation", item: "TenantContext prevents cross-org data access" },
    { check: "HTTPS/TLS", item: "All traffic encrypted in production via Vercel" },
  ];

  checklist.forEach((item, idx) => {
    const yPos = 1.2 + idx * 0.65;

    // Check icon (using rectangle as proxy)
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.6,
      y: yPos + 0.05,
      w: 0.25,
      h: 0.25,
      fill: { color: colors.teal },
    });

    slide.addText("✓", {
      x: 0.6,
      y: yPos + 0.05,
      w: 0.25,
      h: 0.25,
      fontFace: "Georgia",
      fontSize: 14,
      bold: true,
      color: colors.offWhite,
      align: "center",
      valign: "middle",
    });

    // Check name
    slide.addText(item.check, {
      x: 1.1,
      y: yPos,
      w: 2.2,
      h: 0.35,
      fontFace: "Georgia",
      fontSize: 11,
      bold: true,
      color: colors.charcoal,
    });

    // Description
    slide.addText(item.item, {
      x: 3.5,
      y: yPos,
      w: 5.9,
      h: 0.6,
      fontFace: "Calibri",
      fontSize: 10,
      color: colors.mediumGray,
    });
  });
}

// SLIDE 16: Scaling Considerations
function addScalingSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Scaling Considerations", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  const scalingStrategies = [
    { strategy: "Horizontal Scaling", desc: "Vercel automatically scales serverless functions based on load" },
    { strategy: "DB Connection Pooling", desc: "PgBouncer/Vercel Postgres maintains efficient connection reuse" },
    { strategy: "Caching Strategy", desc: "Redis for session management and computed result caching" },
    { strategy: "CDN Static Assets", desc: "Vercel CDN distributes frontend bundles to edge locations globally" },
    { strategy: "Rate Limiting", desc: "Implemented per-tenant with sliding window algorithm" },
    { strategy: "Async Processing", desc: "Celery/RabbitMQ for long-running background tasks" },
  ];

  let yPos = 1.2;
  scalingStrategies.forEach((item) => {
    // Strategy name
    slide.addText(item.strategy, {
      x: 0.5,
      y: yPos,
      w: 2.4,
      h: 0.35,
      fontFace: "Georgia",
      fontSize: 11,
      bold: true,
      color: colors.teal,
    });

    // Description
    slide.addText(item.desc, {
      x: 3.1,
      y: yPos,
      w: 6.4,
      h: 0.5,
      fontFace: "Calibri",
      fontSize: 10,
      color: colors.mediumGray,
    });

    yPos += 0.65;
  });
}

// SLIDE 17: Troubleshooting
function addTroubleshootingSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Troubleshooting Common Issues", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  const issues = [
    { problem: "Module Import Failures", solution: "Check PYTHONPATH; verify __init__.py files exist" },
    { problem: "Enum Name vs Value Bugs", solution: "Use .value for comparison; validate enum assignments" },
    { problem: "SQLAlchemy Async Issues", solution: "Use AsyncSession context manager; await all queries" },
    { problem: "CORS Errors", solution: "Verify CORS_ORIGINS env var; check browser console for blocked requests" },
    { problem: "JWT Token Expiration", solution: "Refresh token before expiry (24 hours); check system clock" },
  ];

  const tableData = [
    [
      { text: "Issue", options: { bold: true, color: colors.offWhite } },
      { text: "Solution", options: { bold: true, color: colors.offWhite } },
    ],
    ...issues.map((i) => [{ text: i.problem }, { text: i.solution }]),
  ];

  slide.addTable(tableData, {
    x: 0.5,
    y: 1.2,
    w: 9,
    h: 3.8,
    colW: [2.8, 6.2],
    border: { pt: 1, color: colors.lightGray },
    fill: { color: colors.light },
    valign: "top",
    fontSize: 10,
  });
}

// SLIDE 18: Rollback Procedures
function addRollbackSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Rollback Procedures", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  const rollbackSteps = [
    { type: "Vercel Rollback", desc: "Instant rollback to previous deployment within Vercel dashboard" },
    { type: "Database Rollback", desc: "Run previous Alembic migration or restore from backup" },
    { type: "Feature Flags", desc: "Disable problematic feature without full rollback via environment variable" },
    { type: "Blue-Green Deploy", desc: "Maintain two production environments for zero-downtime rollback" },
  ];

  rollbackSteps.forEach((step, idx) => {
    const yPos = 1.3 + idx * 1.0;

    // Type box
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5,
      y: yPos,
      w: 2.0,
      h: 0.8,
      fill: { color: colors.charcoal },
    });

    slide.addText(step.type, {
      x: 0.5,
      y: yPos,
      w: 2.0,
      h: 0.8,
      fontFace: "Georgia",
      fontSize: 11,
      bold: true,
      color: colors.offWhite,
      align: "center",
      valign: "middle",
    });

    // Description
    slide.addText(step.desc, {
      x: 2.7,
      y: yPos,
      w: 6.8,
      h: 0.8,
      fontFace: "Calibri",
      fontSize: 11,
      color: colors.mediumGray,
      valign: "middle",
    });
  });
}

// SLIDE 19: Quick Reference
function addQuickReferenceSlide() {
  const slide = pres.addSlide();
  slide.background = { color: colors.offWhite };

  slide.addText("Quick Reference — Command Cheat Sheet", makeHeadingOpts({ y: 0.4, x: 0.5 }));

  const commands = [
    { cmd: "npm run build", desc: "Frontend: Vite build production bundle" },
    { cmd: "vercel deploy --prod", desc: "Deploy to production immediately" },
    { cmd: "pytest --cov", desc: "Run all tests with coverage report" },
    { cmd: "python seed_data.py", desc: "Populate demo data into database" },
    { cmd: "alembic upgrade head", desc: "Run pending database migrations" },
    { cmd: "uvicorn api.main:app", desc: "Start backend dev server (localhost:8000)" },
  ];

  const cmdData = [
    [
      { text: "Command", options: { bold: true, color: colors.offWhite, fontFace: "Consolas", fontSize: 10 } },
      { text: "Description", options: { bold: true, color: colors.offWhite } },
    ],
    ...commands.map((c) => [
      { text: c.cmd, fontFace: "Consolas", fontSize: 10 },
      { text: c.desc },
    ]),
  ];

  slide.addTable(cmdData, {
    x: 0.5,
    y: 1.2,
    w: 9,
    h: 4.0,
    colW: [2.8, 6.2],
    border: { pt: 1, color: colors.lightGray },
    fill: { color: colors.light },
    valign: "middle",
    fontSize: 10,
  });
}

// Generate all slides
addTitleSlide();
addTableOfContents();
addArchitectureSlide();
addPrerequisitesSlide();
addRepoStructureSlide();
addEnvironmentSlide();
addLocalDevSlide();
addBackendDeploymentSlide();
addFrontendDeploySlide();
addDatabaseSlide();
addMultiTenantSlide();
addSeedDataSlide();
addCICDSlide();
addMonitoringSlide();
addSecuritySlide();
addScalingSlide();
addTroubleshootingSlide();
addRollbackSlide();
addQuickReferenceSlide();

// Write output
pres.writeFile({ fileName: "/sessions/awesome-youthful-maxwell/mnt/outputs/HotGigs_Deployment_Guide.pptx" });

console.log("PowerPoint presentation created successfully!");
console.log("File: /sessions/awesome-youthful-maxwell/mnt/outputs/HotGigs_Deployment_Guide.pptx");
