# Report Generation Pipeline

```mermaid
flowchart LR
                  Sources --> Claims
                  Claims --> Checks[Claim Checks]
                  Checks --> Tables
                  Tables --> Figures
                  Figures --> Markdown
                  Markdown --> PDF
                  Markdown --> Slides
```
