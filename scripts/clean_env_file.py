import re
import sys

# Read the .env file
with open(sys.argv[1], 'r') as f:
    content = f.read()

# Replacement patterns
replacements = [
    (r'OPENROUTER_API_KEY=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', 
     'OPENROUTER_API_KEY=your-openrouter-api-key-here'),
    (r'DEEPL_API_KEY=cb214565-7929-4c70-ad90-5114ab911947:fx', 
     'DEEPL_API_KEY=your-deepl-api-key-here'),
    (r'NEO4J_PASSWORD=JbAl2SE5yvUavfe\+D3zgzgtgd50Lgn2oAimCCKmdRoc=', 
     'NEO4J_PASSWORD=your-neo4j-password-here'),
    (r'BLABLADOR_API_KEY=glpat-fDjk32726TKmAqFHwsujkG86MQp1Omdqbgk\.01\.0z0slgkdx', 
     'BLABLADOR_API_KEY=your-blablador-api-key-here'),
    (r'WEBUI_SECRET_KEY=gCyd2f3umFIvmwcvBvS87XZ0Ia6WBZRQMN55ure9MQ4=', 
     'WEBUI_SECRET_KEY=your-webui-secret-key-here'),
    (r'OPENWEBUI_API_KEY=P3N\+/ejMOP4fkqQt8CC2y88vvvVUAjzCVW3a8ssDnZo=', 
     'OPENWEBUI_API_KEY=your-openwebui-api-key-here'),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Write back
with open(sys.argv[1], 'w') as f:
    f.write(content)
