from agents.root_cause_agent import run_root_cause_agent
from agents.remediation_agent import run_remediation_agent

code = """interface User {
    name: string;
}

function displayUser(user: User | undefined) {
    console.log(user.name);
}

function loadProfile() {
    const user: User | undefined = undefined;
    displayUser(user);
}

loadProfile();"""

error_message = "TypeError: Cannot read properties of undefined (reading 'name')"

stack_trace = """TypeError: Cannot read properties of undefined (reading 'name')
    at displayUser (profile.ts:12:22)
    at loadProfile (profile.ts:20:5)"""

failure_code = "console.log(user.name);"

root_result = run_root_cause_agent(
    title="TypeError while accessing undefined user profile",
    description="The application crashes because the user object is undefined.",
    error_message=error_message,
    stack_trace=stack_trace,
    code=code,
    language="TypeScript",
    bug_type="Runtime Error",
    severity="High",
    priority="P2",
    exception_type="TypeError",
    failure_file="profile.ts",
    failure_line=12,
    failure_function="displayUser",
    failure_code=failure_code
)

print("=== ROOT CAUSE ===")
print(root_result["root_cause"])
print("Confidence:", root_result["confidence"])

remediation_result = run_remediation_agent(
    language="TypeScript",
    code=code,
    exception_type="TypeError",
    failure_file="profile.ts",
    failure_line=12,
    failure_function="displayUser",
    failure_code=failure_code,
    root_cause=root_result["root_cause"],
    similar_bugs=[]
)

print("\n=== SOLUTION ===")
print(remediation_result["solution"])

print("\n=== FIXED CODE ===")
print(remediation_result["fixed_code"])

print("\n=== REMEDIATION CONFIDENCE ===")
print(remediation_result["confidence"])