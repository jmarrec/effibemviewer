---
hide:
  - toc
  - navigation
---

```python exec="true" html="true"
from effibemviewer import generate_loader_html

html_content = generate_loader_html(
    include_geometry_diagnostics=True,
    embedded=False,
    cdn=True,
    script_only=True,
)
print(html_content)
```
