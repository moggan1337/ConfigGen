export class DockerGen { generate(name: string) { return `FROM node:20\nCOPY . /app\nRUN npm install\nCMD ["node", "index.js"]`; } }
export class K8sGen { generate(name: string) { return `apiVersion: v1\nkind: Pod\nmetadata:\n  name: ${name}`; } }
export class GHActionsGen { generate(name: string) { return `name: CI\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest`; } }
export default { DockerGen, K8sGen, GHActionsGen };
