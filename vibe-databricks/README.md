# 🪩 Vibe Databricks - MLOps Pipeline Generator

Deploy end-to-end ML pipelines to Databricks using AI assistants (Claude/Cursor) with MCP (Model Context Protocol).

**Just describe what you want → AI builds & deploys the complete MLOps pipeline.**

---

## 🎯 What This Does

This template enables AI assistants to:
- ✅ Create Databricks Asset Bundles (DABs) projects
- ✅ Set up CI/CD with GitHub Actions
- ✅ Deploy to multiple environments (dev/staging/prod)
- ✅ Train ML models with hyperparameter optimization
- ✅ Register models to Unity Catalog
- ✅ All from natural language prompts!

---

## 🚀 Quick Start

### 1. Clone This Repository

```bash
git clone https://github.com/<your-org>/vibe-databricks.git
cd vibe-databricks
```

### 2. Configure MCP Servers

Add the following to your MCP configuration:

**For Cursor** (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "github": {
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer <YOUR_GITHUB_TOKEN>"
      }
    },
    "databricks": {
      "type": "streamable-http",
      "url": "https://<YOUR_WORKSPACE>.cloud.databricks.com/api/2.0/mcp/functions/<CATALOG>/<SCHEMA>",
      "headers": {
        "Authorization": "Bearer <YOUR_DATABRICKS_PAT>"
      }
    }
  }
}
```

**For Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "github": {
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer <YOUR_GITHUB_TOKEN>"
      }
    }
  }
}
```

### 3. Prepare Your Credentials

You'll need:
- **Databricks Workspace URL**: `https://dbc-xxxxx.cloud.databricks.com`
- **Databricks PAT Token**: Generate from User Settings → Developer → Access Tokens
- **Unity Catalog Name**: e.g., `my_catalog`
- **GitHub Repository**: Where to push the generated project

### 4. Open in Your AI Client

Open this folder in Cursor or add it to Claude Desktop, then start chatting!

---

## 💬 Example Prompt

Copy and paste this prompt to get started:

```
Please use cluster ID <YOUR_CLUSTER_ID> to create the context and do your work. 
Follow the rules in the claude.md file.

The task is to train a model on the Titanic dataset:
- Create a new schema in which we will log everything
- Download the data and save in a Delta table
- Do descriptive statistics and EDA
- Build a training pipeline with hyperparameter optimization
- Deploy the model as a serving endpoint
- Set up MLflow experiment logging
- Create a CI/CD pipeline as described in the claude.md file

Configuration:
- Catalog to use: <YOUR_CATALOG>
- Databricks workspace: <YOUR_WORKSPACE_URL>
- GitHub repo: <YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>

Please start by checking the available MCP servers and let me know if you can use them.
```

**Replace the placeholders:**
- `<YOUR_CLUSTER_ID>` - Your Databricks cluster ID (e.g., `1124-191600-6iri9ssy`)
- `<YOUR_CATALOG>` - Your Unity Catalog name (e.g., `my_mlops_catalog`)
- `<YOUR_WORKSPACE_URL>` - Your Databricks workspace URL
- `<YOUR_GITHUB_USERNAME>` - Your GitHub username
- `<YOUR_REPO_NAME>` - Name for the new repository

---

## 🔐 GitHub Secrets Setup

After the AI creates your GitHub repository, add these secrets:

1. Go to: `https://github.com/<owner>/<repo>/settings/secrets/actions`
2. Add:

| Secret Name | Value |
|-------------|-------|
| `DATABRICKS_HOST` | `https://dbc-xxxxx.cloud.databricks.com` |
| `DATABRICKS_TOKEN` | `dapi...` (your PAT token) |

---

## 📁 What Gets Generated

The AI will create a complete MLOps project:

```
your-mlops-project/
├── databricks.yml              # DABs configuration
├── requirements.txt            # Python dependencies
├── resources/
│   └── training_job.yml        # Databricks job definition
├── config/
│   ├── dev.yaml               # Dev environment config
│   ├── staging.yaml           # Staging config
│   └── prod.yaml              # Production config
├── src/<project>/
│   ├── training/
│   │   ├── feature_engineering.py
│   │   └── train.py
│   └── validation/
│       └── validate_model.py
├── tests/
│   └── test_config.py
└── .github/workflows/
    └── ci.yml                  # CI/CD pipeline
```

---

## 🌟 Features

| Feature | Description |
|---------|-------------|
| **Multi-Environment** | Automatic dev/staging/prod deployments |
| **Unity Catalog** | Models registered to UC for governance |
| **MLflow Tracking** | Experiment tracking and model versioning |
| **Serverless Support** | Works with serverless compute |
| **GitHub Actions CI/CD** | Automated validation and deployment |
| **Hyperparameter Tuning** | Built-in Hyperopt optimization |

---

## 🛠️ Troubleshooting

### IP ACL Errors
If you see "Source IP address is blocked", your workspace has IP restrictions. Options:
1. Add GitHub Actions IP ranges to your workspace IP Access List
2. Use a self-hosted GitHub runner

---

## 📚 Resources

- [Databricks Asset Bundles](https://docs.databricks.com/dev-tools/bundles/index.html)
- [MLOps Deployment Patterns](https://docs.databricks.com/aws/en/machine-learning/mlops/deployment-patterns)
- [MCP Specification](https://modelcontextprotocol.io/)
- [GitHub Actions for Databricks](https://github.com/databricks/setup-cli)

---

## 🤝 Contributing

PRs welcome! Please follow the patterns in `claude.md` for consistency.

---

## 📄 License

MIT License - feel free to use this template for your projects!
