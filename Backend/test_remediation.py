from agents.remediation_agent import run_remediation_agent

code = """
def divide(a, b):
    return a / b

print(divide(10, 0))
"""

similar_bugs = [
    {
        "similarity": 0.3018,
        "similarity_percent": 30.18,
        "solution": (
            "Avoid directly accessing a dictionary key that may "
            "not exist. Use dictionary.get()."
        )
    }
]

result = run_remediation_agent(
    language="python",
    code=code,
    exception_type="ZeroDivisionError",
    failure_line=3,
    failure_function="divide",
    failure_code="return a / b",
    root_cause=(
        "The function divide() performs division using 'b' as "
        "the divisor. The call divide(10, 0) passes 0 to 'b', "
        "causing a ZeroDivisionError."
    ),
    similar_bugs=similar_bugs
)

print("SOLUTION:")
print(result["solution"])

print("\nFIXED CODE:")
print(result["fixed_code"])

print("\nREASONING:")
print(result["reasoning"])

print("\nCONFIDENCE:")
print(result["confidence"])