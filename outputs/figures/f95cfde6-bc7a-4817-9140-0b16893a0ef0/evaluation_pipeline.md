# Evaluation Pipeline

```mermaid
flowchart LR
                  Report --> Rubric
                  Figures --> Rubric
                  Citations --> Rubric
                  Rubric --> JSON
                  Rubric --> Markdown
                  JSON --> Threshold{Pass?}
                  Threshold -->|No| Revision
                  Threshold -->|Yes| Presentation
```
