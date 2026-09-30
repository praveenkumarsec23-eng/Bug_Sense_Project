from agents.log_analysis_agent import run_log_analysis_agent

code = """#include <stdio.h>

void printValue(int *ptr) {
    printf("%d\\n", *ptr);
}

int main() {
    int *ptr = NULL;
    printValue(ptr);
    return 0;
}
"""

result = run_log_analysis_agent(
    code=code,
    language="c"
)

print(result)