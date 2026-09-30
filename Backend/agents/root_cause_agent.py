# =========================================================
# BUGSENSE - ROOT CAUSE AGENT
# =========================================================
# Third agent in the BugSense multi-agent pipeline.
#
# Responsibilities:
# - Use triage + log-analysis evidence
# - Identify probable root cause
# - Generate an explanation
# - Produce an evidence-based confidence score
# =========================================================


class RootCauseAgent:

    def __init__(self):
        self.name = "Root Cause Agent"

    # =====================================================
    # MAIN ANALYSIS
    # =====================================================

    def analyze(
        self,
        title="",
        description="",
        error_message="",
        stack_trace="",
        code="",
        language="",
        bug_type="",
        severity="",
        priority="",
        exception_type=None,
        failure_file=None,
        failure_line=None,
        failure_function=None,
        failure_code=None
    ):
        title = title or ""
        description = description or ""
        error_message = error_message or ""
        stack_trace = stack_trace or ""
        code = code or ""
        language = language or ""
        bug_type = bug_type or ""
        severity = severity or ""
        priority = priority or ""

        combined_text = "\n".join([
            title,
            description,
            error_message,
            stack_trace,
            code,
            failure_code or ""
        ])

        root_cause, strength = self._detect_root_cause(
            text=combined_text,
            exception_type=exception_type,
            language=language,
            failure_code=failure_code
        )

        confidence = self._calculate_confidence(
            strength=strength,
            exception_type=exception_type,
            failure_file=failure_file,
            failure_line=failure_line,
            failure_function=failure_function,
            failure_code=failure_code
        )

        explanation = self._build_explanation(
            root_cause=root_cause,
            exception_type=exception_type,
            failure_file=failure_file,
            failure_line=failure_line,
            failure_function=failure_function,
            failure_code=failure_code,
            bug_type=bug_type
        )

        return {
            "agent": self.name,
            "root_cause": root_cause,
            "explanation": explanation,
            "confidence": confidence,
            "language": language,
            "bug_type": bug_type,
            "severity": severity,
            "priority": priority
        }

    # =====================================================
    # ROOT CAUSE DETECTION
    # =====================================================

    def _detect_root_cause(
        self,
        text,
        exception_type=None,
        language="",
        failure_code=None
    ):
        text_lower = (
            text or ""
        ).lower()

        exception_lower = (
            exception_type or ""
        ).lower()

        language_lower = (
            language or ""
        ).strip().lower()

        failure_lower = (
            failure_code or ""
        ).lower()

        # =================================================
        # PHP
        # =================================================

        if language_lower == "php":

            if (
                "call to a member function" in text_lower
                and "on null" in text_lower
            ):
                return (
                    "A PHP object reference is null when a "
                    "member method is being called. The object "
                    "must be initialized or validated before "
                    "the method is invoked.",
                    "strong"
                )

            if (
                "attempt to read property" in text_lower
                and "on null" in text_lower
            ):
                return (
                    "A PHP object reference is null when one "
                    "of its properties is being accessed. The "
                    "object should be initialized or checked "
                    "for null before the property is read.",
                    "strong"
                )

            if (
                "attempt to assign property" in text_lower
                and "on null" in text_lower
            ):
                return (
                    "A PHP object reference is null while a "
                    "property assignment is being attempted. "
                    "The object must exist before assigning "
                    "values to its properties.",
                    "strong"
                )

            if (
                "->" in failure_lower
                and (
                    "null" in text_lower
                    or "null" in failure_lower
                )
            ):
                return (
                    "A PHP object is being dereferenced with "
                    "the -> operator while its value may be "
                    "null. Validate or initialize the object "
                    "before accessing its member.",
                    "strong"
                )

            if (
                "undefined variable" in text_lower
                or "undefined array key" in text_lower
            ):
                return (
                    "The PHP code is using a variable or array "
                    "key that has not been defined for the "
                    "current execution path. Validate that the "
                    "value exists before accessing it.",
                    "strong"
                )

        # =================================================
        # C#
        # =================================================

        if (
            "nullreferenceexception" in exception_lower
            or (
                "object reference not set to an instance"
                in text_lower
            )
        ):
            return (
                "A C# object reference is null when one of its "
                "properties or methods is being accessed. The "
                "object should be initialized or validated "
                "before it is dereferenced.",
                "strong"
            )

        # =================================================
        # JAVA NULL POINTER
        # =================================================

        if (
            "nullpointerexception" in exception_lower
            or "nullpointerexception" in text_lower
        ):
            return (
                "A Java object reference is null when a method "
                "or property is being accessed. The object "
                "should be initialized or checked for null "
                "before it is dereferenced.",
                "strong"
            )

        # =================================================
        # PYTHON KEY ERROR
        # =================================================

        if (
            "keyerror" in exception_lower
            or "keyerror" in text_lower
        ):
            return (
                "The code attempts to access a dictionary key "
                "that is not present in the current dictionary. "
                "The key should be validated before direct "
                "access or retrieved with a safe lookup.",
                "strong"
            )

        # =================================================
        # PYTHON INDEX ERROR
        # =================================================

        if (
            "indexerror" in exception_lower
            or "indexerror" in text_lower
        ):
            return (
                "The code attempts to access a sequence index "
                "that is outside the valid range. The index "
                "should be validated against the sequence "
                "length before access.",
                "strong"
            )

        # =================================================
        # PYTHON ZERO DIVISION
        # =================================================

        if (
            "zerodivisionerror" in exception_lower
            or "zerodivisionerror" in text_lower
            or "division by zero" in text_lower
        ):
            zero_division_details = (
                self._analyze_python_zero_division(
                    text=text,
                    failure_code=failure_code
                )
            )

            if zero_division_details:
                return (
                    zero_division_details,
                    "strong"
                )

            return (
                "The Python code performs a division operation "
                "with a zero denominator. The divisor must be "
                "validated before the division is executed.",
                "strong"
            )

        # =================================================
        # PYTHON ATTRIBUTE ERROR
        # =================================================

        if (
            "attributeerror" in exception_lower
            or "attributeerror" in text_lower
        ):
            return (
                "The code attempts to access an attribute or "
                "method that is not available on the current "
                "object. The object type and attribute "
                "availability should be validated.",
                "strong"
            )

        # =================================================
        # PYTHON TYPE ERROR
        # =================================================

        if (
            "typeerror" in exception_lower
            and language_lower == "python"
        ):
            return (
                "The Python operation is being applied to an "
                "object of an incompatible type. Validate or "
                "convert the value before performing the "
                "operation.",
                "strong"
            )

        # =================================================
        # JAVASCRIPT / TYPESCRIPT REFERENCE ERROR
        # =================================================

        if (
            "referenceerror" in exception_lower
            or "referenceerror" in text_lower
        ):
            return (
                "The JavaScript or TypeScript code references "
                "a variable or identifier that is not defined "
                "in the current scope. Define the identifier "
                "or correct the reference before using it.",
                "strong"
            )

        # =================================================
        # JAVASCRIPT / TYPESCRIPT NULL / UNDEFINED
        # =================================================

        if language_lower in [
            "javascript",
            "js",
            "typescript",
            "ts"
        ]:
            if (
                "cannot read properties of undefined"
                in text_lower
                or
                "cannot read property" in text_lower
                and "undefined" in text_lower
            ):
                return (
                    "A JavaScript or TypeScript value is "
                    "undefined when one of its properties or "
                    "methods is being accessed. Validate or "
                    "initialize the value before dereferencing "
                    "it.",
                    "strong"
                )

            if (
                "cannot read properties of null"
                in text_lower
                or
                "cannot read property" in text_lower
                and "null" in text_lower
            ):
                return (
                    "A JavaScript or TypeScript value is null "
                    "when one of its properties or methods is "
                    "being accessed. Validate the value before "
                    "dereferencing it.",
                    "strong"
                )

            if (
                "typeerror" in exception_lower
                and (
                    "undefined" in text_lower
                    or "null" in text_lower
                )
            ):
                return (
                    "A JavaScript or TypeScript operation is "
                    "being performed on a null or undefined "
                    "value. The value should be validated "
                    "before the operation is executed.",
                    "strong"
                )

        # =================================================
        # C / C++ SEGMENTATION FAULT
        # =================================================

        if language_lower in [
            "c",
            "c++",
            "cpp"
        ]:
            if (
                "segmentation fault" in text_lower
                or "sigsegv" in text_lower
            ):
                return (
                    "The program is accessing invalid memory, "
                    "commonly through a null, dangling, or "
                    "otherwise invalid pointer. Validate the "
                    "pointer before dereferencing it.",
                    "strong"
                )

            if (
                "nullptr" in text_lower
                or "null pointer" in text_lower
            ):
                return (
                    "A pointer is null when the program "
                    "attempts to dereference it. Validate the "
                    "pointer before accessing the referenced "
                    "memory.",
                    "strong"
                )

        # =================================================
        # VALUE ERROR
        # =================================================

        if (
            "valueerror" in exception_lower
            or "valueerror" in text_lower
        ):
            return (
                "The code received a value that is invalid for "
                "the requested operation. Validate or convert "
                "the input before using it.",
                "strong"
            )

        # =================================================
        # RANGE ERROR
        # =================================================

        if (
            "rangeerror" in exception_lower
            or "rangeerror" in text_lower
        ):
            return (
                "The operation uses a value outside the "
                "supported range. Validate the value before "
                "performing the operation.",
                "strong"
            )

        # =================================================
        # SYNTAX ERROR
        # =================================================

        if (
            "syntaxerror" in exception_lower
            or "syntax error" in text_lower
        ):
            return (
                "The submitted source contains invalid syntax "
                "that prevents the language parser or runtime "
                "from processing the statement correctly.",
                "strong"
            )

        # =================================================
        # DATABASE / SQL
        # =================================================

        if (
            "sql" in text_lower
            and (
                "constraint" in text_lower
                or "duplicate" in text_lower
                or "database" in text_lower
            )
        ):
            return (
                "The failure is related to a database "
                "operation or constraint. Validate the query, "
                "input data, and database constraints involved "
                "in the failing operation.",
                "medium"
            )

        # =================================================
        # GENERIC NULL FAILURE
        # =================================================

        if (
            "null" in text_lower
            and (
                "dereference" in text_lower
                or "object" in text_lower
                or "pointer" in text_lower
            )
        ):
            return (
                "A null value is being used where a valid "
                "object or memory reference is required. "
                "Validate or initialize the value before it is "
                "used.",
                "medium"
            )

        # =================================================
        # GENERIC EXCEPTION
        # =================================================

        if exception_type:
            return (
                "The detected exception indicates a runtime "
                "failure near the identified failure point. "
                "The supplied evidence does not match a more "
                "specific deterministic root-cause rule.",
                "medium"
            )

        # =================================================
        # FALLBACK
        # =================================================

        return (
            "The available evidence indicates a runtime "
            "failure, but the current deterministic analysis "
            "rules cannot identify a specific underlying "
            "cause from the supplied information.",
            "weak"
        )
        # =====================================================
    # PYTHON ZERO DIVISION ANALYSIS
    # =====================================================

    def _analyze_python_zero_division(
        self,
        text,
        failure_code=None
    ):
        import re

        source_text = text or ""
        failure_statement = (
            failure_code or ""
        ).strip()

        # Detect the divisor from the failure statement.
        #
        # Example:
        # return a / b
        #
        # divisor = b

        divisor_match = re.search(
            r'/\s*([A-Za-z_]\w*)',
            failure_statement
        )

        if not divisor_match:
            return None

        divisor = divisor_match.group(1)

        # Find a function containing this divisor as a parameter.
        #
        # Example:
        # def divide(a, b):

        function_pattern = re.compile(
            r'def\s+'
            r'([A-Za-z_]\w*)'
            r'\s*\(([^)]*)\)\s*:'
        )

        for function_match in (
            function_pattern.finditer(
                source_text
            )
        ):
            function_name = (
                function_match.group(1)
            )

            parameters = [
                parameter.strip()
                for parameter
                in function_match.group(2).split(",")
                if parameter.strip()
            ]

            if divisor not in parameters:
                continue

            divisor_position = (
                parameters.index(
                    divisor
                )
            )

            # Find calls to that function.
            #
            # Example:
            # divide(10, 0)

            call_pattern = re.compile(
                rf'\b{re.escape(function_name)}'
                r'\s*\(([^)]*)\)'
            )

            for call_match in (
                call_pattern.finditer(
                    source_text
                )
            ):
                arguments = [
                    argument.strip()
                    for argument
                    in call_match.group(1).split(",")
                ]

                if (
                    divisor_position
                    >= len(arguments)
                ):
                    continue

                divisor_argument = (
                    arguments[
                        divisor_position
                    ]
                )

                if re.fullmatch(
                    r'[+-]?0+(?:\.0*)?',
                    divisor_argument
                ):
                    return (
                        f"The function {function_name}() performs "
                        f"division using '{divisor}' as the divisor. "
                        f"The call {function_name}("
                        f"{', '.join(arguments)}) passes 0 to "
                        f"'{divisor}', causing a ZeroDivisionError. "
                        f"The divisor '{divisor}' must be validated "
                        "before the division is performed."
                    )

        return (
            f"The failure statement performs division using "
            f"'{divisor}' as the divisor. The detected "
            "ZeroDivisionError indicates that this divisor "
            "receives a zero value at runtime. Validate the "
            f"value of '{divisor}' before performing division."
        )
    # =====================================================
    # CONFIDENCE CALCULATION
    # =====================================================

    def _calculate_confidence(
        self,
        strength,
        exception_type=None,
        failure_file=None,
        failure_line=None,
        failure_function=None,
        failure_code=None
    ):
        if strength == "strong":
            confidence = 0.55

        elif strength == "medium":
            confidence = 0.45

        else:
            confidence = 0.30

        if exception_type:
            confidence += 0.10

        if failure_file:
            confidence += 0.05

        if failure_line is not None:
            confidence += 0.05

        if failure_function:
            confidence += 0.05

        if failure_code:
            confidence += 0.10

        confidence = min(
            confidence,
            0.95
        )

        return round(
            confidence,
            2
        )

    # =====================================================
    # EXPLANATION BUILDER
    # =====================================================

    def _build_explanation(
        self,
        root_cause,
        exception_type=None,
        failure_file=None,
        failure_line=None,
        failure_function=None,
        failure_code=None,
        bug_type=""
    ):
        parts = []

        if exception_type:
            parts.append(
                f"The detected exception is "
                f"{exception_type}."
            )

        location_parts = []

        if failure_file:
            location_parts.append(
                f"file {failure_file}"
            )

        if failure_function:
            location_parts.append(
                f"function {failure_function}"
            )

        if failure_line is not None:
            location_parts.append(
                f"line {failure_line}"
            )

        if location_parts:
            parts.append(
                "The failure was detected around "
                + ", ".join(location_parts)
                + "."
            )

        if failure_code:
            parts.append(
                "The suspected failure statement is: "
                f"{failure_code}"
            )

        if bug_type:
            parts.append(
                "The Triage Agent classified the issue as "
                f"{bug_type}."
            )

        parts.append(
            f"Probable cause: {root_cause}"
        )

        return " ".join(parts)


# =========================================================
# SIMPLE FUNCTION INTERFACE
# =========================================================

def run_root_cause_agent(
    title="",
    description="",
    error_message="",
    stack_trace="",
    code="",
    language="",
    bug_type="",
    severity="",
    priority="",
    exception_type=None,
    failure_file=None,
    failure_line=None,
    failure_function=None,
    failure_code=None
):
    agent = RootCauseAgent()

    return agent.analyze(
        title=title,
        description=description,
        error_message=error_message,
        stack_trace=stack_trace,
        code=code,
        language=language,
        bug_type=bug_type,
        severity=severity,
        priority=priority,
        exception_type=exception_type,
        failure_file=failure_file,
        failure_line=failure_line,
        failure_function=failure_function,
        failure_code=failure_code
    )