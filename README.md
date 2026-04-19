# ConfigGen ⚙️

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Node](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0-blue.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)
![Downloads](https://img.shields.io/badge/downloads-1k%2Fmonth-orange.svg)

**ConfigGen** is a powerful configuration file generator for modern DevOps workflows. Generate production-ready Docker files, Kubernetes manifests, GitHub Actions workflows, and Terraform configurations with a single function call.

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start) • [Usage](#usage) • [API Reference](#api-reference) • [Contributing](#contributing) • [License](#license)

</div>

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Usage](#usage)
   - [Docker Generator](#docker-generator)
   - [Kubernetes Generator](#kubernetes-generator)
   - [GitHub Actions Generator](#github-actions-generator)
6. [API Reference](#api-reference)
   - [DockerGen](#dockergen)
   - [K8sGen](#k8sgen)
   - [GHActionsGen](#ghactionsgen)
7. [Configuration Options](#configuration-options)
8. [Examples](#examples)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)
12. [License](#license)

---

## Overview

ConfigGen simplifies the process of creating DevOps configuration files by providing a unified API for generating production-ready templates. Whether you're setting up a new microservice, configuring CI/CD pipelines, or deploying to Kubernetes, ConfigGen has you covered.

### Why ConfigGen?

- **🚀 Fast** - Generate configurations in milliseconds
- **📝 TypeScript Native** - Full type safety and IntelliSense support
- **🎨 Customizable** - Extensive options for every generator
- **📦 Zero Dependencies** - Lightweight with no external runtime dependencies
- **🔧 Extensible** - Easy to extend with custom generators

---

## Features

### 🐳 Docker Support

Generate production-ready Dockerfiles with:
- Multi-stage builds
- Multi-platform support (AMD64, ARM64)
- Layer caching optimization
- Health checks
- Non-root user support
- Build arguments and secrets

### ☸️ Kubernetes Support

Create Kubernetes manifests including:
- Deployments
- Services
- ConfigMaps
- Secrets
- Ingress resources
- Horizontal Pod Autoscalers
- ServiceAccounts and RBAC

### 🔄 GitHub Actions Support

Build CI/CD workflows with:
- Matrix builds
- Caching strategies
- Environment variables
- Secret management
- Artifact handling
- Deployment targets
- Pull request automation

### 📦 Terraform Support (Coming Soon)

Infrastructure as Code templates for:
- AWS resources
- Azure resources
- GCP resources
- Kubernetes deployments
- Networking configurations

---

## Installation

### Prerequisites

- Node.js >= 18.0.0
- npm, yarn, or pnpm

### Package Managers

```bash
# npm
npm install configgen

# yarn
yarn add configgen

# pnpm
pnpm add configgen
```

### From Source

```bash
git clone https://github.com/yourusername/configgen.git
cd configgen
npm install
npm run build
```

### TypeScript Setup

ConfigGen is written in TypeScript and ships with full type definitions. No additional `@types` packages are required.

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true
  }
}
```

---

## Quick Start

### Basic Usage

```typescript
import { DockerGen, K8sGen, GHActionsGen } from 'configgen';

// Generate a Dockerfile
const docker = new DockerGen();
const dockerfile = docker.generate('myapp');
console.log(dockerfile);

// Generate Kubernetes manifests
const k8s = new K8sGen();
const manifest = k8s.generate('myapp');
console.log(manifest);

// Generate GitHub Actions workflow
const actions = new GHActionsGen();
const workflow = actions.generate('ci');
console.log(workflow);
```

### CLI Usage

```bash
# Generate a Dockerfile
configgen docker myapp --output ./Dockerfile

# Generate Kubernetes manifests
configgen k8s myapp --output ./k8s/

# Generate GitHub Actions workflow
configgen actions ci --output ./.github/workflows/
```

---

## Usage

### Docker Generator

The DockerGen class generates production-ready Dockerfiles optimized for security, caching, and size.

#### Basic Example

```typescript
import { DockerGen } from 'configgen';

const docker = new DockerGen();

// Generate a basic Dockerfile
const dockerfile = docker.generate('my-node-app');
```

**Output:**
```dockerfile
FROM node:20
COPY . /app
RUN npm install
CMD ["node", "index.js"]
```

#### Advanced Example with Options

```typescript
const docker = new DockerGen({
  baseImage: 'node:20-alpine',
  multiStage: true,
  nonRoot: true,
  healthCheck: true,
  platform: 'linux/amd64'
});

const dockerfile = docker.generate('production-app', {
  installCommand: 'npm ci --only=production',
  startCommand: 'node dist/index.js',
  workingDirectory: '/app',
  env: {
    NODE_ENV: 'production',
    PORT: '3000'
  },
  ports: [3000],
  healthCheckPath: '/health'
});
```

**Output:**
```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine
WORKDIR /app
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1
CMD ["node", "dist/index.js"]
```

### Kubernetes Generator

The K8sGen class creates Kubernetes manifests following best practices for production deployments.

#### Basic Example

```typescript
import { K8sGen } from 'configgen';

const k8s = new K8sGen();

// Generate basic Pod manifest
const manifest = k8s.generate('myapp');
```

**Output:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
```

#### Deployment Example

```typescript
const k8s = new K8sGen({
  namespace: 'production',
  replicas: 3,
  resources: {
    requests: { cpu: '100m', memory: '256Mi' },
    limits: { cpu: '500m', memory: '512Mi' }
  }
});

const deployment = k8s.generateDeployment('web-app', {
  image: 'myregistry/web-app:v1.0.0',
  port: 8080,
  env: [
    { name: 'DATABASE_URL', secretRef: 'db-credentials', key: 'url' },
    { name: 'LOG_LEVEL', value: 'info' }
  ],
  serviceAccount: 'web-app-sa',
  ingress: {
    host: 'app.example.com',
    path: '/',
    tls: true
  }
});
```

**Output:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: production
  labels:
    app: web-app
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
        version: v1.0.0
    spec:
      serviceAccountName: web-app-sa
      containers:
        - name: web-app
          image: myregistry/web-app:v1.0.0
          ports:
            - containerPort: 8080
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: url
            - name: LOG_LEVEL
              value: info
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: web-app
  namespace: production
spec:
  selector:
    app: web-app
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-app
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  tls:
    - hosts:
        - app.example.com
      secretName: web-app-tls
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web-app
                port:
                  number: 80
```

### GitHub Actions Generator

The GHActionsGen class creates CI/CD workflows with modern best practices.

#### Basic Example

```typescript
import { GHActionsGen } from 'configgen';

const actions = new GHActionsGen();

// Generate CI workflow
const workflow = actions.generate('ci');
```

**Output:**
```yaml
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
```

#### Full CI/CD Pipeline Example

```typescript
const actions = new GHActionsGen({
  nodeVersion: '20',
  caching: true,
  cachingStrategy: 'npm'
});

const workflow = actions.generatePipeline('deploy', {
  triggers: ['push', 'pull_request'],
  branches: ['main', 'develop'],
  jobs: [
    {
      name: 'test',
      runsOn: 'ubuntu-latest',
      steps: [
        { name: 'Checkout', uses: 'actions/checkout@v4' },
        { name: 'Setup Node', uses: 'actions/setup-node@v4', with: { 'node-version': '20' } },
        { name: 'Cache dependencies', uses: 'actions/cache@v4', with: { 'cache': 'npm' } },
        { name: 'Install', run: 'npm ci' },
        { name: 'Lint', run: 'npm run lint' },
        { name: 'Test', run: 'npm test', with: { 'coverage': true } }
      ]
    },
    {
      name: 'build-and-push',
      runsOn: 'ubuntu-latest',
      needs: 'test',
      if: "github.ref == 'refs/heads/main'",
      steps: [
        { name: 'Checkout', uses: 'actions/checkout@v4' },
        { name: 'Login to Registry', uses: 'docker/login-action@v3', with: { 'registry': 'ghcr.io', 'username': '${{ github.actor }}', 'password': '${{ secrets.GITHUB_TOKEN }}' } },
        { name: 'Build and Push', uses: 'docker/build-push-action@v5', with: { 'push': true, 'tags': 'ghcr.io/${{ github.repository }}:${{ github.sha }}' } }
      ]
    },
    {
      name: 'deploy',
      runsOn: 'ubuntu-latest',
      needs: 'build-and-push',
      environment: 'production',
      steps: [
        { name: 'Deploy', run: 'kubectl apply -f k8s/' }
      ]
    }
  ]
});
```

---

## API Reference

### DockerGen

#### Constructor

```typescript
new DockerGen(options?: DockerOptions)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `baseImage` | `string` | `'node:20'` | Base Docker image |
| `multiStage` | `boolean` | `false` | Enable multi-stage builds |
| `nonRoot` | `boolean` | `false` | Run as non-root user |
| `healthCheck` | `boolean` | `false` | Include health check |
| `platform` | `string` | `undefined` | Target platform |

#### Methods

##### `generate(name: string, options?: DockerGenerateOptions): string`

Generates a Dockerfile.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `string` | Yes | Application name |
| `options.installCommand` | `string` | No | Package install command |
| `options.startCommand` | `string` | No | Application start command |
| `options.workingDirectory` | `string` | No | Working directory path |
| `options.env` | `Record<string, string>` | No | Environment variables |
| `options.ports` | `number[]` | No | Exposed ports |
| `options.healthCheckPath` | `string` | No | Health check endpoint |

**Returns:** `string` - Generated Dockerfile content

---

### K8sGen

#### Constructor

```typescript
new K8sGen(options?: K8sOptions)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `namespace` | `string` | `'default'` | Kubernetes namespace |
| `replicas` | `number` | `1` | Default replica count |
| `resources` | `ResourceRequirements` | `undefined` | Default resource limits |

#### Methods

##### `generate(name: string): string`

Generates a basic Pod manifest.

##### `generateDeployment(name: string, options?: DeploymentOptions): string`

Generates a complete Deployment with Service and Ingress.

**DeploymentOptions:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image` | `string` | Yes | Container image |
| `port` | `number` | No | Container port |
| `replicas` | `number` | No | Number of replicas |
| `env` | `EnvVar[]` | No | Environment variables |
| `serviceAccount` | `string` | No | Service account name |
| `ingress` | `IngressConfig` | No | Ingress configuration |
| `resources` | `ResourceRequirements` | No | Resource limits |

---

### GHActionsGen

#### Constructor

```typescript
new GHActionsGen(options?: GHActionsOptions)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `nodeVersion` | `string` | `'20'` | Node.js version |
| `caching` | `boolean` | `false` | Enable dependency caching |
| `cachingStrategy` | `'npm'` \| `'yarn'` \| `'pnpm'` | `'npm'` | Cache strategy |

#### Methods

##### `generate(name: string): string`

Generates a basic workflow.

##### `generatePipeline(name: string, options?: PipelineOptions): string`

Generates a complete CI/CD pipeline.

**PipelineOptions:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `triggers` | `string[]` | No | Event triggers |
| `branches` | `string[]` | No | Branch filters |
| `jobs` | `Job[]` | Yes | Pipeline jobs |
| `secrets` | `string[]` | No | Required secrets |

---

## Configuration Options

### DockerOptions

```typescript
interface DockerOptions {
  baseImage?: string;
  multiStage?: boolean;
  nonRoot?: boolean;
  healthCheck?: boolean;
  platform?: string;
  buildArgs?: Record<string, string>;
  labels?: Record<string, string>;
}
```

### K8sOptions

```typescript
interface K8sOptions {
  namespace?: string;
  replicas?: number;
  resources?: {
    requests?: { cpu?: string; memory?: string };
    limits?: { cpu?: string; memory?: string };
  };
  labels?: Record<string, string>;
}
```

### GHActionsOptions

```typescript
interface GHActionsOptions {
  nodeVersion?: string;
  caching?: boolean;
  cachingStrategy?: 'npm' | 'yarn' | 'pnpm';
  registry?: string;
}
```

---

## Examples

### Complete Microservice Setup

```typescript
import { DockerGen, K8sGen, GHActionsGen } from 'configgen';

const SERVICE_NAME = 'user-service';
const REGISTRY = 'gcr.io/my-project';

// Docker
const docker = new DockerGen({ 
  baseImage: 'node:20-alpine',
  multiStage: true,
  nonRoot: true,
  healthCheck: true
});

const dockerfile = docker.generate(SERVICE_NAME, {
  installCommand: 'npm ci',
  startCommand: 'node dist/server.js',
  env: { NODE_ENV: 'production' },
  ports: [3000],
  healthCheckPath: '/health'
});

// Kubernetes
const k8s = new K8sGen({
  namespace: 'production',
  replicas: 3,
  resources: {
    requests: { cpu: '100m', memory: '128Mi' },
    limits: { cpu: '500m', memory: '512Mi' }
  }
});

const manifests = k8s.generateDeployment(SERVICE_NAME, {
  image: `${REGISTRY}/${SERVICE_NAME}:latest`,
  port: 3000,
  ingress: {
    host: `${SERVICE_NAME}.example.com`,
    path: '/',
    tls: true
  }
});

// GitHub Actions
const actions = new GHActionsGen({ 
  nodeVersion: '20', 
  caching: true 
});

const workflow = actions.generatePipeline('ci-cd', {
  triggers: ['push', 'pull_request'],
  branches: ['main'],
  jobs: [
    {
      name: 'test',
      runsOn: 'ubuntu-latest',
      steps: [
        { name: 'Checkout', uses: 'actions/checkout@v4' },
        { name: 'Setup Node', uses: 'actions/setup-node@v4', with: { 'node-version': '20' } },
        { name: 'Cache', uses: 'actions/cache@v4', with: { 'cache': 'npm' } },
        { name: 'Install', run: 'npm ci' },
        { name: 'Test', run: 'npm test' }
      ]
    },
    {
      name: 'build-and-deploy',
      runsOn: 'ubuntu-latest',
      needs: 'test',
      if: "github.ref == 'refs/heads/main'",
      steps: [
        { name: 'Google Auth', uses: 'google-github-actions/auth@v2', with: { 'credentials_json': '${{ secrets.GCP_SA_KEY }}' } },
        { name: 'Setup gcloud', uses: 'google-github-actions/setup-gcloud@v2' },
        { name: 'Configure Docker', run: 'gcloud auth configure-docker' },
        { name: 'Build and Push', run: `docker build -t ${REGISTRY}/${SERVICE_NAME}:${{ github.sha }} . && docker push ${REGISTRY}/${SERVICE_NAME}:${{ github.sha }}` }
      ]
    }
  ]
});
```

---

## Best Practices

### Docker

1. **Use multi-stage builds** to reduce final image size
2. **Always specify versions** for base images (e.g., `node:20-alpine` not `node:alpine`)
3. **Use non-root users** for security
4. **Order instructions** by change frequency (least to most frequent)
5. **Add health checks** for container orchestration

### Kubernetes

1. **Set resource limits** to prevent resource exhaustion
2. **Use namespaces** for environment separation
3. **Add labels and selectors** for proper resource management
4. **Configure readiness/liveness probes** for reliability
5. **Use Ingress** with TLS for external access

### GitHub Actions

1. **Pin action versions** to specific commits or tags
2. **Use caching** to speed up workflows
3. **Separate jobs** for test, build, and deploy
4. **Protect main branch** with required reviewers
5. **Store secrets** in GitHub Secrets, never in code

---

## Troubleshooting

### Common Issues

**Q: Generated files have incorrect formatting**
A: The generators output valid YAML/Dockerfile syntax. Use `docker build --check` or `kubectl apply --dry-run` to validate.

**Q: Health check endpoint not found**
A: Ensure your application exposes the configured health check path and returns appropriate status codes.

**Q: GitHub Actions cache not working**
A: Verify that the `GITHUB_TOKEN` has the correct permissions in your repository settings.

### Debug Mode

Enable verbose output for debugging:

```typescript
import { DockerGen, K8sGen, GHActionsGen } from 'configgen';

const docker = new DockerGen({ debug: true });
const k8s = new K8sGen({ debug: true });
const actions = new GHActionsGen({ debug: true });
```

---

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/yourusername/configgen.git
cd configgen
npm install
npm run build
npm test
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**Made with ❤️ for the DevOps community**

[Back to top](#configgen-)

</div>
