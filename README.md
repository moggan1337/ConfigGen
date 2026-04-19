# ConfigGen ⚙️

**Config File Generator** - Docker, K8s, GitHub Actions.

## Features

- **🐳 Docker** - Dockerfile generation
- **☸️ Kubernetes** - K8s manifests
- **🔄 GitHub Actions** - CI/CD workflows
- **📦 Terraform** - IaC templates

## Installation

```bash
npm install configgen
```

## Usage

```typescript
import { DockerGen, K8sGen, GHActionsGen } from 'configgen';

// Docker
const docker = new DockerGen();
const dockerfile = docker.generate('myapp');

// Kubernetes
const k8s = new K8sGen();
const manifest = k8s.generate('myapp');

// GitHub Actions
const actions = new GHActionsGen();
const workflow = actions.generate('ci');
```

## Generators

| Generator | Output |
|-----------|--------|
| `DockerGen` | Dockerfile |
| `K8sGen` | K8s manifests |
| `GHActionsGen` | GitHub Actions |
| `TerraformGen` | Terraform files |

## License

MIT
