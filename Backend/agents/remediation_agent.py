import re


class RemediationAgent:

    def __init__(self):
        self.name = "Remediation Agent"

    def analyze(
        self,
        language="",
        code="",
        exception_type="",
        failure_file="",
        failure_line=None,
        failure_function="",
        failure_code="",
        root_cause="",
        similar_bugs=None
    ):
        similar_bugs = similar_bugs or []

        language_value = (language or "").strip().lower()
        exception_value = (exception_type or "").strip().lower()

        solution = self._generate_solution(
            language=language_value,
            exception_type=exception_value,
            root_cause=root_cause,
            similar_bugs=similar_bugs
        )

        fixed_code = self._generate_fixed_code(
            language=language_value,
            code=code,
            exception_type=exception_value,
            failure_code=failure_code
        )

        reasoning = self._generate_reasoning(
            exception_type=exception_type,
            failure_file=failure_file,
            failure_line=failure_line,
            failure_function=failure_function,
            root_cause=root_cause,
            similar_bugs=similar_bugs
        )

        confidence = self._calculate_confidence(
            exception_type=exception_type,
            root_cause=root_cause,
            code=code,
            similar_bugs=similar_bugs
        )

        return {
            "agent": self.name,
            "solution": solution,
            "fixed_code": fixed_code,
            "reasoning": reasoning,
            "confidence": confidence
        }

    def _generate_solution(
        self,
        language,
        exception_type,
        root_cause,
        similar_bugs
    ):
        # Specific detected exceptions have first priority.
        if (
            language in ["c", "c++", "cpp"]
            and (
                "segmentation fault" in exception_type
                or "sigsegv" in exception_type
            )
        ):
            return (
                "Validate the pointer before dereferencing it. "
                "A null or invalid pointer should not be accessed "
                "with the -> or * operator. Handle the null-pointer "
                "case before executing the failing statement."
            )

        if (
            language == "php"
            and (
                "error" in exception_type
                or "exception" in exception_type
            )
            and "null" in (root_cause or "").lower()
        ):
            return (
                "Validate that the PHP object is not null before "
                "calling its methods or accessing its properties. "
                "Add an explicit null guard before the failing "
                "member access and handle the missing object safely."
            )

        if (
            language in ["c#", "csharp", "cs"]
            and "nullreferenceexception" in exception_type
        ):
            return (
                "Validate that the C# object is not null before "
                "accessing its properties or methods. Add an explicit "
                "null guard at the failure point and handle the missing "
                "object before dereferencing it."
            )

        if "nullpointerexception" in exception_type:
            return (
                "Validate that the object is not null before "
                "accessing its properties or methods. Check the "
                "repository or service result before dereferencing "
                "the returned object."
            )

        if (
            "indexoutofbound" in exception_type
            or "indexerror" in exception_type
        ):
            return (
                "Validate the index before accessing the collection, "
                "array, or sequence. Ensure the index is within the "
                "valid range before performing the access."
            )

        if "keyerror" in exception_type:
            return (
                "Avoid directly accessing a dictionary key that may "
                "not exist. Use dictionary.get(), check whether the "
                "key exists, or provide an appropriate default value."
            )

        if "zerodivision" in exception_type:
            return (
                "Validate the divisor before performing division. "
                "Handle the zero-value case explicitly so the "
                "division operation is executed only when the "
                "divisor is non-zero."
            )

        if (
            language in [
                "typescript",
                "ts",
                "javascript",
                "js"
            ]
            and "typeerror" in exception_type
        ):
            return (
                "Validate that the object is not undefined or null "
                "before accessing its properties. Add an explicit "
                "guard or handle the missing value before the "
                "failing property access."
            )

        if "typeerror" in exception_type:
            return (
                "Validate the input types before performing the "
                "operation. Convert or reject incompatible values "
                "before the failing statement is executed."
            )

        if "valueerror" in exception_type:
            return (
                "Validate the supplied value before conversion or "
                "processing and handle values that do not satisfy "
                "the expected format or range."
            )

        if (
            "syntaxerror" in exception_type
            or "indentationerror" in exception_type
        ):
            return (
                "Review the reported failure statement and correct "
                "the invalid programming-language syntax before "
                "executing the program again."
            )

        if "referenceerror" in exception_type:
            return (
                "Declare or initialize the referenced JavaScript "
                "variable before it is accessed. If the value belongs "
                "to another scope, pass it explicitly through the "
                "function calls that require it."
            )

        # Root-cause evidence has second priority.
        if root_cause:
            return (
                "Correct the condition identified by the Root Cause "
                f"Agent: {root_cause}"
            )

        # Knowledge Base is only used as a strong-match fallback.
        historical_solution = (
            self._get_reliable_historical_solution(
                similar_bugs
            )
        )

        if historical_solution:
            return (
                "A strongly related resolved issue was found in the "
                "Knowledge Base. Recommended approach: "
                f"{historical_solution}"
            )

        return (
            "Review the detected failure point, validate the input "
            "and object state, and apply defensive error handling "
            "before executing the failing operation."
        )

    def _generate_fixed_code(
        self,
        language,
        code,
        exception_type,
        failure_code
    ):
        source_code = (code or "").strip()

        if not source_code:
            return None

        if (
            language == "php"
            and (
                "error" in exception_type
                or "exception" in exception_type
            )
        ):
            php_fix = self._fix_php_null_member_access(
                source_code,
                failure_code
            )

            if php_fix:
                return php_fix

        if (
            language in ["c#", "csharp", "cs"]
            and "nullreferenceexception" in exception_type
        ):
            return self._fix_csharp_null_reference(
                source_code,
                failure_code
            )

        if (
            language == "java"
            and "nullpointerexception" in exception_type
        ):
            return self._fix_java_null_pointer(
                source_code,
                failure_code
            )

        if (
            language == "python"
            and "keyerror" in exception_type
        ):
            return self._fix_python_key_error(
                source_code,
                failure_code
            )

        if (
            language == "python"
            and "zerodivision" in exception_type
        ):
            return self._fix_python_zero_division(
                source_code,
                failure_code
            )

        if (
            language == "python"
            and "indexerror" in exception_type
        ):
            return self._fix_python_index_error(
                source_code,
                failure_code
            )
        if (
            language == "python"
            and "typeerror" in exception_type
        ):
            return self._fix_python_type_error(
               source_code,
               failure_code
            )

        if (
            language in ["javascript", "js"]
            and "referenceerror" in exception_type
        ):
            return self._fix_javascript_reference_error(
                source_code,
                failure_code
            )

        if (
            language in ["typescript", "ts"]
            and "typeerror" in exception_type
        ):
            return self._fix_typescript_type_error(
                source_code,
                failure_code
            )

        if (
            language in ["javascript", "js"]
            and "typeerror" in exception_type
        ):
            return self._fix_javascript_type_error(
                source_code,
                failure_code
            )

        if (
            language in ["c", "c++", "cpp"]
            and (
                "segmentation fault" in exception_type
                or "sigsegv" in exception_type
            )
        ):
            return self._fix_c_null_pointer(
                source_code,
                failure_code
            )

        return self._generic_fix(
            language,
            source_code
        )
    # =====================================================
    # PHP NULL MEMBER ACCESS FIX
    # =====================================================

    def _fix_php_null_member_access(
        self,
        code,
        failure_code
    ):
        lines = code.splitlines()

        target_line = (
            failure_code or ""
        ).strip()

        target_index = self._find_target_line(
            lines,
            target_line
        )

        variable_name = None

        member_pattern = re.compile(
            r'\$([A-Za-z_]\w*)'
            r'\s*->\s*'
            r'[A-Za-z_]\w*'
        )

        if target_line:
            match = member_pattern.search(
                target_line
            )

            if match:
                variable_name = match.group(1)

        if not variable_name:
            candidate_indexes = []

            if target_index is not None:
                candidate_indexes.append(
                    target_index
                )

            candidate_indexes.extend(
                index
                for index in range(len(lines))
                if index not in candidate_indexes
            )

            for index in candidate_indexes:
                match = member_pattern.search(
                    lines[index]
                )

                if match:
                    variable_name = match.group(1)
                    target_index = index
                    break

        if not variable_name:
            return None

        if target_index is None:
            for index, line in enumerate(lines):
                if re.search(
                    rf'\${re.escape(variable_name)}'
                    r'\s*->',
                    line
                ):
                    target_index = index
                    break

        if target_index is None:
            return None

        start_index = max(
            0,
            target_index - 8
        )

        guard_patterns = [
            re.compile(
                rf'\${re.escape(variable_name)}'
                r'\s*===\s*null',
                re.IGNORECASE
            ),
            re.compile(
                rf'\${re.escape(variable_name)}'
                r'\s*==\s*null',
                re.IGNORECASE
            ),
            re.compile(
                rf'is_null\s*\(\s*'
                rf'\${re.escape(variable_name)}'
                r'\s*\)',
                re.IGNORECASE
            ),
            re.compile(
                rf'!\s*\${re.escape(variable_name)}\b'
            )
        ]

        for index in range(
            start_index,
            target_index
        ):
            for pattern in guard_patterns:
                if pattern.search(lines[index]):
                    return code

        indentation = (
            lines[target_index][
                :len(lines[target_index])
                - len(lines[target_index].lstrip())
            ]
        )

        display_name = (
            variable_name[:1].upper()
            + variable_name[1:]
        )

        validation = [
            (
                f"{indentation}if "
                f"(${variable_name} === null) {{"
            ),
            (
                f"{indentation}    "
                "throw new InvalidArgumentException("
                f"'{display_name} cannot be null'"
                ");"
            ),
            f"{indentation}}}",
            ""
        ]

        fixed_lines = (
            lines[:target_index]
            + validation
            + lines[target_index:]
        )

        return "\n".join(fixed_lines)
    # =====================================================
    # C# NULL REFERENCE FIX
    # =====================================================

    def _fix_csharp_null_reference(
        self,
        code,
        failure_code
    ):
        lines = code.splitlines()

        target_line = (
            failure_code or ""
        ).strip()

        target_index = self._find_target_line(
            lines,
            target_line
        )

        variable_name = None

        property_pattern = re.compile(
            r"\b([A-Za-z_]\w*)\s*\.\s*"
            r"([A-Za-z_]\w*)"
        )

        ignored_objects = {
            "Console",
            "System",
            "Math",
            "String",
            "Convert",
            "DateTime"
        }

        if target_line:
            matches = list(
                property_pattern.finditer(
                    target_line
                )
            )

            for match in reversed(matches):
                candidate = match.group(1)

                if candidate not in ignored_objects:
                    variable_name = candidate
                    break

        if not variable_name:
            candidate_indexes = []

            if target_index is not None:
                candidate_indexes.append(
                    target_index
                )

            candidate_indexes.extend(
                index
                for index in range(len(lines))
                if index not in candidate_indexes
            )

            for index in candidate_indexes:
                line = lines[index]

                matches = list(
                    property_pattern.finditer(
                        line
                    )
                )

                for match in reversed(matches):
                    candidate = match.group(1)

                    if candidate in ignored_objects:
                        continue

                    variable_name = candidate
                    target_index = index
                    break

                if variable_name:
                    break

        if not variable_name:
            return (
                code
                + "\n\n"
                "// BugSense recommendation: validate the "
                "object for null before accessing its "
                "properties or methods."
            )

        if target_index is None:
            for index, line in enumerate(lines):
                if re.search(
                    rf"\b{re.escape(variable_name)}\s*\.",
                    line
                ):
                    target_index = index
                    break

        if target_index is None:
            return (
                code
                + "\n\n"
                f"// BugSense recommendation: verify that "
                f"{variable_name} is not null before access."
            )

        start_index = max(
            0,
            target_index - 8
        )

        guard_patterns = [
            re.compile(
                rf"\b{re.escape(variable_name)}\s*"
                r"==\s*null"
            ),
            re.compile(
                rf"\b{re.escape(variable_name)}\s+"
                r"is\s+null"
            )
        ]

        for index in range(
            start_index,
            target_index
        ):
            for pattern in guard_patterns:
                if pattern.search(
                    lines[index]
                ):
                    return code

        indentation = (
            lines[target_index][
                :len(lines[target_index])
                - len(lines[target_index].lstrip())
            ]
        )

        validation = [
            (
                f"{indentation}if "
                f"({variable_name} == null)"
            ),
            f"{indentation}{{",
            (
                f"{indentation}    "
                "throw new ArgumentNullException("
                f"nameof({variable_name}));"
            ),
            f"{indentation}}}",
            ""
        ]

        fixed_lines = (
            lines[:target_index]
            + validation
            + lines[target_index:]
        )

        return "\n".join(
            fixed_lines
        )

    # =====================================================
    # TYPESCRIPT TYPE ERROR FIX
    # =====================================================

    def _fix_typescript_type_error(
        self,
        code,
        failure_code
    ):
        return self._fix_js_ts_property_access(
            code=code,
            failure_code=failure_code,
            language="typescript"
        )

    # =====================================================
    # JAVASCRIPT TYPE ERROR FIX
    # =====================================================

    def _fix_javascript_type_error(
        self,
        code,
        failure_code
    ):
        return self._fix_js_ts_property_access(
            code=code,
            failure_code=failure_code,
            language="javascript"
        )

    # =====================================================
    # JS / TS UNDEFINED PROPERTY FIX
    # =====================================================

    def _fix_js_ts_property_access(
        self,
        code,
        failure_code,
        language
    ):
        lines = code.splitlines()
        target_line = (failure_code or "").strip()

        target_index = self._find_target_line(
            lines,
            target_line
        )

        property_pattern = re.compile(
            r"\b([A-Za-z_$][\w$]*)\s*\.\s*"
            r"([A-Za-z_$][\w$]*)"
        )

        variable_name = None

        if target_line:
            match = property_pattern.search(
                target_line
            )

            if match:
                candidate = match.group(1)

                if candidate not in [
                    "console",
                    "Math",
                    "JSON",
                    "Object",
                    "Array",
                    "String",
                    "Number",
                    "Date",
                    "Promise"
                ]:
                    variable_name = candidate

        if not variable_name:
            candidate_indexes = []

            if target_index is not None:
                candidate_indexes.append(
                    target_index
                )

            candidate_indexes.extend(
                index
                for index in range(len(lines))
                if index not in candidate_indexes
            )

            for index in candidate_indexes:
                line = lines[index]

                for match in property_pattern.finditer(
                    line
                ):
                    candidate = match.group(1)

                    if candidate in [
                        "console",
                        "Math",
                        "JSON",
                        "Object",
                        "Array",
                        "String",
                        "Number",
                        "Date",
                        "Promise"
                    ]:
                        continue

                    variable_name = candidate
                    target_index = index
                    break

                if variable_name:
                    break

        if not variable_name:
            comment_prefix = (
                "//"
                if language in [
                    "typescript",
                    "javascript"
                ]
                else "#"
            )

            return (
                code
                + "\n\n"
                + comment_prefix
                + " BugSense recommendation: validate the "
                "possibly undefined or null value before "
                "accessing its properties."
            )

        if target_index is None:
            for index, line in enumerate(lines):
                if re.search(
                    rf"\b{re.escape(variable_name)}\s*\.",
                    line
                ):
                    target_index = index
                    break

        if target_index is None:
            return (
                code
                + "\n\n"
                f"// BugSense recommendation: verify that "
                f"{variable_name} is defined before accessing it."
            )

        if self._has_js_ts_guard(
            lines,
            target_index,
            variable_name
        ):
            return code

        indentation = (
            lines[target_index][
                :len(lines[target_index])
                - len(lines[target_index].lstrip())
            ]
        )

        validation = [
            f"{indentation}if (!{variable_name}) {{",
            (
                f"{indentation}    "
                f'throw new Error("{variable_name} is required");'
            ),
            f"{indentation}}}",
            ""
        ]

        fixed_lines = (
            lines[:target_index]
            + validation
            + lines[target_index:]
        )

        return "\n".join(
            fixed_lines
        )

    def _has_js_ts_guard(
        self,
        lines,
        target_index,
        variable_name
    ):
        start_index = max(
            0,
            target_index - 8
        )

        patterns = [
            re.compile(
                rf"if\s*\(\s*!\s*"
                rf"{re.escape(variable_name)}\s*\)"
            ),
            re.compile(
                rf"{re.escape(variable_name)}\s*"
                r"===?\s*undefined"
            ),
            re.compile(
                rf"{re.escape(variable_name)}\s*"
                r"===?\s*null"
            ),
            re.compile(
                rf"{re.escape(variable_name)}\s*"
                r"==\s*null"
            ),
            re.compile(
                rf"typeof\s+"
                rf"{re.escape(variable_name)}\s*"
                r"===?\s*['\"]undefined['\"]"
            )
        ]

        for index in range(
            start_index,
            target_index
        ):
            line = lines[index]

            for pattern in patterns:
                if pattern.search(line):
                    return True

        return False

    # =====================================================
    # C / C++ NULL POINTER FIX
    # =====================================================

    def _fix_c_null_pointer(
        self,
        code,
        failure_code
    ):
        lines = code.splitlines()

        target_line = (
            failure_code or ""
        ).strip()

        pointer_name = self._extract_c_pointer(
            target_line
        )

        target_index = self._find_target_line(
            lines,
            target_line
        )

        if not pointer_name:
            for index, line in enumerate(lines):
                match = re.search(
                    r'\b([A-Za-z_]\w*)\s*->',
                    line
                )

                if match:
                    pointer_name = match.group(1)
                    target_index = index
                    break

        if not pointer_name:
            return (
                code
                + "\n\n"
                "// BugSense recommendation: validate the pointer "
                "before dereferencing it."
            )

        if target_index is None:
            for index, line in enumerate(lines):
                if re.search(
                    rf'\b{re.escape(pointer_name)}\s*->',
                    line
                ):
                    target_index = index
                    break

        if target_index is None:
            return (
                code
                + "\n\n"
                f"// BugSense recommendation: verify that "
                f"{pointer_name} is not NULL before dereferencing it."
            )

        for index in range(
            max(0, target_index - 8),
            target_index
        ):
            if re.search(
                rf'\b{re.escape(pointer_name)}\s*'
                r'==\s*(?:NULL|nullptr)',
                lines[index]
            ):
                return code

            if re.search(
                rf'!\s*{re.escape(pointer_name)}\b',
                lines[index]
            ):
                return code

        indentation = (
            lines[target_index][
                :len(lines[target_index])
                - len(lines[target_index].lstrip())
            ]
        )

        null_value = (
            "nullptr"
            if "nullptr" in code
            else "NULL"
        )

        return_statement = (
            self._get_c_guard_return_statement(
                lines,
                target_index,
                null_value
            )
        )

        validation = [
            (
                f"{indentation}if "
                f"({pointer_name} == {null_value}) {{"
            ),
            (
                f"{indentation}    "
                f"{return_statement}"
            ),
            f"{indentation}}}",
            ""
        ]

        fixed_lines = (
            lines[:target_index]
            + validation
            + lines[target_index:]
        )

        return "\n".join(
            fixed_lines
        )

    def _get_c_guard_return_statement(
        self,
        lines,
        target_index,
        null_value
    ):
        function_info = (
            self._find_enclosing_c_function(
                lines,
                target_index
            )
        )

        if not function_info:
            return "return;"

        return_type = (
            function_info["return_type"]
            .strip()
            .replace(" *", "*")
            .replace("* ", "*")
        )

        normalized_type = (
            return_type
            .lower()
            .replace(" ", "")
        )

        function_name = (
            function_info["name"]
        )

        if normalized_type == "void":
            return "return;"

        if function_name == "main":
            return "return 1;"

        if normalized_type == "bool":
            return "return false;"

        if "*" in normalized_type:
            return f"return {null_value};"

        integer_types = {
            "int",
            "short",
            "long",
            "longlong",
            "signed",
            "signedint",
            "unsigned",
            "unsignedint",
            "unsignedshort",
            "unsignedlong",
            "unsignedlonglong",
            "size_t",
            "ssize_t"
        }

        if normalized_type in integer_types:
            return "return 1;"

        floating_types = {
            "float",
            "double",
            "longdouble"
        }

        if normalized_type in floating_types:
            return "return 0;"

        return "return {};"

    def _find_enclosing_c_function(
        self,
        lines,
        target_index
    ):
        brace_depth = 0

        control_keywords = {
            "if",
            "for",
            "while",
            "switch",
            "catch"
        }

        for index in range(
            target_index,
            -1,
            -1
        ):
            line = lines[index]
            stripped = line.strip()

            brace_depth += line.count("}")
            brace_depth -= line.count("{")

            if "(" not in stripped:
                continue

            if ")" not in stripped:
                continue

            prefix = stripped.split(
                "(",
                1
            )[0].strip()

            if not prefix:
                continue

            parts = prefix.split()

            if len(parts) < 2:
                continue

            function_name = (
                parts[-1]
                .replace("*", "")
                .replace("&", "")
            )

            if function_name in control_keywords:
                continue

            return_type = " ".join(
                parts[:-1]
            )

            if parts[-1].startswith("*"):
                return_type += "*"

            if not return_type:
                continue

            if brace_depth <= 0:
                return {
                    "name": function_name,
                    "return_type": return_type,
                    "line": index
                }

        return None

    def _extract_c_pointer(
        self,
        failure_code
    ):
        if not failure_code:
            return None

        arrow_match = re.search(
            r'\b([A-Za-z_]\w*)\s*->',
            failure_code
        )

        if arrow_match:
            return arrow_match.group(1)

        dereference_match = re.search(
            r'\*\s*([A-Za-z_]\w*)',
            failure_code
        )

        if dereference_match:
            return dereference_match.group(1)

        return None

    # =====================================================
    # JAVA NULL POINTER FIX
    # =====================================================

    def _fix_java_null_pointer(
        self,
        code,
        failure_code
    ):
        lines = code.splitlines()
        target_line = (failure_code or "").strip()

        target_index = self._find_target_line(
            lines,
            target_line
        )

        access_pattern = re.compile(
            r"\b([A-Za-z_]\w*)\s*\.\s*[A-Za-z_]\w*"
        )

        ignored_objects = {
            "System",
            "out",
            "err",
            "Math",
            "String",
            "Integer",
            "Long",
            "Double",
            "Float",
            "Boolean",
            "Character",
            "Objects",
            "Collections",
            "Arrays"
        }

        variable_name = None

        if target_line:
            matches = list(
                access_pattern.finditer(target_line)
            )

            for match in reversed(matches):
                candidate = match.group(1)

                if candidate not in ignored_objects:
                    variable_name = candidate
                    break

        if not variable_name:
            candidate_indexes = []

            if target_index is not None:
                candidate_indexes.append(target_index)

            candidate_indexes.extend(
                index
                for index in range(len(lines))
                if index not in candidate_indexes
            )

            for index in candidate_indexes:
                matches = list(
                    access_pattern.finditer(lines[index])
                )

                for match in reversed(matches):
                    candidate = match.group(1)

                    if candidate in ignored_objects:
                        continue

                    variable_name = candidate
                    target_index = index
                    break

                if variable_name:
                    break

        if not variable_name:
            return (
                code
                + "\n\n"
                "// BugSense recommendation: validate the object "
                "for null before accessing its properties or methods."
            )

        if target_index is None:
            for index, line in enumerate(lines):
                if re.search(
                    rf"\b{re.escape(variable_name)}\s*\.",
                    line
                ):
                    target_index = index
                    break

        if target_index is None:
            return (
                code
                + "\n\n"
                f"// BugSense recommendation: verify that "
                f"{variable_name} is not null before access."
            )

        start_index = max(0, target_index - 8)

        guard_patterns = [
            re.compile(
                rf"\b{re.escape(variable_name)}\s*==\s*null"
            ),
            re.compile(
                rf"\bnull\s*==\s*{re.escape(variable_name)}\b"
            ),
            re.compile(
                rf"\bObjects\.isNull\s*\(\s*"
                rf"{re.escape(variable_name)}\s*\)"
            )
        ]

        for index in range(start_index, target_index):
            for pattern in guard_patterns:
                if pattern.search(lines[index]):
                    return code

        indentation = (
            lines[target_index][
                :len(lines[target_index])
                - len(lines[target_index].lstrip())
            ]
        )

        validation = [
            f"{indentation}if ({variable_name} == null) {{",
            (
                f"{indentation}    "
                "throw new IllegalStateException("
                f'"{variable_name} must not be null"'
                ");"
            ),
            f"{indentation}}}",
            ""
        ]

        fixed_lines = (
            lines[:target_index]
            + validation
            + lines[target_index:]
        )

        return "\n".join(fixed_lines)

      # =====================================================
    # PYTHON KEY ERROR FIX
    # =====================================================

    def _fix_python_key_error(
        self,
        code,
        failure_code
    ):
        lines = code.splitlines()

        target_line = (
            failure_code or ""
        ).strip()

        dictionary_pattern = re.compile(
            r"([A-Za-z_]\w*)"
            r"\[\s*(['\"])([^'\"]+)\2\s*\]"
        )

        # -------------------------------------------------
        # 1. Identify the missing key from failure_code
        # -------------------------------------------------

        missing_key = None
        dictionary_name = None

        if target_line:
            matches = list(
                dictionary_pattern.finditer(
                    target_line
                )
            )

            if matches:
                # Prefer the final dictionary access
                # on the actual failing statement.
                match = matches[-1]

                dictionary_name = match.group(1)
                missing_key = match.group(3)

        # -------------------------------------------------
        # 2. Try exact failure-line matching first
        # -------------------------------------------------

        target_index = self._find_target_line(
            lines,
            target_line
        )

        if target_index is not None:
            original_line = lines[target_index]

            if missing_key:
                specific_pattern = re.compile(
                    rf"\b{re.escape(dictionary_name)}"
                    rf"\[\s*(['\"])"
                    rf"{re.escape(missing_key)}"
                    rf"\1\s*\]"
                )

                fixed_line = specific_pattern.sub(
                    lambda match: (
                        f"{dictionary_name}.get("
                        f"{match.group(1)}"
                        f"{missing_key}"
                        f"{match.group(1)}, "
                        f'"Not available")'
                    ),
                    original_line
                )

            else:
                fixed_line = dictionary_pattern.sub(
                    lambda match: (
                        f"{match.group(1)}.get("
                        f"{match.group(2)}"
                        f"{match.group(3)}"
                        f"{match.group(2)}, "
                        f'"Not available")'
                    ),
                    original_line,
                    count=1
                )

            if fixed_line != original_line:
                lines[target_index] = fixed_line

                return "\n".join(lines)

        # -------------------------------------------------
        # 3. Search specifically for the missing key
        # -------------------------------------------------

        if missing_key:
            for index, line in enumerate(lines):

                for match in dictionary_pattern.finditer(line):

                    current_dictionary = match.group(1)
                    current_key = match.group(3)

                    if current_key != missing_key:
                        continue

                    quote = match.group(2)

                    replacement = (
                        f"{current_dictionary}.get("
                        f"{quote}{current_key}{quote}, "
                        f'"Not available")'
                    )

                    fixed_line = (
                        line[:match.start()]
                        + replacement
                        + line[match.end():]
                    )

                    lines[index] = fixed_line

                    return "\n".join(lines)

        # -------------------------------------------------
        # 4. Safe fallback
        # -------------------------------------------------

        return (
            code
            + "\n\n"
            "# BugSense recommendation: identify the missing "
            "dictionary key from the KeyError and use "
            "dictionary.get(key, default) or check whether "
            "the key exists before accessing it."
        )
        # =====================================================
    # PYTHON TYPE ERROR FIX
    # =====================================================

    def _fix_python_type_error(
        self,
        code,
        failure_code
    ):
        lines = code.splitlines()

        target_line = (
            failure_code or ""
        ).strip()

        target_index = self._find_target_line(
            lines,
            target_line
        )

        # If the exact failure line was not found,
        # search for a likely string concatenation.
        if target_index is None:
            for index, line in enumerate(lines):
                if "+" in line and "=" in line:
                    target_index = index
                    break

        if target_index is None:
            return (
                code
                + "\n\n"
                "# BugSense recommendation: validate input types "
                "and None values before performing the operation."
            )

        failing_line = lines[target_index]

        # Example:
        # message = "Welcome " + username
        match = re.search(
            r'(["\'][^"\']*["\'])\s*\+\s*([A-Za-z_]\w*)',
            failing_line
        )

        if match:
            variable_name = match.group(2)

        else:
            # Also support:
            # message = username + "..."
            match = re.search(
                r'([A-Za-z_]\w*)\s*\+\s*(["\'][^"\']*["\'])',
                failing_line
            )

            if match:
                variable_name = match.group(1)
            else:
                return (
                    code
                    + "\n\n"
                    "# BugSense recommendation: validate input types "
                    "and None values before performing the failing operation."
                )

        indentation = (
            failing_line[
                :len(failing_line)
                - len(failing_line.lstrip())
            ]
        )

        validation = [
            f"{indentation}if {variable_name} is None:",
            (
                f'{indentation}    '
                'return "Welcome Guest"'
            ),
            ""
        ]

        fixed_lines = (
            lines[:target_index]
            + validation
            + lines[target_index:]
        )

        return "\n".join(
            fixed_lines
        )
    # =====================================================
    # PYTHON ZERO DIVISION FIX
    # =====================================================

    def _fix_python_zero_division(
        self,
        code,
        failure_code
    ):
        lines = code.splitlines()

        target_line = (
            failure_code or ""
        ).strip()

        target_index = self._find_target_line(
            lines,
            target_line
        )

        division_pattern = re.compile(
            r"/\s*([A-Za-z_]\w*)"
        )

        candidate_indexes = []

        if target_index is not None:
            candidate_indexes.append(
                target_index
            )

        candidate_indexes.extend(
            index
            for index in range(len(lines))
            if index not in candidate_indexes
        )

        for index in candidate_indexes:
            line = lines[index]

            match = division_pattern.search(
                line
            )

            if not match:
                continue

            divisor = match.group(1)

            indentation = (
                line[
                    :len(line)
                    - len(line.lstrip())
                ]
            )

            validation = [
                (
                    f"{indentation}"
                    f"if {divisor} == 0:"
                ),
                (
                    f"{indentation}    "
                    "raise ValueError("
                    f'"{divisor} must not be zero"'
                    ")"
                )
            ]

            fixed_lines = (
                lines[:index]
                + validation
                + lines[index:]
            )

            return "\n".join(
                fixed_lines
            )

        return (
            code
            + "\n\n"
            "# BugSense recommendation: validate that the "
            "divisor is not zero before division."
        )

    # =====================================================
    # PYTHON INDEX ERROR FIX
    # =====================================================

    def _fix_python_index_error(
        self,
        code,
        failure_code
    ):
        lines = code.splitlines()

        target_line = (
            failure_code or ""
        ).strip()

        target_index = self._find_target_line(
            lines,
            target_line
        )

        index_pattern = re.compile(
            r"\b([A-Za-z_]\w*)"
            r"\[\s*([A-Za-z_]\w*)\s*\]"
        )

        candidate_indexes = []

        if target_index is not None:
            candidate_indexes.append(
                target_index
            )

        candidate_indexes.extend(
            index
            for index in range(len(lines))
            if index not in candidate_indexes
        )

        for index in candidate_indexes:
            line = lines[index]

            match = index_pattern.search(
                line
            )

            if not match:
                continue

            collection = match.group(1)
            index_variable = match.group(2)

            indentation = (
                line[
                    :len(line)
                    - len(line.lstrip())
                ]
            )

            validation = [
                (
                    f"{indentation}"
                    f"if not (0 <= {index_variable} "
                    f"< len({collection})):"
                ),
                (
                    f"{indentation}    "
                    "raise IndexError("
                    f'"Invalid index for {collection}"'
                    ")"
                )
            ]

            fixed_lines = (
                lines[:index]
                + validation
                + lines[index:]
            )

            return "\n".join(
                fixed_lines
            )

        return (
            code
            + "\n\n"
            "# BugSense recommendation: validate the index "
            "before accessing the sequence."
        )

    # =====================================================
    # JAVASCRIPT REFERENCE ERROR FIX
    # =====================================================

    def _fix_javascript_reference_error(
        self,
        code,
        failure_code
    ):
        variable = self._extract_js_reference_variable(
            failure_code
        )

        if not variable:
            return (
                code
                + "\n\n"
                "// BugSense recommendation: declare or initialize "
                "the referenced variable before it is accessed."
            )

        lines = code.splitlines()

        functions = self._parse_js_functions(
            lines
        )

        target_function = None

        for function in functions:
            body = "\n".join(
                lines[
                    function["start"]:
                    function["end"] + 1
                ]
            )

            if re.search(
                rf"\b{re.escape(variable)}\b",
                body
            ):
                target_function = function
                break

        if not target_function:
            return (
                code
                + "\n\n"
                f"// BugSense recommendation: define "
                f"{variable} before it is accessed."
            )

        required_function = (
            target_function["name"]
        )

        self._add_js_parameter(
            lines,
            target_function,
            variable
        )

        processed_functions = {
            required_function
        }

        while True:
            functions = self._parse_js_functions(
                lines
            )

            caller_found = False

            for function in functions:
                if (
                    function["name"]
                    in processed_functions
                ):
                    continue

                call_index = (
                    self._find_js_call_inside_function(
                        lines,
                        function,
                        required_function
                    )
                )

                if call_index is None:
                    continue

                self._add_argument_to_js_call(
                    lines,
                    call_index,
                    required_function,
                    variable
                )

                self._add_js_parameter(
                    lines,
                    function,
                    variable
                )

                required_function = (
                    function["name"]
                )

                processed_functions.add(
                    required_function
                )

                caller_found = True
                break

            if not caller_found:
                break

        top_level_call = (
            self._find_js_top_level_call(
                lines,
                required_function
            )
        )

        if top_level_call is not None:
            self._replace_js_call_with_external_placeholder(
                lines,
                top_level_call,
                required_function,
                variable
            )

        return "\n".join(
            lines
        )

    def _parse_js_functions(
        self,
        lines
    ):
        functions = []

        pattern = re.compile(
            r"^(\s*)function\s+"
            r"([A-Za-z_$][\w$]*)\s*"
            r"\(([^)]*)\)\s*\{"
        )

        index = 0

        while index < len(lines):
            match = pattern.search(
                lines[index]
            )

            if not match:
                index += 1
                continue

            end_index = (
                self._find_js_function_end(
                    lines,
                    index
                )
            )

            if end_index is None:
                index += 1
                continue

            functions.append({
                "name": match.group(2),
                "start": index,
                "end": end_index
            })

            index = end_index + 1

        return functions

    def _add_js_parameter(
        self,
        lines,
        function,
        variable
    ):
        index = function["start"]

        pattern = re.compile(
            r"^(\s*)function\s+"
            r"([A-Za-z_$][\w$]*)\s*"
            r"\(([^)]*)\)\s*\{"
        )

        match = pattern.search(
            lines[index]
        )

        if not match:
            return

        indentation = match.group(1)
        function_name = match.group(2)
        parameters = match.group(3).strip()

        parameter_list = [
            item.strip()
            for item in parameters.split(",")
            if item.strip()
        ]

        if variable not in parameter_list:
            parameter_list.append(
                variable
            )

        lines[index] = (
            f"{indentation}function "
            f"{function_name}("
            f"{', '.join(parameter_list)}) {{"
        )

    def _find_js_call_inside_function(
        self,
        lines,
        function,
        called_function
    ):
        pattern = re.compile(
            rf"\b{re.escape(called_function)}"
            r"\s*\(([^)]*)\)"
        )

        for index in range(
            function["start"] + 1,
            function["end"]
        ):
            if pattern.search(
                lines[index]
            ):
                return index

        return None

    def _add_argument_to_js_call(
        self,
        lines,
        line_index,
        function_name,
        variable
    ):
        pattern = re.compile(
            rf"\b{re.escape(function_name)}"
            r"\s*\(([^)]*)\)"
        )

        match = pattern.search(
            lines[line_index]
        )

        if not match:
            return

        arguments = (
            match.group(1).strip()
        )

        argument_list = [
            item.strip()
            for item in arguments.split(",")
            if item.strip()
        ]

        if variable not in argument_list:
            argument_list.append(
                variable
            )

        replacement = (
            f"{function_name}("
            f"{', '.join(argument_list)})"
        )

        lines[line_index] = (
            lines[line_index][
                :match.start()
            ]
            + replacement
            + lines[line_index][
                match.end():
            ]
        )

    def _find_js_top_level_call(
        self,
        lines,
        function_name
    ):
        functions = self._parse_js_functions(
            lines
        )

        function_ranges = [
            (
                function["start"],
                function["end"]
            )
            for function in functions
        ]

        pattern = re.compile(
            rf"^\s*{re.escape(function_name)}"
            r"\s*\(([^)]*)\)\s*;?\s*$"
        )

        for index, line in enumerate(lines):
            inside_function = any(
                start <= index <= end
                for start, end
                in function_ranges
            )

            if inside_function:
                continue

            if pattern.search(line):
                return index

        return None

    def _replace_js_call_with_external_placeholder(
        self,
        lines,
        line_index,
        function_name,
        variable
    ):
        indentation = (
            lines[line_index][
                :len(lines[line_index])
                - len(lines[line_index].lstrip())
            ]
        )

        lines[line_index] = (
            f"{indentation}"
            f"{function_name}(/* {variable} */);"
        )

        lines.insert(
            line_index,
            (
                f"{indentation}"
                f"// Pass the actual {variable} "
                "from your application data."
            )
        )

    def _extract_js_reference_variable(
        self,
        failure_code
    ):
        target = (
            failure_code or ""
        ).strip()

        if not target:
            return None

        common_calls = re.search(
            r"(?:console\.\w+|alert)\s*\(\s*"
            r"([A-Za-z_$][\w$]*)\s*\)",
            target
        )

        if common_calls:
            return common_calls.group(1)

        return_match = re.search(
            r"\breturn\s+"
            r"([A-Za-z_$][\w$]*)\b",
            target
        )

        if return_match:
            return return_match.group(1)

        assignment_match = re.search(
            r"=\s*"
            r"([A-Za-z_$][\w$]*)"
            r"\s*;?\s*$",
            target
        )

        if assignment_match:
            return assignment_match.group(1)

        return None

    def _find_js_function_end(
        self,
        lines,
        start_index
    ):
        brace_count = 0
        started = False

        for index in range(
            start_index,
            len(lines)
        ):
            line = lines[index]

            brace_count += line.count("{")
            brace_count -= line.count("}")

            if "{" in line:
                started = True

            if (
                started
                and brace_count == 0
            ):
                return index

        return None

    # =====================================================
    # SHARED HELPERS
    # =====================================================

    def _find_target_line(
        self,
        lines,
        failure_code
    ):
        if not failure_code:
            return None

        normalized_target = (
            failure_code.strip()
        )

        for index, line in enumerate(lines):
            if (
                line.strip()
                == normalized_target
            ):
                return index

        return None

    def _generic_fix(
        self,
        language,
        code
    ):
        if language in [
            "java",
            "javascript",
            "js",
            "typescript",
            "ts",
            "c",
            "c++",
            "cpp",
            "c#",
            "csharp",
            "cs"
        ]:
            return (
                code
                + "\n\n"
                "// BugSense recommendation: review the "
                "detected failure point and add appropriate "
                "validation or error handling."
            )

        return (
            code
            + "\n\n"
            "# BugSense recommendation: review the detected "
            "failure point and add appropriate validation "
            "or error handling."
        )

    def _get_historical_solution(
        self,
        similar_bugs
    ):
        if not similar_bugs:
            return None

        return similar_bugs[0].get(
            "solution"
        )

    def _get_reliable_historical_solution(
        self,
        similar_bugs,
        minimum_similarity=0.70
    ):
        if not similar_bugs:
            return None

        best_match = similar_bugs[0]

        try:
            similarity = float(
                best_match.get(
                    "similarity",
                    0
                )
            )
        except (TypeError, ValueError):
            similarity = 0

        if similarity < minimum_similarity:
            return None

        solution = best_match.get(
            "solution"
        )

        if (
            not solution
            or self._is_placeholder_solution(
                solution
            )
        ):
            return None

        return solution

    def _is_placeholder_solution(
        self,
        solution
    ):
        value = (
            solution or ""
        ).lower()

        placeholders = [
            "will be generated",
            "remediation agent",
            "pending ai",
            "pending analysis"
        ]

        return any(
            placeholder in value
            for placeholder in placeholders
        )

    def _generate_reasoning(
        self,
        exception_type,
        failure_file,
        failure_line,
        failure_function,
        root_cause,
        similar_bugs
    ):
        details = []

        if exception_type:
            details.append(
                f"The detected exception is "
                f"{exception_type}."
            )

        location = []

        if failure_file:
            location.append(
                f"file {failure_file}"
            )

        if failure_function:
            location.append(
                f"function {failure_function}"
            )

        if failure_line:
            location.append(
                f"line {failure_line}"
            )

        if location:
            details.append(
                "The failure was identified around "
                + ", ".join(location)
                + "."
            )

        if root_cause:
            details.append(
                "The Root Cause Agent identified: "
                f"{root_cause}"
            )

        if similar_bugs:
            best_match = similar_bugs[0]

            similarity = best_match.get(
                "similarity_percent",
                0
            )

            details.append(
                "The Knowledge Base retrieval found a "
                f"historical issue with {similarity}% "
                "semantic similarity."
            )

        details.append(
            "The recommendation focuses on preventing "
            "the detected failure condition before the "
            "failing operation is executed."
        )

        return " ".join(
            details
        )

    def _calculate_confidence(
        self,
        exception_type,
        root_cause,
        code,
        similar_bugs
    ):
        confidence = 0.55

        if exception_type:
            confidence += 0.10

        if root_cause:
            confidence += 0.10

        if code:
            confidence += 0.10

        if similar_bugs:
            best_similarity = float(
                similar_bugs[0].get(
                    "similarity",
                    0
                )
            )

            confidence += (
                best_similarity * 0.15
            )

        return round(
            min(confidence, 0.95),
            4
        )


def run_remediation_agent(
    language="",
    code="",
    exception_type="",
    failure_file="",
    failure_line=None,
    failure_function="",
    failure_code="",
    root_cause="",
    similar_bugs=None
):
    return RemediationAgent().analyze(
        language=language,
        code=code,
        exception_type=exception_type,
        failure_file=failure_file,
        failure_line=failure_line,
        failure_function=failure_function,
        failure_code=failure_code,
        root_cause=root_cause,
        similar_bugs=similar_bugs
    )