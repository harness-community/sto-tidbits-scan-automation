# STO: Scan Automation — Run Multiple Scanners in Parallel

> **Harness University Tidbit.** A 5–10 minute, self-paced micro-lesson backed by an executable repo.
> **Skill:** Run three native STO scanners — Snyk (SCA), Aqua Trivy (container), Zap (DAST) — concurrently in a parallel step group to cover all scan dimensions in one shot.

## What this skill accomplishes

- Runs three native STO scanners concurrently in the same pipeline stage using a **step group with parallel execution**
- Covers three different scan dimensions: SCA code (Snyk), container CVEs (Aqua Trivy), and DAST web app (Zap)
- Reduces total scan time — all three scanners run simultaneously instead of sequentially
- Each scanner has its own `fail_on_severity` threshold appropriate to its scan type
- All findings appear in a single **Security Tests** tab for the execution

## How it works

```
┌──────────────── Security Tests Stage ────────────────────────────────┐
│                                                                        │
│  ┌─── Step Group: Parallel Scanners (all three run simultaneously) ─┐ │
│  │                                                                    │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │ │
│  │  │   Snyk Step     │  │ AquaTrivy Step  │  │    Zap Step      │ │ │
│  │  │ type: Snyk      │  │ type: AquaTrivy │  │  type: Zap       │ │ │
│  │  │ mode: orchest.  │  │ mode: orchest.  │  │  mode: orchest.  │ │ │
│  │  │ target: repo    │  │ target: container│ │  target: instance│ │ │
│  │  │ (SCA/SAST)      │  │ (container CVEs)│  │  (DAST web app)  │ │ │
│  │  └─────────────────┘  └─────────────────┘  └──────────────────┘ │ │
│  │                                                                    │ │
│  │  ← step group ends when ALL three scanners complete →             │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  Results from all three scanners appear in Security Tests tab         │
└────────────────────────────────────────────────────────────────────────┘
```

## Scanner coverage at a glance

| Scanner | Step Type | Target | What it finds |
|---|---|---|---|
| **Snyk** | `Snyk` | Repository | Dependency vulnerabilities in open-source packages |
| **Aqua Trivy** | `AquaTrivy` | Container Image | OS and package CVEs in the container image layers |
| **Zap** | `Zap` | Instance (web app) | Runtime vulnerabilities by simulating HTTP attacks |

## Repo layout

```
sto-tidbits-scan-automation/
├── README.md
└── .harness/
    └── pipeline.yaml        ← Security stage with parallel step group
```

## Prerequisites

| Requirement | Details |
|---|---|
| Harness STO license | Required for native scan steps |
| Snyk API token | Store as a Harness text secret; used by the Snyk step for authentication |
| Running web instance | ZAP needs a live URL to scan — it does not scan code or containers |
| Docker connector | Needed only if scanning a remote container image (skip if using local image) |
| Enough build resources | Parallel steps run simultaneously — ensure your runner has enough CPU/memory |

## Steps

### 1. Create a Security Tests stage

In your pipeline, click **Add Stage** and select **Security Tests**. Set the infrastructure to **Harness Cloud** (Linux/AMD64) for the simplest setup.

### 2. Add a step group for parallel scanning

In the **Execution** tab, click **Add Step → Step Group**. Name it `Parallel Scanners`. Inside the step group, all steps added next to each other (not indented under each other) will run in parallel.

In YAML, the `parallel:` keyword inside a step group groups those steps for concurrent execution:

```yaml
- stepGroup:
    name: Parallel Scanners
    identifier: parallel_scanners
    steps:
      - parallel:
          - step:
              type: Snyk
              ...
          - step:
              type: AquaTrivy
              ...
          - step:
              type: Zap
              ...
```

### 3. Configure the Snyk step

- **Target Type**: Repository
- **Scan Configuration**: Snyk Open Source (for dependency scanning)
- **Target/Variant Detection**: Auto (detects repo name and branch from git)
- **Auth → Access Token**: `<+secrets.getValue("snyk_api_token")>`
- **Fail on Severity**: High

### 4. Configure the Aqua Trivy step

- **Target Type**: Container Image
- **Image Type**: Registry (provide a pre-built image) or Local Image (if built earlier in the pipeline)
- **Image Name/Tag**: your image repository and tag
- **Fail on Severity**: Critical

### 5. Configure the Zap step

- **Target Type**: Instance (web application)
- **Scan Configuration**: Standard (active scan) or Quick (faster, shallower)
- **Target Name**: URL of your deployed web app, e.g., `myapp.dev.internal`
- **Target Variant**: a version or environment label, e.g., `dev`
- **Instance Domain**: the base domain to scan, e.g., `https://myapp.dev.internal`
- **Instance Protocol**: https
- **Fail on Severity**: High

> ZAP needs a running application to scan. Deploy your app in an earlier stage, then run Zap in a subsequent Security stage.

### 6. Monitor resource usage

Step groups with parallel steps consume peak CPU/memory simultaneously. If your runner runs out of resources, steps fail. Increase your runner's limits or reduce parallelism as needed.

In the execution view, parallel steps show side-by-side progress — you can watch all three scanners run at the same time.

## Key concepts

| Concept | Description |
|---|---|
| **Step group** | A named container for steps inside a stage. Supports parallel execution within the group |
| **Parallel steps in a group** | Use the `parallel:` key inside the step group's `steps` list to run steps concurrently |
| **Peak resource consumption** | Parallel steps all run at once — the stage must have enough CPU/memory for all of them simultaneously |
| **Different target types** | Snyk and Trivy scan code/containers (`repository`, `container`). ZAP scans a live web app (`instance`). All results unify in the Security Tests tab |
| **Fail on severity** | Each step has its own threshold. A Critical CVE in Trivy fails, but a Medium finding in Snyk may not — configure per scanner based on your risk tolerance |
| **Deduplication** | STO deduplicates findings across scans so the same CVE reported by multiple scanners appears only once in the Security Tests view |
