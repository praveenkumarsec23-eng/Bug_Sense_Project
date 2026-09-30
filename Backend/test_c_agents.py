from agents.log_analysis_agent import run_log_analysis_agent
from agents.remediation_agent import run_remediation_agent

error_message = "Segmentation fault (core dumped)"

stack_trace = """Program received signal SIGSEGV, Segmentation fault.
0x0000000000401136 in printUser (user.c:15)
15      printf("%s\\n", user->name);
#0  printUser (user=0x0) at user.c:15
#1  main () at main.c:25"""

code = """#include <stdio.h>

typedef struct {
    char *name;
} User;

void printUser(User *user) {
    printf("%s\\n", user->name);
}

int main() {
    User *user = NULL;
    printUser(user);
    return 0;
}"""

log_result = run_log_analysis_agent(
    error_message=error_message,
    stack_trace=stack_trace,
    code=code,
    language="C"
)

print("=== LOG ANALYSIS ===")
print(log_result)

remediation_result = run_remediation_agent(
    language="C",
    code=code,
    exception_type=log_result["exception"],
    failure_file=log_result["file"],
    failure_line=log_result["line"],
    failure_function=log_result["function"],
    failure_code=log_result["failure_code"],
    root_cause="A null pointer is being dereferenced before it has been validated.",
    similar_bugs=[]
)

print("\n=== SOLUTION ===")
print(remediation_result["solution"])

print("\n=== FIXED CODE ===")
print(remediation_result["fixed_code"])

print("\n=== CONFIDENCE ===")
print(remediation_result["confidence"])