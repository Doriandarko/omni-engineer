# Running Omni Engineer & Claude Engineer Inside Reproducible Daytona Workspaces

**By Huzaifa (`@khuxaiphi-stack`)** • Step-by-Step Devcontainer & Daytona Guide (`daytona/content` #36)

---

## 1. Quickstart with Daytona

```bash
daytona env set ANTHROPIC_API_KEY="sk-ant-..."
daytona env set OPENAI_API_KEY="sk-proj-..."
daytona env set TAVILY_API_KEY="tvly-..."

daytona create https://github.com/Doriandarko/omni-engineer --code
python main.py
```
