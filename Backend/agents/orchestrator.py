from agents.triage_agent import run_triage_agent
from agents.log_analysis_agent import run_log_analysis_agent
from agents.root_cause_agent import run_root_cause_agent
from agents.duplicate_agent import run_duplicate_agent
from agents.remediation_agent import run_remediation_agent
from services.rag_service import rag_service


class BugAnalysisOrchestrator:

    def analyze(
        self,
        title,
        language,
        description="",
        error_message="",
        stack_trace="",
        code="",
        analyze_root_cause=True,
        search_similar_bugs=True,
        detect_duplicates=True,
        generate_fix_recommendation=True,
        knowledge_entries=None
    ):
        if knowledge_entries is None:
            knowledge_entries = []

        # =================================================
        # AGENT 1 - TRIAGE AGENT
        # =================================================

        triage_result = run_triage_agent(
            title=title,
            description=description,
            error_message=error_message,
            stack_trace=stack_trace,
            code=code,
            language=language
        )

        # =================================================
        # AGENT 2 - LOG ANALYSIS AGENT
        # =================================================

        log_result = run_log_analysis_agent(
            error_message=error_message,
            stack_trace=stack_trace,
            code=code,
            language=language
        )

        # =================================================
        # AGENT 3 - ROOT CAUSE AGENT
        # =================================================

        root_cause_result = None

        if analyze_root_cause:
            root_cause_result = run_root_cause_agent(
                title=title,
                description=description,
                error_message=error_message,
                stack_trace=stack_trace,
                code=code,
                language=language,

                bug_type=triage_result["bug_type"],
                severity=triage_result["severity"],
                priority=triage_result["priority"],

                exception_type=log_result["exception"],
                failure_file=log_result["file"],
                failure_line=log_result["line"],
                failure_function=log_result["function"],
                failure_code=log_result["failure_code"]
            )

        # =================================================
        # RAG SEMANTIC RETRIEVAL
        # =================================================

        similar_bugs = []

        if search_similar_bugs or detect_duplicates:

            rag_query = rag_service.build_query(
                title=title,
                description=description,
                error_message=error_message,
                bug_type=triage_result["bug_type"],
                language=language,
                exception_type=(
                    log_result["exception"] or ""
                ),
                root_cause=(
                    root_cause_result["root_cause"]
                    if root_cause_result
                    else ""
                )
            )

            similar_bugs = rag_service.search(
                query=rag_query,
                knowledge_entries=knowledge_entries,
                top_k=3,
                minimum_score=0.25
            )

        # =================================================
        # AGENT 4 - DUPLICATE DETECTION AGENT
        # =================================================

        duplicate_result = None

        if detect_duplicates:
            duplicate_result = run_duplicate_agent(
                similar_bugs=similar_bugs,
                duplicate_threshold=0.70
            )

        # =================================================
        # AGENT 5 - REMEDIATION AGENT
        # =================================================

        remediation_result = None

        if generate_fix_recommendation:
            remediation_result = run_remediation_agent(
                language=language,
                code=code,

                exception_type=(
                    log_result["exception"] or ""
                ),

                failure_file=(
                    log_result["file"] or ""
                ),

                failure_line=log_result["line"],

                failure_function=(
                    log_result["function"] or ""
                ),

                failure_code=(
                    log_result["failure_code"] or ""
                ),

                root_cause=(
                    root_cause_result["root_cause"]
                    if root_cause_result
                    else ""
                ),

                similar_bugs=similar_bugs
            )

        # =================================================
        # COMBINED ORCHESTRATOR RESULT
        # =================================================

        return {
            "orchestrator": "Bug Analysis Orchestrator",

            "triage": triage_result,

            "log_analysis": log_result,

            "root_cause": root_cause_result,

            "rag": {
                "similar_bugs": similar_bugs,
                "matches_found": len(similar_bugs)
            },

            "duplicate_detection": duplicate_result,

            "remediation": remediation_result,

            "agents": {
                "triage": "completed",
                "log_analysis": "completed",

                "root_cause": (
                    "completed"
                    if root_cause_result
                    else "skipped"
                ),

                "duplicate_detection": (
                    "completed"
                    if duplicate_result
                    else "skipped"
                ),

                "remediation": (
                    "completed"
                    if remediation_result
                    else "skipped"
                )
            }
        }


bug_analysis_orchestrator = BugAnalysisOrchestrator()


def run_bug_analysis(
    title,
    language,
    description="",
    error_message="",
    stack_trace="",
    code="",
    analyze_root_cause=True,
    search_similar_bugs=True,
    detect_duplicates=True,
    generate_fix_recommendation=True,
    knowledge_entries=None
):
    return bug_analysis_orchestrator.analyze(
        title=title,
        language=language,
        description=description,
        error_message=error_message,
        stack_trace=stack_trace,
        code=code,
        analyze_root_cause=analyze_root_cause,
        search_similar_bugs=search_similar_bugs,
        detect_duplicates=detect_duplicates,
        generate_fix_recommendation=generate_fix_recommendation,
        knowledge_entries=knowledge_entries
    )