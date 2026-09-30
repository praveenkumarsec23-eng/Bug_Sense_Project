from agents.log_analysis_agent import run_log_analysis_agent
from agents.root_cause_agent import run_root_cause_agent
from agents.remediation_agent import run_remediation_agent

code = """using System;

class User
{
    public string Name { get; set; }
}

class UserService
{
    public void DisplayUser(User user)
    {
        Console.WriteLine(user.Name);
    }
}

class Program
{
    static void Main(string[] args)
    {
        User user = null;
        UserService service = new UserService();
        service.DisplayUser(user);
    }
}
"""

error_message = (
    "System.NullReferenceException: "
    "Object reference not set to an instance of an object."
)

stack_trace = """System.NullReferenceException: Object reference not set to an instance of an object.
   at UserService.DisplayUser(User user) in UserService.cs:line 12
   at Program.Main(String[] args) in Program.cs:line 21
"""

log_result = run_log_analysis_agent(
    error_message=error_message,
    stack_trace=stack_trace,
    code=code,
    language="csharp"
)

print("=== LOG ANALYSIS ===")
print(log_result)

root_result = run_root_cause_agent(
    title="NullReferenceException while displaying user",
    description=(
        "The application crashes while displaying a user's "
        "name because the User object is null."
    ),
    error_message=error_message,
    stack_trace=stack_trace,
    code=code,
    language="csharp",
    bug_type="Application Error",
    severity="High",
    priority="P2",
    exception_type=log_result["exception"],
    failure_file=log_result["file"],
    failure_line=log_result["line"],
    failure_function=log_result["function"],
    failure_code=log_result["failure_code"]
)

print("\n=== ROOT CAUSE ===")
print(root_result)

remediation_result = run_remediation_agent(
    language="csharp",
    code=code,
    exception_type=log_result["exception"],
    failure_file=log_result["file"],
    failure_line=log_result["line"],
    failure_function=log_result["function"],
    failure_code=log_result["failure_code"],
    root_cause=root_result["root_cause"],
    similar_bugs=[]
)

print("\n=== SOLUTION ===")
print(remediation_result["solution"])

print("\n=== FIXED CODE ===")
print(remediation_result["fixed_code"])

print("\n=== REASONING ===")
print(remediation_result["reasoning"])

print("\n=== REMEDIATION CONFIDENCE ===")
print(remediation_result["confidence"])