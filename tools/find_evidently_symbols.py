import importlib
import pathlib
import re

pkg = importlib.import_module('evidently')
root = pathlib.Path(pkg.__file__).parent
print('evidently root:', root)

patterns = ['Dashboard', 'DataDriftTab', 'DataDriftProfileSection', 'DataDrift', 'Dashboard(']
matches = []
for fp in sorted(root.rglob('*.py')):
    try:
        s = fp.read_text(errors='ignore')
    except Exception:
        continue
    for p in patterns:
        if p in s:
            matches.append((fp.relative_to(root), p))

# print summary grouped by file
from collections import defaultdict
byfile = defaultdict(list)
for f,p in matches:
    byfile[str(f)].append(p)

for f,ps in byfile.items():
    print(f, ':', sorted(set(ps)))

# also print possible import paths where symbols are defined as names
print('\nModules that export Dashboard/DataDriftTab as attributes:')
for mod in pkg.__path__:
    pass
# scan package for assignments like Dashboard =
for fp in sorted(root.rglob('*.py')):
    try:
        s = fp.read_text(errors='ignore')
    except Exception:
        continue
    if re.search(r"\bclass\s+Dashboard\b", s) or re.search(r"\bclass\s+DataDriftTab\b", s):
        print('class defined in', fp.relative_to(root))
    if re.search(r"\bdef\s+create_dashboard\b", s):
        print('factory create_dashboard in', fp.relative_to(root))

print('\nDone')
