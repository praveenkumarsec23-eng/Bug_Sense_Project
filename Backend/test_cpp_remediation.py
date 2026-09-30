from agents.remediation_agent import run_remediation_agent

code = """#include <iostream>
#include <string>

class User {
public:
    std::string name;

    void printName() {
        std::cout << name << std::endl;
    }
};

int main() {
    User *user = nullptr;
    user->printName();
    return 0;
}
"""

result = run_remediation_agent(
    language="cpp",
    code=code,
    exception_type="Segmentation fault",
    failure_file="user.cpp",
    failure_line=12,
    failure_function="main",
    failure_code="user->printName();",
    root_cause=(
        "A null or invalid pointer is likely being "
        "dereferenced, causing the program to access "
        "invalid memory."
    ),
    similar_bugs=[]
)

print("=== SOLUTION ===")
print(result["solution"])

print("\n=== FIXED CODE ===")
print(result["fixed_code"])

print("\n=== REASONING ===")
print(result["reasoning"])

print("\n=== CONFIDENCE ===")
print(result["confidence"])