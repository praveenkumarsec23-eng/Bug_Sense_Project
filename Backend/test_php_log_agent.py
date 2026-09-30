from agents.log_analysis_agent import run_log_analysis_agent

code = """<?php

class User {
    public $name = "Praveen";
}

function printUserName($user) {
    echo $user->name;
}

$user = null;
printUserName($user);

?>
"""

result = run_log_analysis_agent(
    code=code,
    language="php"
)

print(result)