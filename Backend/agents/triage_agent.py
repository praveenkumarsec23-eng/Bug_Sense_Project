# =========================================================
# BUGSENSE - TRIAGE AGENT
# =========================================================
# First agent in the BugSense multi-agent pipeline.
#
# Responsibilities:
# - Classify bug type
# - Estimate severity
# - Assign priority
# - Provide a short triage reason
#
# This version uses deterministic rule-based analysis so
# BugSense can work without any paid AI API.
# =========================================================


class TriageAgent:

    def __init__(self):
        self.name = "Triage Agent"

    def analyze(
        self,
        title="",
        description="",
        error_message="",
        stack_trace="",
        code="",
        language=""
    ):
        title = title or ""
        description = description or ""
        error_message = error_message or ""
        stack_trace = stack_trace or ""
        code = code or ""
        language = language or ""

        combined_text = " ".join([
            title,
            description,
            error_message,
            stack_trace,
            code
        ]).lower()

        # =================================================
        # BUG TYPE CLASSIFICATION
        # =================================================

        bug_type = self._detect_bug_type(
            combined_text
        )

        # =================================================
        # SEVERITY CLASSIFICATION
        # =================================================

        severity = self._detect_severity(
            combined_text,
            bug_type
        )

        # =================================================
        # PRIORITY
        # =================================================

        priority = self._get_priority(
            severity
        )

        # =================================================
        # TRIAGE REASON
        # =================================================

        reason = self._build_reason(
            severity,
            bug_type
        )

        return {
            "agent": self.name,
            "severity": severity,
            "priority": priority,
            "bug_type": bug_type,
            "reason": reason,
            "language": language
        }

    # =====================================================
    # BUG TYPE DETECTION
    # =====================================================

    def _detect_bug_type(
        self,
        text
    ):

        security_keywords = [
            "sql injection",
            "xss",
            "cross site scripting",
            "authentication bypass",
            "authorization bypass",
            "unauthorized access",
            "privilege escalation",
            "security breach",
            "vulnerability",
            "csrf"
        ]

        database_keywords = [
            "sql",
            "database",
            "deadlock",
            "duplicate key",
            "foreign key",
            "constraint failed",
            "database locked",
            "integrityerror"
        ]

        memory_keywords = [
            "outofmemory",
            "out of memory",
            "memoryerror",
            "memory leak",
            "heap space",
            "segmentation fault",
            "segfault"
        ]

        network_keywords = [
            "connection timeout",
            "network timeout",
            "connection reset",
            "connection refused",
            "dns failure",
            "dns error",
            "socket error",
            "network error"
        ]

        syntax_keywords = [
            "syntaxerror",
            "syntax error",
            "unexpected token",
            "indentationerror",
            "indentation error",
            "compile error",
            "compilation error",
            "compiler error"
        ]

        performance_keywords = [
            "slow response",
            "performance issue",
            "high cpu",
            "high memory usage",
            "latency",
            "takes too long",
            "performance degradation"
        ]

        runtime_keywords = [
            "nullpointerexception",
            "null pointer",
            "indexerror",
            "indexoutofbounds",
            "indexoutofboundsexception",
            "keyerror",
            "typeerror",
            "valueerror",
            "zerodivisionerror",
            "runtimeerror",
            "runtimeexception",
            "referenceerror",
            "rangeerror",
            "unhandled exception"
        ]

        if self._contains_any(
            text,
            security_keywords
        ):
            return "Security Issue"

        if self._contains_any(
            text,
            database_keywords
        ):
            return "Database Error"

        if self._contains_any(
            text,
            memory_keywords
        ):
            return "Memory Error"

        if self._contains_any(
            text,
            network_keywords
        ):
            return "Network Error"

        if self._contains_any(
            text,
            syntax_keywords
        ):
            return "Syntax Error"

        if self._contains_any(
            text,
            performance_keywords
        ):
            return "Performance Issue"

        if self._contains_any(
            text,
            runtime_keywords
        ):
            return "Runtime Error"

        return "Application Error"

    # =====================================================
    # SEVERITY DETECTION
    # =====================================================

    def _detect_severity(
        self,
        text,
        bug_type
    ):

        # -------------------------------------------------
        # CRITICAL
        # -------------------------------------------------
        # Reserved for strong evidence of severe business,
        # security, availability, data, or system impact.
        # -------------------------------------------------

        critical_keywords = [
            "production down",
            "production outage",
            "complete outage",
            "system unavailable",
            "service unavailable for all users",
            "all users affected",
            "data loss",
            "permanent data loss",
            "data corruption",
            "security breach",
            "authentication bypass",
            "authorization bypass",
            "privilege escalation",
            "unauthorized admin access",
            "remote code execution",
            "ransomware",
            "segmentation fault",
            "outofmemory",
            "out of memory",
            "heap exhausted"
        ]

        # -------------------------------------------------
        # HIGH
        # -------------------------------------------------

        high_keywords = [
            "application crash",
            "application crashes",
            "server crash",
            "server crashes",
            "repeated crash",
            "repeatedly crashes",
            "deadlock",
            "database unavailable",
            "cannot login",
            "unable to login",
            "connection refused",
            "major functionality unavailable",
            "core functionality unavailable"
        ]

        # -------------------------------------------------
        # LOW
        # -------------------------------------------------

        low_keywords = [
            "typo",
            "alignment issue",
            "color issue",
            "spacing issue",
            "cosmetic",
            "minor ui",
            "wrong label",
            "label issue",
            "font size",
            "visual issue"
        ]

        # -------------------------------------------------
        # SECURITY
        # -------------------------------------------------

        if bug_type == "Security Issue":
            return "Critical"

        # -------------------------------------------------
        # CRITICAL SIGNAL
        # -------------------------------------------------

        if self._contains_any(
            text,
            critical_keywords
        ):
            return "Critical"

        # -------------------------------------------------
        # HIGH SIGNAL
        # -------------------------------------------------

        if self._contains_any(
            text,
            high_keywords
        ):
            return "High"

        # -------------------------------------------------
        # MEMORY FAILURES
        # -------------------------------------------------

        if bug_type == "Memory Error":
            return "High"

        # -------------------------------------------------
        # LOW / COSMETIC
        # -------------------------------------------------

        if self._contains_any(
            text,
            low_keywords
        ):
            return "Low"

        # -------------------------------------------------
        # NORMAL RUNTIME ERRORS
        # -------------------------------------------------

        normal_runtime_errors = [
            "keyerror",
            "typeerror",
            "valueerror",
            "indexerror",
            "indexoutofbounds",
            "indexoutofboundsexception",
            "nullpointerexception",
            "null pointer",
            "zerodivisionerror",
            "referenceerror",
            "rangeerror",
            "runtimeerror",
            "runtimeexception"
        ]

        if (
            bug_type == "Runtime Error"
            and self._contains_any(
                text,
                normal_runtime_errors
            )
        ):
            return "Medium"

        # -------------------------------------------------
        # SYNTAX ERRORS
        # -------------------------------------------------

        if bug_type == "Syntax Error":
            return "Medium"

        # -------------------------------------------------
        # PERFORMANCE ISSUES
        # -------------------------------------------------

        if bug_type == "Performance Issue":
            return "Medium"

        # -------------------------------------------------
        # NETWORK ERRORS
        # -------------------------------------------------

        if bug_type == "Network Error":
            return "Medium"

        # -------------------------------------------------
        # DATABASE ERRORS
        # -------------------------------------------------

        if bug_type == "Database Error":
            return "Medium"

        # -------------------------------------------------
        # DEFAULT
        # -------------------------------------------------

        return "Medium"

    # =====================================================
    # PRIORITY MAPPING
    # =====================================================

    def _get_priority(
        self,
        severity
    ):

        priority_map = {
            "Critical": "P1",
            "High": "P2",
            "Medium": "P3",
            "Low": "P4"
        }

        return priority_map.get(
            severity,
            "P3"
        )

    # =====================================================
    # TRIAGE REASON
    # =====================================================

    def _build_reason(
        self,
        severity,
        bug_type
    ):

        if severity == "Critical":
            return (
                f"The issue is classified as a "
                f"{bug_type} with indicators of severe "
                f"security, data, availability, or "
                f"system-level impact."
            )

        if severity == "High":
            return (
                f"The issue is classified as a "
                f"{bug_type} and may significantly "
                f"disrupt important application "
                f"functionality."
            )

        if severity == "Medium":
            return (
                f"The issue is classified as a "
                f"{bug_type} and affects normal "
                f"application behavior, but no clear "
                f"critical system-wide impact was "
                f"detected."
            )

        return (
            f"The issue is classified as a "
            f"{bug_type} with limited impact on "
            f"core application functionality."
        )

    # =====================================================
    # KEYWORD HELPER
    # =====================================================

    def _contains_any(
        self,
        text,
        keywords
    ):

        return any(
            keyword in text
            for keyword in keywords
        )


# =========================================================
# SIMPLE FUNCTION INTERFACE
# =========================================================

def run_triage_agent(
    title="",
    description="",
    error_message="",
    stack_trace="",
    code="",
    language=""
):

    agent = TriageAgent()

    return agent.analyze(
        title=title,
        description=description,
        error_message=error_message,
        stack_trace=stack_trace,
        code=code,
        language=language
    )