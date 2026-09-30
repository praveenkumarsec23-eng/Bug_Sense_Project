from agents.log_analysis_agent import run_log_analysis_agent

code = """using System;

class Program
{
    static void PrintUser(User user)
    {
        Console.WriteLine(user.Name);
    }

    static void Main()
    {
        User user = null;
        PrintUser(user);
    }
}

class User
{
    public string Name { get; set; }
}
"""

result = run_log_analysis_agent(
    code=code,
    language="csharp"
)

print(result)