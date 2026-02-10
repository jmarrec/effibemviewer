---
hide:
  - toc
  - navigation
---

```python exec="true" html="true"
from effibemviewer import generate_loader_html

print("""\
<style>
/* Hide the auto-generated page title (the loader prompt has its own) */
.md-typeset > h1:first-child {
  display: none;
}
</style>
""")

html_content = generate_loader_html(
    height="70vh",
    include_geometry_diagnostics=True,
    embedded=False,
    cdn=True,
    script_only=True,
)
print(html_content)
```
