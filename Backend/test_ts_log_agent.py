from agents.log_analysis_agent import run_log_analysis_agent

code = """interface User {
    name: string;
}

function printUserName(user: User | null) {
    console.log(user.name);
}

let user: User | null = null;
printUserName(user);
"""

result = run_log_analysis_agent(
    code=code,
    language="typescript"
)

print(result)