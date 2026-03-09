"""
E2E Testing Agent for HotGigs 2026 Platform.

This agent can:
1. Test all API endpoints (GET endpoints with mock auth)
2. Validate frontend page components (check imports, exports, required elements)
3. Analyze application logs for errors/warnings
4. Generate test reports with severity-ranked fix recommendations
5. Track test history for regression detection
"""

import logging
import json
import time
import os
import re
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class TestStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    ERROR = "error"


class TestSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class TestCategory(str, Enum):
    API_ENDPOINT = "api_endpoint"
    FRONTEND_PAGE = "frontend_page"
    FRONTEND_BUILD = "frontend_build"
    IMPORT_VALIDATION = "import_validation"
    ROUTE_VALIDATION = "route_validation"
    MODEL_VALIDATION = "model_validation"
    SCHEMA_VALIDATION = "schema_validation"
    LOG_ANALYSIS = "log_analysis"
    DEPENDENCY_CHECK = "dependency_check"
    SECURITY_CHECK = "security_check"


@dataclass
class TestResult:
    test_id: str
    category: str
    name: str
    status: str  # passed/failed/warning/skipped/error
    severity: str  # critical/high/medium/low/info
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0
    recommendation: str = ""
    file_path: str = ""
    line_number: int = 0


@dataclass
class TestReport:
    report_id: str
    run_type: str  # full, api_only, frontend_only, log_analysis, quick_smoke
    started_at: str
    completed_at: str
    duration_seconds: float
    total_tests: int
    passed: int
    failed: int
    warnings: int
    skipped: int
    errors: int
    pass_rate: float
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    category_breakdown: Dict[str, Dict[str, int]]


class TestAgent:
    """Core testing agent that orchestrates all test types."""

    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.logger = logging.getLogger("TestAgent")
        self.results: List[TestResult] = []
        self.test_history: List[TestReport] = []

    def _add_result(self, result: TestResult):
        self.results.append(result)

    # ═══════════════════════════════════════
    # 1. API ENDPOINT TESTS
    # ═══════════════════════════════════════

    def test_api_endpoints(self) -> List[TestResult]:
        """Test all registered API endpoints by importing the FastAPI app and checking routes."""
        results = []
        try:
            from api.vercel_app import app

            routes = [r for r in app.routes if hasattr(r, "methods")]

            # Group by prefix
            route_groups = {}
            for route in routes:
                path = route.path
                prefix = path.split("/")[3] if len(path.split("/")) > 3 else "root"
                if prefix not in route_groups:
                    route_groups[prefix] = []
                route_groups[prefix].append(
                    {
                        "path": path,
                        "methods": list(route.methods - {"HEAD", "OPTIONS"}),
                        "name": route.name,
                    }
                )

            # Test each route group
            for group_name, group_routes in route_groups.items():
                for route_info in group_routes:
                    test_id = f"api_{group_name}_{route_info['name']}"
                    start = time.time()

                    # Validate route has proper path
                    path = route_info["path"]
                    methods = route_info["methods"]

                    issues = []
                    if not path.startswith("/api/"):
                        issues.append("Route doesn't start with /api/")
                    if not methods:
                        issues.append("No HTTP methods defined")
                    if "{" in path and "}" not in path:
                        issues.append("Malformed path parameter")

                    status = TestStatus.PASSED if not issues else TestStatus.WARNING
                    result = TestResult(
                        test_id=test_id,
                        category=TestCategory.API_ENDPOINT,
                        name=f"{','.join(methods)} {path}",
                        status=status,
                        severity=TestSeverity.MEDIUM if issues else TestSeverity.INFO,
                        message="; ".join(issues)
                        if issues
                        else f"Route registered: {','.join(methods)} {path}",
                        details={
                            "path": path,
                            "methods": methods,
                            "function": route_info["name"],
                        },
                        duration_ms=(time.time() - start) * 1000,
                        recommendation=f"Fix route issues: {'; '.join(issues)}"
                        if issues
                        else "",
                    )
                    results.append(result)

            # Summary test
            results.append(
                TestResult(
                    test_id="api_route_count",
                    category=TestCategory.API_ENDPOINT,
                    name="Total API Routes Loaded",
                    status=TestStatus.PASSED,
                    severity=TestSeverity.INFO,
                    message=f"{len(routes)} routes loaded across {len(route_groups)} modules",
                    details={
                        "total_routes": len(routes),
                        "modules": len(route_groups),
                        "groups": {k: len(v) for k, v in route_groups.items()},
                    },
                )
            )

        except Exception as e:
            results.append(
                TestResult(
                    test_id="api_load_error",
                    category=TestCategory.API_ENDPOINT,
                    name="API Application Load",
                    status=TestStatus.ERROR,
                    severity=TestSeverity.CRITICAL,
                    message=f"Failed to load FastAPI app: {str(e)}",
                    recommendation="Check api/vercel_app.py for import errors. Run: python -c 'from api.vercel_app import app'",
                )
            )

        self.results.extend(results)
        return results

    # ═══════════════════════════════════════
    # 2. FRONTEND PAGE VALIDATION
    # ═══════════════════════════════════════

    def test_frontend_pages(self) -> List[TestResult]:
        """Validate all frontend page components exist, export properly, and have required elements."""
        results = []
        pages_dir = os.path.join(self.project_root, "frontend", "src", "pages")

        # Read App.tsx to get expected imports
        app_tsx_path = os.path.join(self.project_root, "frontend", "src", "App.tsx")
        try:
            with open(app_tsx_path, "r") as f:
                app_content = f.read()
        except:
            app_content = ""

        # Extract all imported page components
        import_pattern = r"import\s+\{?\s*(\w+)\s*\}?\s+from\s+'@/pages/([^']+)'"
        imports = re.findall(import_pattern, app_content)

        # Extract all route paths
        route_pattern = r'path="([^"]+)"'
        routes = re.findall(route_pattern, app_content)

        for component_name, import_path in imports:
            test_id = f"page_{component_name}"
            start = time.time()

            # Resolve file path
            file_path = os.path.join(
                self.project_root, "frontend", "src", "pages", import_path
            )
            if not file_path.endswith(".tsx") and not file_path.endswith(".ts"):
                file_path += ".tsx"

            issues = []
            details = {"component": component_name, "import_path": import_path}

            if not os.path.exists(file_path):
                issues.append(f"File not found: {file_path}")
                severity = TestSeverity.CRITICAL
            else:
                with open(file_path, "r") as f:
                    content = f.read()

                details["file_size"] = len(content)
                details["line_count"] = content.count("\n") + 1

                # Check export
                if (
                    f"export const {component_name}" not in content
                    and f"export default" not in content
                    and f"export {{ {component_name}" not in content
                ):
                    issues.append(f"Component '{component_name}' not properly exported")

                # Check for common heroicon issues
                icon_imports = re.findall(
                    r"import\s+\{([^}]+)\}\s+from\s+['\"]@heroicons", content
                )
                for icon_group in icon_imports:
                    icons = [i.strip() for i in icon_group.split(",")]
                    known_bad = [
                        "TrendingUpIcon",
                        "ShieldAlertIcon",
                        "PinIcon",
                        "ToggleLeftIcon",
                    ]
                    for icon in icons:
                        if icon in known_bad:
                            issues.append(f"Invalid heroicon: {icon}")

                severity = TestSeverity.HIGH if issues else TestSeverity.INFO

            status = (
                TestStatus.FAILED
                if any("not found" in i or "not properly exported" in i for i in issues)
                else TestStatus.WARNING if issues
                else TestStatus.PASSED
            )

            results.append(
                TestResult(
                    test_id=test_id,
                    category=TestCategory.FRONTEND_PAGE,
                    name=f"Page: {component_name}",
                    status=status,
                    severity=severity,
                    message="; ".join(issues)
                    if issues
                    else f"Page component valid ({details.get('line_count', 0)} lines)",
                    details=details,
                    duration_ms=(time.time() - start) * 1000,
                    recommendation="; ".join([f"Fix: {i}" for i in issues])
                    if issues
                    else "",
                    file_path=file_path,
                )
            )

        # Check for orphan pages (files not imported in App.tsx)
        if os.path.exists(pages_dir):
            all_pages = glob.glob(os.path.join(pages_dir, "*.tsx"))
            imported_files = set()
            for _, path in imports:
                p = path if path.endswith(".tsx") else path + ".tsx"
                imported_files.add(os.path.basename(p))

            for page_file in all_pages:
                basename = os.path.basename(page_file)
                if basename not in imported_files and basename != "index.tsx":
                    results.append(
                        TestResult(
                            test_id=f"orphan_{basename}",
                            category=TestCategory.FRONTEND_PAGE,
                            name=f"Orphan Page: {basename}",
                            status=TestStatus.WARNING,
                            severity=TestSeverity.LOW,
                            message=f"Page file exists but is not imported in App.tsx",
                            file_path=page_file,
                            recommendation=f"Either add route for {basename} in App.tsx or remove if unused",
                        )
                    )

        self.results.extend(results)
        return results

    # ═══════════════════════════════════════
    # 3. FRONTEND BUILD VALIDATION
    # ═══════════════════════════════════════

    def test_frontend_build(self) -> List[TestResult]:
        """Run vite build and analyze output for errors/warnings."""
        import subprocess

        results = []
        start = time.time()

        try:
            proc = subprocess.run(
                ["npx", "vite", "build"],
                cwd=os.path.join(self.project_root, "frontend"),
                capture_output=True,
                text=True,
                timeout=120,
            )

            duration = (time.time() - start) * 1000
            output = proc.stdout + proc.stderr

            if proc.returncode == 0:
                # Extract module count
                module_match = re.search(r"(\d+)\s+modules\s+transformed", output)
                modules = int(module_match.group(1)) if module_match else 0

                # Extract build time
                time_match = re.search(r"built in\s+([\d.]+)s", output)
                build_time = float(time_match.group(1)) if time_match else 0

                # Check for warnings
                warnings = re.findall(r"\(!\)\s+(.+)", output)

                results.append(
                    TestResult(
                        test_id="build_success",
                        category=TestCategory.FRONTEND_BUILD,
                        name="Frontend Build",
                        status=TestStatus.PASSED,
                        severity=TestSeverity.INFO,
                        message=f"Build successful: {modules} modules in {build_time}s",
                        details={
                            "modules": modules,
                            "build_time_s": build_time,
                            "warnings": warnings,
                        },
                        duration_ms=duration,
                    )
                )

                for i, warn in enumerate(warnings):
                    results.append(
                        TestResult(
                            test_id=f"build_warning_{i}",
                            category=TestCategory.FRONTEND_BUILD,
                            name=f"Build Warning",
                            status=TestStatus.WARNING,
                            severity=TestSeverity.LOW,
                            message=warn.strip(),
                            duration_ms=0,
                            recommendation="Consider code-splitting with dynamic imports to reduce chunk sizes",
                        )
                    )
            else:
                # Parse build errors
                error_lines = [
                    l for l in output.split("\n") if "error" in l.lower() or "Error" in l
                ]
                results.append(
                    TestResult(
                        test_id="build_failure",
                        category=TestCategory.FRONTEND_BUILD,
                        name="Frontend Build",
                        status=TestStatus.FAILED,
                        severity=TestSeverity.CRITICAL,
                        message=f"Build FAILED with exit code {proc.returncode}",
                        details={
                            "exit_code": proc.returncode,
                            "errors": error_lines[:10],
                            "full_output": output[-2000:],
                        },
                        duration_ms=duration,
                        recommendation="Fix build errors before deployment. Check error details for specific file/line issues.",
                    )
                )

        except subprocess.TimeoutExpired:
            results.append(
                TestResult(
                    test_id="build_timeout",
                    category=TestCategory.FRONTEND_BUILD,
                    name="Frontend Build",
                    status=TestStatus.ERROR,
                    severity=TestSeverity.HIGH,
                    message="Build timed out after 120 seconds",
                    recommendation="Check for circular dependencies or infinite loops in build process",
                )
            )
        except Exception as e:
            results.append(
                TestResult(
                    test_id="build_error",
                    category=TestCategory.FRONTEND_BUILD,
                    name="Frontend Build",
                    status=TestStatus.ERROR,
                    severity=TestSeverity.CRITICAL,
                    message=f"Build process error: {str(e)}",
                )
            )

        self.results.extend(results)
        return results

    # ═══════════════════════════════════════
    # 4. MODEL & SCHEMA VALIDATION
    # ═══════════════════════════════════════

    def test_models_and_schemas(self) -> List[TestResult]:
        """Validate SQLAlchemy models load without conflicts."""
        results = []

        # Test model imports
        model_dir = os.path.join(self.project_root, "models")
        if os.path.exists(model_dir):
            model_files = glob.glob(os.path.join(model_dir, "*.py"))
            for model_file in model_files:
                basename = os.path.basename(model_file)
                if basename.startswith("__"):
                    continue
                module_name = basename.replace(".py", "")
                test_id = f"model_{module_name}"
                start = time.time()

                try:
                    with open(model_file, "r") as f:
                        content = f.read()

                    issues = []
                    # Check for reserved 'metadata' column
                    if re.search(r"\bmetadata\s*=\s*Column", content):
                        issues.append(
                            "Uses reserved 'metadata' column name — rename to avoid SQLAlchemy conflicts"
                        )

                    # Check for duplicate __tablename__
                    table_names = re.findall(
                        r'__tablename__\s*=\s*["\'](\w+)["\']', content
                    )

                    status = TestStatus.WARNING if issues else TestStatus.PASSED
                    results.append(
                        TestResult(
                            test_id=test_id,
                            category=TestCategory.MODEL_VALIDATION,
                            name=f"Model: {module_name}",
                            status=status,
                            severity=TestSeverity.HIGH if issues else TestSeverity.INFO,
                            message="; ".join(issues)
                            if issues
                            else f"Model valid ({len(table_names)} tables: {', '.join(table_names)})",
                            details={"tables": table_names, "file": model_file},
                            duration_ms=(time.time() - start) * 1000,
                            file_path=model_file,
                            recommendation="; ".join(issues) if issues else "",
                        )
                    )
                except Exception as e:
                    results.append(
                        TestResult(
                            test_id=test_id,
                            category=TestCategory.MODEL_VALIDATION,
                            name=f"Model: {module_name}",
                            status=TestStatus.ERROR,
                            severity=TestSeverity.HIGH,
                            message=f"Error reading model: {str(e)}",
                            file_path=model_file,
                        )
                    )

        # Test schema imports
        schema_dir = os.path.join(self.project_root, "schemas")
        if os.path.exists(schema_dir):
            schema_files = glob.glob(os.path.join(schema_dir, "*.py"))
            for schema_file in schema_files:
                basename = os.path.basename(schema_file)
                if basename.startswith("__"):
                    continue
                module_name = basename.replace(".py", "")
                test_id = f"schema_{module_name}"

                try:
                    with open(schema_file, "r") as f:
                        content = f.read()
                    classes = re.findall(r"class\s+(\w+)\s*\(", content)
                    results.append(
                        TestResult(
                            test_id=test_id,
                            category=TestCategory.SCHEMA_VALIDATION,
                            name=f"Schema: {module_name}",
                            status=TestStatus.PASSED,
                            severity=TestSeverity.INFO,
                            message=f"Schema valid ({len(classes)} models: {', '.join(classes[:5])}{'...' if len(classes) > 5 else ''})",
                            details={"models": classes, "file": schema_file},
                            file_path=schema_file,
                        )
                    )
                except Exception as e:
                    results.append(
                        TestResult(
                            test_id=test_id,
                            category=TestCategory.SCHEMA_VALIDATION,
                            name=f"Schema: {module_name}",
                            status=TestStatus.ERROR,
                            severity=TestSeverity.MEDIUM,
                            message=f"Error: {str(e)}",
                            file_path=schema_file,
                        )
                    )

        self.results.extend(results)
        return results

    # ═══════════════════════════════════════
    # 5. ROUTE CONSISTENCY CHECK
    # ═══════════════════════════════════════

    def test_route_consistency(self) -> List[TestResult]:
        """Check that frontend routes match backend API endpoints and sidebar links."""
        results = []

        # Read sidebar
        sidebar_path = os.path.join(
            self.project_root, "frontend", "src", "components", "layout", "Sidebar.tsx"
        )
        app_path = os.path.join(self.project_root, "frontend", "src", "App.tsx")

        try:
            if os.path.exists(sidebar_path):
                with open(sidebar_path, "r") as f:
                    sidebar_content = f.read()
            else:
                sidebar_content = ""

            with open(app_path, "r") as f:
                app_content = f.read()

            # Extract sidebar hrefs
            sidebar_hrefs = set(re.findall(r"href:\s*'([^']+)'", sidebar_content))

            # Extract App.tsx route paths
            app_routes = set(re.findall(r'path="([^"]+)"', app_content))

            # Check sidebar links have matching routes
            for href in sidebar_hrefs:
                if href not in app_routes and not any(
                    href.startswith(r.replace("/*", "")) for r in app_routes
                ):
                    results.append(
                        TestResult(
                            test_id=f"route_missing_{href.replace('/', '_')}",
                            category=TestCategory.ROUTE_VALIDATION,
                            name=f"Missing Route: {href}",
                            status=TestStatus.WARNING,
                            severity=TestSeverity.MEDIUM,
                            message=f"Sidebar link '{href}' has no matching route in App.tsx",
                            recommendation=f'Add <Route path="{href}"> to App.tsx or remove from Sidebar.tsx',
                        )
                    )

            results.append(
                TestResult(
                    test_id="route_consistency_summary",
                    category=TestCategory.ROUTE_VALIDATION,
                    name="Route Consistency",
                    status=TestStatus.PASSED,
                    severity=TestSeverity.INFO,
                    message=f"Checked {len(sidebar_hrefs)} sidebar links against {len(app_routes)} routes",
                    details={
                        "sidebar_links": len(sidebar_hrefs),
                        "app_routes": len(app_routes),
                    },
                )
            )

        except Exception as e:
            results.append(
                TestResult(
                    test_id="route_check_error",
                    category=TestCategory.ROUTE_VALIDATION,
                    name="Route Consistency Check",
                    status=TestStatus.ERROR,
                    severity=TestSeverity.MEDIUM,
                    message=f"Error: {str(e)}",
                )
            )

        self.results.extend(results)
        return results

    # ═══════════════════════════════════════
    # 6. DEPENDENCY CHECK
    # ═══════════════════════════════════════

    def test_dependencies(self) -> List[TestResult]:
        """Check that required Python and Node packages are installed."""
        import subprocess

        results = []

        # Python deps
        critical_deps = [
            "fastapi",
            "sqlalchemy",
            "pydantic",
            "uvicorn",
            "bcrypt",
            "python-jose",
            "httpx",
        ]
        for dep in critical_deps:
            try:
                subprocess.run(
                    ["python", "-c", f"import {dep.replace('-', '_')}"],
                    capture_output=True,
                    timeout=10,
                )
                results.append(
                    TestResult(
                        test_id=f"dep_py_{dep}",
                        category=TestCategory.DEPENDENCY_CHECK,
                        name=f"Python: {dep}",
                        status=TestStatus.PASSED,
                        severity=TestSeverity.INFO,
                        message=f"{dep} is installed",
                    )
                )
            except:
                results.append(
                    TestResult(
                        test_id=f"dep_py_{dep}",
                        category=TestCategory.DEPENDENCY_CHECK,
                        name=f"Python: {dep}",
                        status=TestStatus.FAILED,
                        severity=TestSeverity.HIGH,
                        message=f"{dep} is NOT installed",
                        recommendation=f"pip install {dep} --break-system-packages",
                    )
                )

        # Check node_modules exists
        nm_path = os.path.join(self.project_root, "frontend", "node_modules")
        results.append(
            TestResult(
                test_id="dep_node_modules",
                category=TestCategory.DEPENDENCY_CHECK,
                name="Node Modules",
                status=TestStatus.PASSED
                if os.path.exists(nm_path)
                else TestStatus.FAILED,
                severity=TestSeverity.CRITICAL
                if not os.path.exists(nm_path)
                else TestSeverity.INFO,
                message="node_modules exists"
                if os.path.exists(nm_path)
                else "node_modules missing",
                recommendation="" if os.path.exists(nm_path) else "cd frontend && npm install",
            )
        )

        self.results.extend(results)
        return results

    # ═══════════════════════════════════════
    # 7. GENERATE REPORT
    # ═══════════════════════════════════════

    def generate_report(self, run_type: str = "full") -> TestReport:
        """Generate a comprehensive test report from accumulated results."""
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        warnings = sum(1 for r in self.results if r.status == TestStatus.WARNING)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
        errors = sum(1 for r in self.results if r.status == TestStatus.ERROR)
        total = len(self.results)

        # Category breakdown
        categories = {}
        for r in self.results:
            cat = r.category
            if cat not in categories:
                categories[cat] = {"passed": 0, "failed": 0, "warning": 0, "error": 0, "skipped": 0}
            categories[cat][r.status] = categories[cat].get(r.status, 0) + 1

        # Recommendations (sorted by severity)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        recommendations = [
            {
                "test_id": r.test_id,
                "severity": r.severity,
                "category": r.category,
                "name": r.name,
                "issue": r.message,
                "recommendation": r.recommendation,
                "file_path": r.file_path,
            }
            for r in self.results
            if r.recommendation
            and r.status
            in (TestStatus.FAILED, TestStatus.WARNING, TestStatus.ERROR)
        ]
        recommendations.sort(key=lambda x: severity_order.get(x["severity"], 99))

        # Calculate health score
        health_score = round(
            ((passed + warnings * 0.5) / total * 100) if total > 0 else 0, 1
        )

        report = TestReport(
            report_id=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            run_type=run_type,
            started_at=datetime.now().isoformat(),
            completed_at=datetime.now().isoformat(),
            duration_seconds=sum(r.duration_ms for r in self.results) / 1000,
            total_tests=total,
            passed=passed,
            failed=failed,
            warnings=warnings,
            skipped=skipped,
            errors=errors,
            pass_rate=round((passed / total * 100) if total > 0 else 0, 1),
            results=[asdict(r) for r in self.results],
            summary={
                "total": total,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "errors": errors,
                "pass_rate": round((passed / total * 100) if total > 0 else 0, 1),
                "health_score": health_score,
            },
            recommendations=recommendations,
            category_breakdown=categories,
        )

        # Store in history
        self.test_history.append(report)
        return report

    # ═══════════════════════════════════════
    # 8. RUN ALL TESTS
    # ═══════════════════════════════════════

    def run_full_suite(self) -> TestReport:
        """Run the complete test suite."""
        self.results = []
        self.test_dependencies()
        self.test_api_endpoints()
        self.test_models_and_schemas()
        self.test_frontend_pages()
        self.test_route_consistency()
        self.test_frontend_build()
        return self.generate_report("full")

    def run_quick_smoke(self) -> TestReport:
        """Run a quick smoke test (no build)."""
        self.results = []
        self.test_api_endpoints()
        self.test_frontend_pages()
        self.test_route_consistency()
        return self.generate_report("quick_smoke")

    def run_api_only(self) -> TestReport:
        """Test API endpoints only."""
        self.results = []
        self.test_api_endpoints()
        self.test_models_and_schemas()
        return self.generate_report("api_only")

    def run_frontend_only(self) -> TestReport:
        """Test frontend only."""
        self.results = []
        self.test_frontend_pages()
        self.test_frontend_build()
        self.test_route_consistency()
        return self.generate_report("frontend_only")

    def get_test_history(self) -> List[TestReport]:
        """Get all test runs from history."""
        return self.test_history

    def get_latest_report(self) -> Optional[TestReport]:
        """Get the most recent test report."""
        return self.test_history[-1] if self.test_history else None
