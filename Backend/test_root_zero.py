from agents.root_cause_agent import run_root_cause_agent

code = """
def divide(a, b):
    return a / b

print(divide(10, 0))
"""

result = run_root_cause_agent(
    title="ZeroDivisionError in Python Division Function",
    code=code,
    language="python",
    bug_type="Runtime Error",
    severity="Medium",
    priority="P3",
    exception_type="ZeroDivisionError",
    failure_line=3,
    failure_function="divide",
    failure_code="return a / b"
)

print("ROOT CAUSE:")
print(result["root_cause"])

print("\nEXPLANATION:")
print(result["explanation"])

print("\nCONFIDENCE:")
print(result["confidence"])