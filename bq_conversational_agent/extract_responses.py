import re

with open('test_output.txt', 'r') as f:
    content = f.read()

cases = content.split('\\n[')
for case in cases[1:]:
    lines = case.split('\\n')
    user_line = lines[0]
    agent_lines = [l for l in lines if l.startswith('Agent:')]
    failed_lines = [l for l in lines if l.startswith('❌ FAILED')]
    
    if failed_lines:
        print(f"[{user_line}")
        if agent_lines:
            print(f"  {agent_lines[0][:200]}...")
        print(f"  {failed_lines[0]}\\n")
