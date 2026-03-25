
# Fix script to correct make_subplots parameter
with open('Algorithmic_Trading_Strategy.ipynb', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the incorrect parameter
content = content.replace('rows=1, col=2,', 'rows=1, cols=2,')

with open('Algorithmic_Trading_Strategy.ipynb', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed: col=2 changed to cols=2")

