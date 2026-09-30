from agents.log_analysis_agent import run_log_analysis_agent

code = """
def divide(a, b):
    return a / b

print(divide(10, 0))
"""

result = run_log_analysis_agent(
    code=code,
    language="python"
)

print(result)