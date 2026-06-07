# Evaluation

The Evaluator Agent scores generated outputs from 0 to 100 on:

| Dimension | Meaning |
| --- | --- |
| Factuality | Are claims grounded in source-backed checks? |
| Relevance | Does the output answer the user topic? |
| Completeness | Are required sections, tables, figures, and formulas present? |
| Structure | Is the report organized like an academic paper? |
| Citation quality | Are major claims linked to citations? |
| Clarity | Is the writing understandable and professional? |
| Visual quality | Are diagrams and charts generated and useful? |
| Reproducibility | Can the demo run without paid keys? |

The aggregate score is an average in the current implementation. The final LaTeX report also documents:

```latex
Q = \alpha F + \beta R + \gamma S + \delta C
```

where `F` is factuality, `R` is relevance, `S` is structure, and `C` is citation quality. Future versions can expose weights in configuration.
