from agents.log_analysis_agent import run_log_analysis_agent

code = """
function printUserName(user) {
    console.log(user.name);
}

let user = null;
printUserName(user);
"""

result = run_log_analysis_agent(
    code=code,
    language="javascript"
)

print(result)