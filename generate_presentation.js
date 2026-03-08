const PptxGenJS = require("pptxgenjs");

const pres = new PptxGenJS();
pres.layout = "LAYOUT_16x9";
pres.author = "HotGigs";
pres.title = "HotGigs 2026 — Complete Feature Guide";

// Color palette
const colors = {
  primary: "028090",      // Teal
  secondary: "00A896",    // Seafoam
  accent: "02C39A",       // Mint
  dark: "05668D",         // Deep teal
  light: "F0FDFB",        // Light
  white: "FFFFFF",
  gray: "64748B",
  lightGray: "E2E8F0",
};

// Helper functions
function makeShadow() {
  return { type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 };
}

function makeTextOptions(size = 14, bold = false, color = colors.dark) {
  return { fontSize: size, bold, color, fontFace: "Calibri" };
}

function makeHeadingOptions(size = 40, color = colors.dark) {
  return { fontSize: size, bold: true, color, fontFace: "Georgia" };
}

function addAccentBar(slide, x, y, height) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: x,
    y: y,
    w: 0.08,
    h: height,
    fill: { color: colors.accent },
    line: { type: "none" },
  });
}

// ============= SLIDE 1: TITLE =============
const slide1 = pres.addSlide();
slide1.background = { color: colors.dark };

slide1.addText("HotGigs 2026", {
  x: 0.5,
  y: 1.5,
  w: 9,
  h: 1,
  ...makeHeadingOptions(60, colors.white),
  align: "center",
});

slide1.addText("Complete Feature Guide", {
  x: 0.5,
  y: 2.7,
  w: 9,
  h: 0.8,
  ...makeHeadingOptions(48, colors.accent),
  align: "center",
});

slide1.addText("Enterprise HR Automation Platform — Every Feature Explained", {
  x: 0.5,
  y: 3.8,
  w: 9,
  h: 0.6,
  ...makeTextOptions(22, false, colors.secondary),
  align: "center",
});

// ============= SLIDE 2: TABLE OF CONTENTS =============
const slide2 = pres.addSlide();
slide2.background = { color: colors.light };

slide2.addText("Table of Contents", {
  x: 0.5,
  y: 0.4,
  w: 9,
  h: 0.6,
  ...makeHeadingOptions(44, colors.dark),
});

addAccentBar(slide2, 0.5, 1.05, 4.2);

const tocItems = [
  "1. Core Platform (Auth & Analytics) — Slides 4-5",
  "2. Recruitment Pipeline (Resume to Offer) — Slides 6-10",
  "3. VMS/MSP Architecture (Multi-Tenant) — Slides 11-14",
  "4. Rate Card Management — Slides 15-16",
  "5. Compliance Engine — Slides 17-18",
  "6. SLA Management — Slides 19-20",
  "7. Timesheet & Invoicing — Slides 21-22",
  "8. AI Agents (42 Smart Agents) — Slides 23-24",
  "9. Communication & Sourcing — Slides 25-26",
  "10. Reports & Administration — Slides 27-28",
];

slide2.addText(
  tocItems.map((item, idx) => ({
    text: item,
    options: { bullet: true, breakLine: idx < tocItems.length - 1 },
  })),
  {
    x: 1,
    y: 1.2,
    w: 8.5,
    h: 4,
    ...makeTextOptions(18, false, colors.dark),
    valign: "top",
  }
);

// ============= SLIDE 3: FEATURE OVERVIEW =============
const slide3 = pres.addSlide();
slide3.background = { color: colors.white };

slide3.addText("Feature Overview Dashboard", {
  x: 0.5,
  y: 0.4,
  w: 9,
  h: 0.6,
  ...makeHeadingOptions(44, colors.dark),
});

addAccentBar(slide3, 0.5, 1.05, 5);

const statBoxes = [
  { label: "Feature Categories", value: "12" },
  { label: "API Endpoints", value: "339" },
  { label: "AI Agents", value: "42" },
  { label: "Portal Types", value: "3" },
  { label: "Database Tables", value: "94+" },
  { label: "Test Cases", value: "74" },
];

let xPos = 0.8;
statBoxes.forEach((stat) => {
  slide3.addShape(pres.shapes.RECTANGLE, {
    x: xPos,
    y: 1.3,
    w: 1.45,
    h: 3.8,
    fill: { color: colors.light },
    line: { color: colors.secondary, width: 2 },
    shadow: makeShadow(),
  });

  slide3.addText(stat.value, {
    x: xPos,
    y: 2,
    w: 1.45,
    h: 0.8,
    ...makeHeadingOptions(48, colors.accent),
    align: "center",
  });

  slide3.addText(stat.label, {
    x: xPos,
    y: 3,
    w: 1.45,
    h: 1.5,
    ...makeTextOptions(13, true, colors.dark),
    align: "center",
    valign: "middle",
  });

  xPos += 1.55;
});

// ============= SLIDE 4: AUTHENTICATION & USER MANAGEMENT =============
const slide4 = pres.addSlide();
slide4.background = { color: colors.white };

slide4.addText("Authentication & User Management", {
  x: 0.5,
  y: 0.4,
  w: 9,
  h: 0.6,
  ...makeHeadingOptions(40, colors.dark),
});

addAccentBar(slide4, 0.5, 1.05, 5);

const authFeatures = [
  "JWT-based authentication with refresh tokens",
  "Multi-organization login support",
  "Role-based access control (RBAC)",
  "Seamless organization switching",
  "5 Role Types:",
  { text: "SUPER_ADMIN, MSP_ADMIN, CLIENT_MANAGER", options: { indentLevel: 1 } },
  { text: "SUPPLIER_RECRUITER, RECRUITER", options: { indentLevel: 1 } },
  "Audit logging for all authentication events",
];

slide4.addText(
  authFeatures.map((feat, idx) => ({
    text: typeof feat === "string" ? feat : feat.text,
    options: {
      bullet: true,
      breakLine: idx < authFeatures.length - 1,
      ...(typeof feat === "string" ? {} : feat.options),
    },
  })),
  {
    x: 0.8,
    y: 1.2,
    w: 5.5,
    h: 4,
    ...makeTextOptions(15, false, colors.dark),
  }
);

// Right side visual
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 6.5,
  y: 1.2,
  w: 3,
  h: 1.8,
  fill: { color: colors.secondary },
  line: { type: "none" },
});

slide4.addText("Multi-Organization Support", {
  x: 6.5,
  y: 1.4,
  w: 3,
  h: 1.4,
  ...makeTextOptions(16, true, colors.white),
  align: "center",
  valign: "middle",
});

slide4.addShape(pres.shapes.RECTANGLE, {
  x: 6.5,
  y: 3.2,
  w: 3,
  h: 1.8,
  fill: { color: colors.accent },
  line: { type: "none" },
});

slide4.addText("Granular Role Control", {
  x: 6.5,
  y: 3.4,
  w: 3,
  h: 1.4,
  ...makeTextOptions(16, true, colors.white),
  align: "center",
  valign: "middle",
});

// ============= SLIDE 5: DASHBOARD & ANALYTICS =============
const slide5 = pres.addSlide();
slide5.background = { color: colors.white };

slide5.addText("Dashboard & Analytics", {
  x: 0.5,
  y: 0.4,
  w: 9,
  h: 0.6,
  ...makeHeadingOptions(40, colors.dark),
});

addAccentBar(slide5, 0.5, 1.05, 5);

const dashboardFeatures = [
  "Real-time metrics and KPI tracking",
  "Customizable widget system",
  "Role-specific dashboards:",
  { text: "MSP View: Client/Supplier overview", options: { indentLevel: 1 } },
  { text: "Client View: Spend & compliance", options: { indentLevel: 1 } },
  { text: "Supplier View: Placements & revenue", options: { indentLevel: 1 } },
  "Drill-down capabilities to detail pages",
  "Export metrics to CSV/PDF",
  "Real-time data refresh every 30 seconds",
];

slide5.addText(
  dashboardFeatures.map((feat, idx) => ({
    text: typeof feat === "string" ? feat : feat.text,
    options: {
      bullet: true,
      breakLine: idx < dashboardFeatures.length - 1,
      ...(typeof feat === "string" ? {} : feat.options),
    },
  })),
  {
    x: 0.8,
    y: 1.2,
    w: 5.5,
    h: 4,
    ...makeTextOptions(15, false, colors.dark),
  }
);

// Right side
slide5.addShape(pres.shapes.RECTANGLE, {
  x: 6.5,
  y: 1.2,
  w: 3,
  h: 1.8,
  fill: { color: colors.primary },
  line: { type: "none" },
});

slide5.addText("Real-Time Tracking", {
  x: 6.5,
  y: 1.4,
  w: 3,
  h: 1.4,
  ...makeTextOptions(16, true, colors.white),
  align: "center",
  valign: "middle",
});

slide5.addShape(pres.shapes.RECTANGLE, {
  x: 6.5,
  y: 3.2,
  w: 3,
  h: 1.8,
  fill: { color: colors.dark },
  line: { type: "none" },
});

slide5.addText("Custom Dashboards", {
  x: 6.5,
  y: 3.4,
  w: 3,
  h: 1.4,
  ...makeTextOptions(16, true, colors.white),
  align: "center",
  valign: "middle",
});

// ============= SLIDE 6: RESUME PARSING & MANAGEMENT =============
const slide6 = pres.addSlide();
slide6.background = { color: colors.white };

slide6.addText("Resume Parsing & Management", {
  x: 0.5,
  y: 0.4,
  w: 9,
  h: 0.6,
  ...makeHeadingOptions(40, colors.dark),
});

addAccentBar(slide6, 0.5, 1.05, 5);

const resumeFeatures = [
  "AI-powered resume parsing with NLP",
  "Automatic skill extraction & normalization",
  "Multi-format support:",
  { text: "PDF, DOCX, LinkedIn profiles", options: { indentLevel: 1 } },
  { text: "Plain text, RTF", options: { indentLevel: 1 } },
  "Comprehensive candidate database",
  "Full-text search with filters",
  "Experience level detection",
  "Duplicate detection & merging",
  "NEW: AI-powered skill recommendations",
];

slide6.addText(
  resumeFeatures.map((feat, idx) => ({
    text: typeof feat === "string" ? feat : feat.text,
    options: {
      bullet: true,
      breakLine: idx < resumeFeatures.length - 1,
      ...(typeof feat === "string" ? {} : feat.options),
    },
  })),
  {
    x: 0.8,
    y: 1.2,
    w: 5.5,
    h: 4,
    ...makeTextOptions(15, false, colors.dark),
  }
);

slide6.addShape(pres.shapes.RECTANGLE, {
  x: 6.5,
  y: 1.2,
  w: 3,
  h: 1.8,
  fill: { color: colors.accent },
  line: { type: "none" },
});

slide6.addText("Multi-Format Support", {
  x: 6.5,
  y: 1.4,
  w: 3,
  h: 1.4,
  ...makeTextOptions(16, true, colors.white),
  align: "center",
  valign: "middle",
});

slide6.addShape(pres.shapes.RECTANGLE, {
  x: 6.5,
  y: 3.2,
  w: 3,
  h: 1.8,
  fill: { color: colors.secondary },
  line: { type: "none" },
});

slide6.addText("Smart Skill Extraction", {
  x: 6.5,
  y: 3.4,
  w: 3,
  h: 1.4,
  ...makeTextOptions(16, true, colors.white),
  align: "center",
  valign: "middle",
});

// [Additional slides 7-30 continue in similar pattern...]
// Due to length, generating all 30 slides with complete feature coverage

// ============= SLIDE 7: INTELLIGENT MATCHING ENGINE =============
const slide7 = pres.addSlide();
slide7.background = { color: colors.white };
slide7.addText("Intelligent Matching Engine", {
  x: 0.5,
  y: 0.4,
  w: 9,
  h: 0.6,
  ...makeHeadingOptions(40, colors.dark),
});
addAccentBar(slide7, 0.5, 1.05, 5);
slide7.addText([
  { text: "4-Factor Weighted Scoring Algorithm", options: { bold: true, breakLine: true } },
  { text: "Skills Match: 40%", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Experience Level: 25%", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Location Proximity: 15%", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Availability & Preferences: 20%", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Ranked candidate lists by match score", options: { bullet: true, breakLine: true } },
  { text: "Configurable matching thresholds", options: { bullet: true, breakLine: true } },
  { text: "Re-ranking based on placement history", options: { bullet: true, breakLine: true } },
  { text: "ENHANCED: Multi-skill matching support", options: { bullet: true } },
], { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(14, false, colors.dark) });

slide7.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 3.8, fill: { color: colors.light }, line: { color: colors.primary, width: 2 } });
slide7.addText("Scoring Weights", { x: 6.5, y: 1.4, w: 3, h: 0.5, ...makeHeadingOptions(18, colors.dark), align: "center" });

const weights = [
  { label: "Skills", pct: "40%", color: colors.accent },
  { label: "Experience", pct: "25%", color: colors.secondary },
  { label: "Location", pct: "15%", color: colors.primary },
  { label: "Availability", pct: "20%", color: colors.dark },
];
let yPos = 2.1;
weights.forEach((w) => {
  slide7.addText(w.label, { x: 6.7, y: yPos, w: 1.3, h: 0.4, ...makeTextOptions(12, false, colors.dark) });
  slide7.addText(w.pct, { x: 8.2, y: yPos, w: 0.8, h: 0.4, ...makeTextOptions(12, true, w.color), align: "right" });
  yPos += 0.6;
});

// ============= SLIDE 8: INTERVIEW MANAGEMENT =============
const slide8 = pres.addSlide();
slide8.background = { color: colors.white };
slide8.addText("Interview Management", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide8, 0.5, 1.05, 5);
const interviewFeatures = [
  "Scheduling with conflict detection",
  "Feedback collection & scoring",
  "Panel interview coordination",
  "Video interview integration (Zoom/Teams)",
  "Automated reminder notifications",
  "AI scheduling agent (slot optimization)",
  "Interview feedback templates",
  "Candidate availability sync",
  "Interview notes & collaboration",
  "NEW: AI-powered interview insights",
];
slide8.addText(interviewFeatures.map((feat, idx) => ({ text: feat, options: { bullet: true, breakLine: idx < interviewFeatures.length - 1 } })), { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(15, false, colors.dark) });
slide8.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.primary }, line: { type: "none" } });
slide8.addText("Smart Scheduling", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide8.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.accent }, line: { type: "none" } });
slide8.addText("Video Integration", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 9: SUBMISSION & OFFER MANAGEMENT =============
const slide9 = pres.addSlide();
slide9.background = { color: colors.white };
slide9.addText("Submission & Offer Management", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide9, 0.5, 1.05, 5);
const submissionFeatures = [
  "Candidate submission workflow",
  "Client approval routing",
  "Automated offer generation",
  "E-signature ready documents",
  "Counter-offer negotiation",
  "Offer expiration tracking",
  "Multi-level approval chains",
  "Submission analytics & tracking",
  "Status notifications & reminders",
  "ENHANCED: Batch offer generation",
];
slide9.addText(submissionFeatures.map((feat, idx) => ({ text: feat, options: { bullet: true, breakLine: idx < submissionFeatures.length - 1 } })), { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(15, false, colors.dark) });
slide9.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.secondary }, line: { type: "none" } });
slide9.addText("Automated Workflows", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide9.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.dark }, line: { type: "none" } });
slide9.addText("E-Signature Ready", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 10: CANDIDATE PORTAL =============
const slide10 = pres.addSlide();
slide10.background = { color: colors.white };
slide10.addText("Candidate Portal", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide10, 0.5, 1.05, 5);
const portalFeatures = [
  "Self-service candidate dashboard",
  "Application status tracking",
  "Document upload & management",
  "Interview scheduling access",
  "Profile editing & updates",
  "Communication history",
  "Availability management",
  "Preference settings",
  "Mobile-responsive design",
  "NEW: In-app messaging",
];
slide10.addText(portalFeatures.map((feat, idx) => ({ text: feat, options: { bullet: true, breakLine: idx < portalFeatures.length - 1 } })), { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(15, false, colors.dark) });
slide10.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.accent }, line: { type: "none" } });
slide10.addText("Candidate Control", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide10.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.primary }, line: { type: "none" } });
slide10.addText("Transparent Tracking", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 11: MULTI-TENANT ARCHITECTURE =============
const slide11 = pres.addSlide();
slide11.background = { color: colors.white };
slide11.addText("Multi-Tenant Architecture", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide11, 0.5, 1.05, 5);
slide11.addText([
  { text: "3 Organization Types", options: { bold: true, breakLine: true } },
  { text: "MSP (Managed Service Provider)", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "CLIENT (Hiring Company)", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "SUPPLIER (Staffing Partner)", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Complete tenant isolation & security", options: { bullet: true, breakLine: true } },
  { text: "Role-based portal access control", options: { bullet: true, breakLine: true } },
  { text: "Data partitioning at DB level", options: { bullet: true, breakLine: true } },
  { text: "Cross-org collaboration workflows", options: { bullet: true, breakLine: true } },
  { text: "Organization hierarchy management", options: { bullet: true } },
], { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(14, false, colors.dark) });

slide11.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.1, fill: { color: colors.primary }, line: { type: "none" } });
slide11.addText("MSP", { x: 6.5, y: 1.35, w: 3, h: 0.8, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide11.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 2.5, w: 1.4, h: 1.1, fill: { color: colors.secondary }, line: { type: "none" } });
slide11.addText("CLIENT", { x: 6.5, y: 2.65, w: 1.4, h: 0.8, ...makeTextOptions(12, true, colors.white), align: "center", valign: "middle" });
slide11.addShape(pres.shapes.RECTANGLE, { x: 8.1, y: 2.5, w: 1.4, h: 1.1, fill: { color: colors.accent }, line: { type: "none" } });
slide11.addText("SUPPLIER", { x: 8.1, y: 2.65, w: 1.4, h: 0.8, ...makeTextOptions(12, true, colors.white), align: "center", valign: "middle" });
slide11.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.8, w: 3, h: 1.2, fill: { color: colors.light }, line: { color: colors.dark, width: 2 } });
slide11.addText("Secure Data\nPartitioning", { x: 6.5, y: 4, w: 3, h: 0.8, ...makeTextOptions(13, true, colors.dark), align: "center", valign: "middle" });

// ============= SLIDE 12: MSP PORTAL FEATURES =============
const slide12 = pres.addSlide();
slide12.background = { color: colors.white };
slide12.addText("MSP Portal Features", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide12, 0.5, 1.05, 5);
const mspFeatures = [
  "Client management & onboarding",
  "Supplier network administration",
  "Submissions pipeline oversight",
  "Rate card configuration & validation",
  "Compliance requirement management",
  "SLA monitoring & breach alerts",
  "VMS timesheet approval workflow",
  "Revenue & margin analytics",
  "Performance reporting",
  "NEW: Automated invoice processing",
];
slide12.addText(mspFeatures.map((feat, idx) => ({ text: feat, options: { bullet: true, breakLine: idx < mspFeatures.length - 1 } })), { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(15, false, colors.dark) });
slide12.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.dark }, line: { type: "none" } });
slide12.addText("Full Control", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide12.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.secondary }, line: { type: "none" } });
slide12.addText("Network Hub", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 13: CLIENT PORTAL FEATURES =============
const slide13 = pres.addSlide();
slide13.background = { color: colors.white };
slide13.addText("Client Portal Features", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide13, 0.5, 1.05, 5);
const clientFeatures = [
  "Executive dashboard overview",
  "Requisition management",
  "Submission review & approval",
  "Timesheet approval workflow",
  "Spend analytics & budgeting",
  "Supplier performance scorecard",
  "Compliance tracking",
  "Interview scheduling access",
  "Placement visibility",
  "NEW: Budget forecasting",
];
slide13.addText(clientFeatures.map((feat, idx) => ({ text: feat, options: { bullet: true, breakLine: idx < clientFeatures.length - 1 } })), { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(15, false, colors.dark) });
slide13.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.accent }, line: { type: "none" } });
slide13.addText("Clear Visibility", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide13.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.primary }, line: { type: "none" } });
slide13.addText("Control & Approval", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 14: SUPPLIER PORTAL FEATURES =============
const slide14 = pres.addSlide();
slide14.background = { color: colors.white };
slide14.addText("Supplier Portal Features", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide14, 0.5, 1.05, 5);
const supplierFeatures = [
  "Supplier dashboard & KPIs",
  "Candidate submission management",
  "Timesheet entry & tracking",
  "Placement visibility",
  "Revenue & commission analytics",
  "Performance metrics & ratings",
  "Compliance status tracking",
  "Opportunity alerts",
  "Communication hub",
  "NEW: Earnings forecast",
];
slide14.addText(supplierFeatures.map((feat, idx) => ({ text: feat, options: { bullet: true, breakLine: idx < supplierFeatures.length - 1 } })), { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(15, false, colors.dark) });
slide14.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.secondary }, line: { type: "none" } });
slide14.addText("Self Service", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide14.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.dark }, line: { type: "none" } });
slide14.addText("Analytics", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 15: RATE CARD SYSTEM =============
const slide15 = pres.addSlide();
slide15.background = { color: colors.white };
slide15.addText("Rate Card System", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide15, 0.5, 1.05, 5);
slide15.addText([
  { text: "Complete Rate Management", options: { bold: true, breakLine: true } },
  { text: "Job category-based rates", options: { bullet: true, breakLine: true } },
  { text: "Location-based pricing", options: { bullet: true, breakLine: true } },
  { text: "Skill level multipliers", options: { bullet: true, breakLine: true } },
  { text: "Bill & pay rate ranges", options: { bullet: true, breakLine: true } },
  { text: "Overtime & weekend multipliers", options: { bullet: true, breakLine: true } },
  { text: "Shift premium rates", options: { bullet: true, breakLine: true } },
  { text: "Multi-currency support", options: { bullet: true, breakLine: true } },
  { text: "Effective date management", options: { bullet: true } },
], { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(14, false, colors.dark) });
slide15.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.primary }, line: { type: "none" } });
slide15.addText("Flexible Pricing", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide15.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.accent }, line: { type: "none" } });
slide15.addText("Global Support", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 16: RATE VALIDATION =============
const slide16 = pres.addSlide();
slide16.background = { color: colors.white };
slide16.addText("Rate Validation Engine", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide16, 0.5, 1.05, 5);
slide16.addText([
  { text: "4-Factor AI-Powered Scoring", options: { bold: true, breakLine: true } },
  { text: "Rate Card Alignment: 40%", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Historical Data: 30%", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Margin Analysis: 20%", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Market Benchmarking: 10%", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Recommendations: APPROVE / REVIEW / REJECT", options: { bullet: true, breakLine: true } },
  { text: "Suggested rate adjustments", options: { bullet: true, breakLine: true } },
  { text: "Compliance check against MSP guidelines", options: { bullet: true, breakLine: true } },
  { text: "NEW: Automated rate negotiation", options: { bullet: true } },
], { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(13.5, false, colors.dark) });
slide16.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 3.8, fill: { color: colors.light }, line: { color: colors.secondary, width: 2 } });
slide16.addText("Validation Factors", { x: 6.5, y: 1.4, w: 3, h: 0.5, ...makeHeadingOptions(16, colors.dark), align: "center" });

const rateFactors = [
  { label: "Rate Card", pct: "40%", color: colors.accent },
  { label: "Historical", pct: "30%", color: colors.primary },
  { label: "Margin", pct: "20%", color: colors.secondary },
  { label: "Market", pct: "10%", color: colors.dark },
];
yPos = 2.1;
rateFactors.forEach((f) => {
  slide16.addText(f.label, { x: 6.7, y: yPos, w: 1.3, h: 0.4, ...makeTextOptions(11, false, colors.dark) });
  slide16.addText(f.pct, { x: 8.2, y: yPos, w: 0.8, h: 0.4, ...makeTextOptions(11, true, f.color), align: "right" });
  yPos += 0.6;
});

// ============= SLIDE 17: COMPLIANCE MANAGEMENT =============
const slide17 = pres.addSlide();
slide17.background = { color: colors.white };
slide17.addText("Compliance Management", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide17, 0.5, 1.05, 5);
slide17.addText([
  { text: "7 Compliance Types Tracked", options: { bold: true, breakLine: true } },
  { text: "Background Checks", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Drug Screening", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Certifications & Licenses", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Insurance Verification", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Training & Competency", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Mandatory/optional status tracking", options: { bullet: true, breakLine: true } },
  { text: "Configurable renewal frequencies", options: { bullet: true, breakLine: true } },
  { text: "Risk level assessment", options: { bullet: true, breakLine: true } },
  { text: "Document verification & approval", options: { bullet: true } },
], { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(13, false, colors.dark) });
slide17.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.dark }, line: { type: "none" } });
slide17.addText("Regulatory Ready", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide17.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.accent }, line: { type: "none" } });
slide17.addText("Risk Control", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 18: COMPLIANCE SCORING & MONITORING =============
const slide18 = pres.addSlide();
slide18.background = { color: colors.white };
slide18.addText("Compliance Scoring & Monitoring", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide18, 0.5, 1.05, 5);
const complianceFeatures = [
  "Supplier compliance scores (0-100)",
  "Gap detection & flagging",
  "Expiration alerts (30-day lookahead)",
  "Placement-level compliance checks",
  "Automated risk assessment",
  "Compliance dashboard & analytics",
  "Bulk compliance updates",
  "Template-based requirements",
  "Audit trail & documentation",
  "NEW: Predictive compliance alerts",
];
slide18.addText(complianceFeatures.map((feat, idx) => ({ text: feat, options: { bullet: true, breakLine: idx < complianceFeatures.length - 1 } })), { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(15, false, colors.dark) });
slide18.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.secondary }, line: { type: "none" } });
slide18.addText("Proactive Monitoring", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide18.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.primary }, line: { type: "none" } });
slide18.addText("Score Tracking", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 19: SLA CONFIGURATION =============
const slide19 = pres.addSlide();
slide19.background = { color: colors.white };
slide19.addText("SLA Configuration", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide19, 0.5, 1.05, 5);
slide19.addText([
  { text: "5 Core SLA Metrics", options: { bold: true, breakLine: true } },
  { text: "Response Time: Initial contact requirement", options: { bullet: true, breakLine: true } },
  { text: "Fill Time: Placement completion window", options: { bullet: true, breakLine: true } },
  { text: "Quality Score: Candidate fit rating", options: { bullet: true, breakLine: true } },
  { text: "Acceptance Rate: Submission success %", options: { bullet: true, breakLine: true } },
  { text: "Retention: Employee tenure metrics", options: { bullet: true, breakLine: true } },
  { text: "Configurable thresholds per SLA", options: { bullet: true, breakLine: true } },
  { text: "Penalty amounts & terms", options: { bullet: true, breakLine: true } },
  { text: "Cumulative/Maximum calculation modes", options: { bullet: true } },
], { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(13.5, false, colors.dark) });
slide19.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.accent }, line: { type: "none" } });
slide19.addText("Custom KPIs", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide19.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.dark }, line: { type: "none" } });
slide19.addText("Performance Goals", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 20: BREACH DETECTION & RESOLUTION =============
const slide20 = pres.addSlide();
slide20.background = { color: colors.white };
slide20.addText("Breach Detection & Resolution", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide20, 0.5, 1.05, 5);
slide20.addText([
  { text: "4 Severity Levels", options: { bold: true, breakLine: true } },
  { text: "CRITICAL (Immediate escalation)", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "HIGH (24-hour notification)", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "MEDIUM (48-hour notification)", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "LOW (Administrative tracking)", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Automated breach detection engine", options: { bullet: true, breakLine: true } },
  { text: "Breach recording & notification", options: { bullet: true, breakLine: true } },
  { text: "Resolution workflow & tracking", options: { bullet: true, breakLine: true } },
  { text: "SLA dashboard with aggregated metrics", options: { bullet: true, breakLine: true } },
  { text: "NEW: AI-powered remediation suggestions", options: { bullet: true } },
], { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(13, false, colors.dark) });
slide20.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.primary }, line: { type: "none" } });
slide20.addText("Real-Time Detection", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide20.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.secondary }, line: { type: "none" } });
slide20.addText("Breach Tracking", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 21: VMS TIMESHEET WORKFLOW =============
const slide21 = pres.addSlide();
slide21.background = { color: colors.white };
slide21.addText("VMS Timesheet Workflow", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide21, 0.5, 1.05, 5);
slide21.addText([
  { text: "3-Tier Approval Workflow", options: { bold: true, breakLine: true } },
  { text: "Step 1: Supplier submits timesheet", options: { bullet: true, breakLine: true } },
  { text: "Step 2: MSP reviews & validates", options: { bullet: true, breakLine: true } },
  { text: "Step 3: Client approves for payment", options: { bullet: true, breakLine: true } },
  { text: "Compliance checks at each stage:", options: { bullet: true, breakLine: true } },
  { text: "Overtime limits enforcement", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Maximum hours per week validation", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Break time compliance", options: { bullet: true, indentLevel: 1, breakLine: true } },
  { text: "Automatic amount calculation", options: { bullet: true, breakLine: true } },
  { text: "Rejection & revision workflows", options: { bullet: true } },
], { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(13, false, colors.dark) });
slide21.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.secondary }, line: { type: "none" } });
slide21.addText("3-Tier Review", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide21.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.accent }, line: { type: "none" } });
slide21.addText("Compliance Checks", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 22: AUTO INVOICE GENERATION =============
const slide22 = pres.addSlide();
slide22.background = { color: colors.white };
slide22.addText("Auto Invoice Generation", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide22, 0.5, 1.05, 5);
const invoiceFeatures = [
  "Batch invoice generation from approved timesheets",
  "Automatic line item detail population",
  "Invoice preview before finalization",
  "Supplier remittance statements",
  "QuickBooks integration ready",
  "Multi-currency invoice support",
  "Custom invoice numbering schemes",
  "Tax & deduction calculations",
  "PDF generation & distribution",
  "NEW: Invoice reconciliation matching",
];
slide22.addText(invoiceFeatures.map((feat, idx) => ({ text: feat, options: { bullet: true, breakLine: idx < invoiceFeatures.length - 1 } })), { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(15, false, colors.dark) });
slide22.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.dark }, line: { type: "none" } });
slide22.addText("Automated", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide22.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.primary }, line: { type: "none" } });
slide22.addText("QuickBooks Ready", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 23: AI AGENT CATEGORIES =============
const slide23 = pres.addSlide();
slide23.background = { color: colors.white };
slide23.addText("AI Agent Categories (42 Total)", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide23, 0.5, 1.05, 5);

const agentCategories = [
  { name: "Recruitment Agents", count: "8" },
  { name: "Pipeline Automation", count: "7" },
  { name: "Rate & Finance", count: "6" },
  { name: "Compliance & Risk", count: "5" },
  { name: "Performance Analytics", count: "8" },
  { name: "Communication", count: "5" },
  { name: "Forecasting", count: "3" },
];

let cardY = 1.3;
agentCategories.forEach((cat) => {
  slide23.addShape(pres.shapes.RECTANGLE, {
    x: 0.8,
    y: cardY,
    w: 3.5,
    h: 0.6,
    fill: { color: colors.light },
    line: { color: colors.accent, width: 1.5 },
  });

  slide23.addText(cat.name, {
    x: 0.9,
    y: cardY + 0.08,
    w: 2.6,
    h: 0.45,
    ...makeTextOptions(14, true, colors.dark),
    valign: "middle",
  });

  slide23.addShape(pres.shapes.RECTANGLE, {
    x: 3.5,
    y: cardY,
    w: 0.8,
    h: 0.6,
    fill: { color: colors.accent },
    line: { type: "none" },
  });

  slide23.addText(cat.count, {
    x: 3.5,
    y: cardY + 0.08,
    w: 0.8,
    h: 0.45,
    ...makeHeadingOptions(18, colors.white),
    align: "center",
    valign: "middle",
  });

  cardY += 0.7;
});

// Right side stats
slide23.addShape(pres.shapes.RECTANGLE, {
  x: 5,
  y: 1.3,
  w: 4.5,
  h: 4.8,
  fill: { color: colors.light },
  line: { color: colors.primary, width: 2 },
});

slide23.addText("Agent Highlights", {
  x: 5.2,
  y: 1.5,
  w: 4.1,
  h: 0.5,
  ...makeHeadingOptions(22, colors.dark),
});

slide23.addText([
  { text: "Deep Learning NLP Models", options: { bullet: true, breakLine: true } },
  { text: "Real-time Decision Making", options: { bullet: true, breakLine: true } },
  { text: "Self-Learning Algorithms", options: { bullet: true, breakLine: true } },
  { text: "Explainable AI Output", options: { bullet: true, breakLine: true } },
  { text: "Configurable Behavior", options: { bullet: true, breakLine: true } },
  { text: "Audit Trail Logging", options: { bullet: true, breakLine: true } },
  { text: "A/B Testing Ready", options: { bullet: true } },
], { x: 5.2, y: 2.2, w: 4.1, h: 3, ...makeTextOptions(13, false, colors.dark) });

// ============= SLIDE 24: FEATURED SMART AGENTS =============
const slide24 = pres.addSlide();
slide24.background = { color: colors.white };
slide24.addText("Featured Smart Agents", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide24, 0.5, 1.05, 5);

const agents = [
  { name: "RateValidationAgent", desc: "Rate compliance scoring with market analysis" },
  { name: "ComplianceVerificationAgent", desc: "Risk assessment and requirement tracking" },
  { name: "WorkforceForecastingAgent", desc: "Demand prediction and capacity planning" },
  { name: "SupplierPerformancePredictionAgent", desc: "Fill probability and success forecasting" },
  { name: "AutoInterviewSchedulingAgent", desc: "Smart scheduling with participant optimization" },
];

let agentY = 1.2;
agents.forEach((agent, idx) => {
  slide24.addShape(pres.shapes.RECTANGLE, {
    x: 0.8,
    y: agentY,
    w: 8.5,
    h: 0.75,
    fill: { color: colors.light },
    line: { color: colors.accent, width: 1.5 },
  });

  slide24.addText(agent.name, {
    x: 0.95,
    y: agentY + 0.05,
    w: 3.5,
    h: 0.35,
    ...makeTextOptions(13, true, colors.primary),
  });

  slide24.addText(agent.desc, {
    x: 0.95,
    y: agentY + 0.4,
    w: 8.2,
    h: 0.3,
    ...makeTextOptions(12, false, colors.dark),
  });

  agentY += 0.85;
});

// ============= SLIDE 25: COMMUNICATION FEATURES =============
const slide25 = pres.addSlide();
slide25.background = { color: colors.white };
slide25.addText("Communication Features", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide25, 0.5, 1.05, 5);
const commFeatures = [
  "Slack integration & notifications",
  "Microsoft Teams integration",
  "Email notification system",
  "SMS alerts for urgent messages",
  "In-app messaging & chat",
  "Conversational AI interface",
  "Automated workflow notifications",
  "Custom notification templates",
  "Message scheduling & drip campaigns",
  "NEW: AI sentiment analysis",
];
slide25.addText(commFeatures.map((feat, idx) => ({ text: feat, options: { bullet: true, breakLine: idx < commFeatures.length - 1 } })), { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(15, false, colors.dark) });
slide25.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.primary }, line: { type: "none" } });
slide25.addText("Multi-Channel", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide25.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.secondary }, line: { type: "none" } });
slide25.addText("Smart Notifications", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 26: SOURCING & MARKETING =============
const slide26 = pres.addSlide();
slide26.background = { color: colors.white };
slide26.addText("Sourcing & Marketing", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide26, 0.5, 1.05, 5);
const sourcingFeatures = [
  "Resume harvesting from LinkedIn",
  "Job board integration",
  "Digital marketing campaigns",
  "Referral network management",
  "Candidate rediscovery engine",
  "Job post intelligence & optimization",
  "Skill-based candidate search",
  "Talent pool building & nurturing",
  "Campaign ROI analytics",
  "NEW: Predictive sourcing models",
];
slide26.addText(sourcingFeatures.map((feat, idx) => ({ text: feat, options: { bullet: true, breakLine: idx < sourcingFeatures.length - 1 } })), { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(15, false, colors.dark) });
slide26.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.accent }, line: { type: "none" } });
slide26.addText("Multi-Source", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide26.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.dark }, line: { type: "none" } });
slide26.addText("Data-Driven", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 27: REPORTS & ANALYTICS =============
const slide27 = pres.addSlide();
slide27.background = { color: colors.white };
slide27.addText("Reports & Analytics", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide27, 0.5, 1.05, 5);
slide27.addText([
  { text: "Report Types Available", options: { bold: true, breakLine: true } },
  { text: "Recruitment funnel analysis", options: { bullet: true, breakLine: true } },
  { text: "Financial reports (revenue, margins, costs)", options: { bullet: true, breakLine: true } },
  { text: "Supplier performance scorecards", options: { bullet: true, breakLine: true } },
  { text: "Compliance requirement reports", options: { bullet: true, breakLine: true } },
  { text: "SLA performance dashboards", options: { bullet: true, breakLine: true } },
  { text: "Workforce analytics & trends", options: { bullet: true, breakLine: true } },
  { text: "Export formats: PDF, CSV, Excel", options: { bullet: true, breakLine: true } },
  { text: "Scheduled report delivery", options: { bullet: true, breakLine: true } },
  { text: "NEW: Predictive analytics & forecasting", options: { bullet: true } },
], { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(13.5, false, colors.dark) });
slide27.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.secondary }, line: { type: "none" } });
slide27.addText("Comprehensive", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide27.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.primary }, line: { type: "none" } });
slide27.addText("Exportable", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 28: ADMINISTRATION =============
const slide28 = pres.addSlide();
slide28.background = { color: colors.white };
slide28.addText("Administration", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide28, 0.5, 1.05, 5);
const adminFeatures = [
  "User management & provisioning",
  "Security & RBAC configuration",
  "Audit logging & compliance",
  "API key management",
  "Webhook configuration",
  "System settings & preferences",
  "CI/CD pipeline integration",
  "Alert & notification rules",
  "Billing & subscription management",
  "NEW: SSO/SAML integration",
];
slide28.addText(adminFeatures.map((feat, idx) => ({ text: feat, options: { bullet: true, breakLine: idx < adminFeatures.length - 1 } })), { x: 0.8, y: 1.2, w: 5.5, h: 4, ...makeTextOptions(15, false, colors.dark) });
slide28.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.2, w: 3, h: 1.8, fill: { color: colors.dark }, line: { type: "none" } });
slide28.addText("Full Control", { x: 6.5, y: 1.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });
slide28.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 3.2, w: 3, h: 1.8, fill: { color: colors.accent }, line: { type: "none" } });
slide28.addText("Enterprise Grade", { x: 6.5, y: 3.4, w: 3, h: 1.4, ...makeTextOptions(16, true, colors.white), align: "center", valign: "middle" });

// ============= SLIDE 29: FEATURE COMPARISON MATRIX =============
const slide29 = pres.addSlide();
slide29.background = { color: colors.white };
slide29.addText("Feature Comparison Matrix", { x: 0.5, y: 0.4, w: 9, h: 0.6, ...makeHeadingOptions(40, colors.dark) });
addAccentBar(slide29, 0.5, 1.05, 5);

const comparisonData = [
  [
    { text: "Feature", options: { bold: true, color: colors.white, fill: { color: colors.dark } } },
    { text: "HotGigs", options: { bold: true, color: colors.white, fill: { color: colors.accent } } },
    { text: "Beeline", options: { bold: true, color: colors.white, fill: { color: colors.dark } } },
    { text: "SAP Fieldglass", options: { bold: true, color: colors.white, fill: { color: colors.dark } } },
  ],
  ["AI Resume Parsing", { text: "✓", options: { bold: true, color: colors.accent } }, "✓", "✓"],
  ["VMS Management", { text: "✓", options: { bold: true, color: colors.accent } }, "✓", "✓"],
  ["Rate Card Automation", { text: "✓", options: { bold: true, color: colors.accent } }, "✓", "✓"],
  ["Compliance Scoring", { text: "✓", options: { bold: true, color: colors.accent } }, "-", "✓"],
  ["42 AI Agents", { text: "✓", options: { bold: true, color: colors.accent } }, "-", "-"],
  ["Conversational AI", { text: "✓", options: { bold: true, color: colors.accent } }, "-", "-"],
  ["Real-time Analytics", { text: "✓", options: { bold: true, color: colors.accent } }, "✓", "✓"],
  ["Multi-Org Tenancy", { text: "✓", options: { bold: true, color: colors.accent } }, "✓", "✓"],
];

slide29.addTable(comparisonData, {
  x: 0.8,
  y: 1.2,
  w: 8.5,
  colW: [2.5, 1.8, 1.8, 1.8],
  border: { pt: 1, color: colors.lightGray },
  align: "center",
  valign: "middle",
  fontSize: 12,
});

// ============= SLIDE 30: ROADMAP =============
const slide30 = pres.addSlide();
slide30.background = { color: colors.light };

slide30.addText("What's Next — 2026 Roadmap", {
  x: 0.5,
  y: 0.4,
  w: 9,
  h: 0.6,
  ...makeHeadingOptions(40, colors.dark),
});

addAccentBar(slide30, 0.5, 1.05, 5);

const roadmap = [
  { quarter: "Q2 2026", items: ["Advanced ML Models", "Deep Learning Skill Matching", "Predictive Analytics"] },
  { quarter: "Q3 2026", items: ["Real-Time Collaboration", "Live Co-Browsing", "Synchronized Editing"] },
  { quarter: "Q4 2026", items: ["Native Mobile App", "iOS & Android", "Offline Capabilities"] },
  { quarter: "2027+", items: ["Autonomous Hiring", "End-to-End Automation", "Agent Marketplace"] },
];

let roadmapY = 1.2;
roadmap.forEach((phase) => {
  slide30.addShape(pres.shapes.RECTANGLE, {
    x: 0.8,
    y: roadmapY,
    w: 8.5,
    h: 0.9,
    fill: { color: colors.secondary },
    line: { type: "none" },
  });

  slide30.addText(phase.quarter, {
    x: 1,
    y: roadmapY + 0.15,
    w: 2,
    h: 0.6,
    ...makeHeadingOptions(16, colors.white),
    valign: "middle",
  });

  const itemsText = phase.items.join(" • ");
  slide30.addText(itemsText, {
    x: 3.2,
    y: roadmapY + 0.15,
    w: 5.9,
    h: 0.6,
    ...makeTextOptions(13, false, colors.white),
    valign: "middle",
  });

  roadmapY += 1;
});

pres.writeFile({ fileName: "/sessions/awesome-youthful-maxwell/mnt/outputs/HotGigs_Feature_Guide.pptx" });
console.log("✓ Presentation created: HotGigs_Feature_Guide.pptx");
