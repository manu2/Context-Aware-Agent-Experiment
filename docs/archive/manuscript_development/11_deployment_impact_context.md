# Deployment Impact Context for Manuscript Revision

**Purpose:** Sourced motivation and impact context for the paper. These sources
establish that deployment-resource contracts matter in widely used systems. They
do **not** establish production-scale savings from this repository's experiment;
the manuscript must keep that distinction explicit.

## What is already a real at-scale problem?

### 1. Containerized services and batch jobs

Kubernetes uses CPU and memory *requests* when scheduling Pods and uses limits
enforced by the runtime/kernel. Its documentation states that a container that
uses more memory than its limit can be terminated, with `OOMKilled` indicating
that it tried to exceed the limit. Thus, code that is semantically correct but
has an unsuitable peak footprint can fail after deployment or force a larger
resource request.

- [Kubernetes resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Kubernetes memory-limit example](https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/)

This is consequential at cluster scale: Borg runs hundreds of thousands of jobs
from thousands of applications across clusters with up to tens of thousands of
machines, and uses admission control, packing, and process-level isolation to
achieve utilization. The paper should cite this only as deployment context, not
as evidence that generated code currently causes a measured Borg-scale problem.

- [Verma et al., *Large-scale cluster management at Google with Borg* (EuroSys 2015)](https://research.google/pubs/large-scale-cluster-management-at-google-with-borg/)

### 2. Serverless and managed containers

Cloud Run terminates an instance that exceeds its configured memory limit; in a
service, in-flight requests then end with HTTP 500. Its documentation also gives
the capacity relationship: peak memory is standing memory plus per-request memory
times concurrency, and reducing the limit can save memory-related costs when the
workload permits it.

- [Cloud Run memory limits](https://cloud.google.com/run/docs/configuring/services/memory-limits)
- [Cloud Run container runtime contract](https://cloud.google.com/run/docs/container-contract)
- [Cloud Run pricing](https://cloud.google.com/run/pricing)

AWS Lambda similarly makes memory a production configuration choice: memory ranges
from 128 MB upward, CPU scales with the memory setting, and duration charges depend
on the configured memory. AWS explicitly recommends measuring memory and duration
to identify an appropriate setting.

- [AWS Lambda memory configuration](https://docs.aws.amazon.com/lambda/latest/dg/configuration-memory.html)
- [AWS Lambda pricing](https://aws.amazon.com/lambda/pricing/)

The direct implication is not that lower memory is always better: in Lambda,
raising memory also raises CPU, and can improve latency. The relevant opportunity
is a generated implementation that meets a known deployment contract with less
unnecessary resource use, not blindly minimizing MaxRSS.

### 3. Device- and edge-constrained software

Android's low-memory killer terminates processes under memory pressure to preserve
system performance; Android identifies elevated low-memory-killer rates as a
memory-management concern and notes user-visible effects such as slower warm
starts and reduced multitasking fluidity. This makes device-class-aware generated
code a plausible future application, but this repository does not evaluate Android
or mobile workloads.

- [Android low-memory-killer guidance](https://developer.android.com/topic/performance/vitals/lmk)

## Claims this experiment can and cannot support

### Supported

> In a controlled pairwise-distance code-generation task, providing an explicit
> RAM/time deployment contract commonly shifted sampled implementations toward
> bounded-memory techniques and lower locally observed MaxRSS. The direction and
> reliability of the shift varied by model and disclosed boundary.

### Supported practical implication

> These results motivate deployment-conditioned code generation for environments
> with explicit resource contracts, such as Kubernetes workloads, serverless
> functions, and constrained devices. A deployment system could pass its resource
> envelope to the code generator before execution rather than relying solely on
> post-failure repair.

### Not supported without a new end-to-end study

- A quantified dollar, energy, carbon, fleet-capacity, or utilization saving.
- A claim that the method reduces Cloud Run HTTP 500s, Kubernetes OOM kills, or
  Android low-memory kills in production.
- A claim about predictive-model accuracy; this benchmark measures numerical
  correctness, memory footprint, and wall time, not ML predictive accuracy.
- A guarantee that a generated program will comply with a hard runtime limit.

## Recommended manuscript placement

1. **Introduction motivation:** one concise paragraph citing Kubernetes and one
   serverless platform, followed by the Borg citation for the scale of resource
   scheduling. Do not imply a measured industry incident rate.
2. **Discussion / implications:** a short paragraph explaining that resource
   disclosure can be an input to an agent before code generation, complementing
   runtime enforcement and post-hoc profiling.
3. **Limitations:** explicitly state that production cost/reliability effects are
   downstream hypotheses, not outcomes measured here.

## Suggested manuscript wording

> Modern deployment platforms expose concrete CPU, memory, and time contracts.
> Kubernetes schedules workloads from declared resource requests and can terminate
> containers that exceed memory limits; managed-container and serverless platforms
> likewise bind execution behavior and billing to resource configuration. Our
> study asks a narrower question: when such a contract is supplied before code
> generation, does the generated implementation change in resource-relevant ways?

> The observed implementation shifts motivate deployment-conditioned code
> generation as a complement to runtime enforcement: rather than discovering a
> mismatch only after execution, an agent can receive the relevant resource envelope
> while selecting an algorithm. We do not measure production failure reduction or
> cost savings in this study.
