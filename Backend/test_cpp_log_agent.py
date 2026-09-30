from agents.log_analysis_agent import run_log_analysis_agent

code = """#include <iostream>

void printValue(int *ptr) {
    std::cout << *ptr << std::endl;
}

int main() {
    int *ptr = nullptr;
    printValue(ptr);
    return 0;
}
"""

result = run_log_analysis_agent(
    code=code,
    language="cpp"
)

print(result)