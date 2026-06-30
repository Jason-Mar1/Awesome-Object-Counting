<div align="center">

# Awesome Object Counting [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

[![Pages](https://img.shields.io/badge/live-Research%20Radar-2ea44f)](https://jason-mar1.github.io/Awesome-Object-Counting/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-blue.svg)](#contributing)

</div>

This repository provides a **curated list of papers for Object Counting** —
focused on **general / class-agnostic** object counting: few-shot, zero-shot,
open-vocabulary, text-guided, training-free, referring-expression, and
foundation-model-based counting.

> Scope note: this list centers on **object counting** (counting arbitrary object
> categories). Pure crowd-counting density methods (e.g. MCNN, CSRNet, P2PNet)
> are intentionally out of scope unless they directly advance class-agnostic or
> open-vocabulary object counting.

Template inspired by [Awesome-LLM-Robotics](https://github.com/GT-RIPL/Awesome-LLM-Robotics)
and [Awesome-World-Model](https://github.com/LMD0311/Awesome-World-Model).

**Contributions are welcome!** Please feel free to submit pull requests or reach
out via email to add papers. If you find this repository useful, please consider
**giving it a star ⭐** and sharing it with others!

> Maintainers can use the included **arXiv / OpenAlex candidate pipeline** to
> discover recent papers for review, and an interactive
> **[Research Radar dashboard](https://jason-mar1.github.io/Awesome-Object-Counting/)**
> that ranks new papers, tracks SOTA, and surfaces trends.

## Overview

- [Featured / Highlighted](#featured--highlighted)
- [Foundation Papers](#foundation-papers)
- [Surveys](#surveys)
- [Benchmarks & Datasets](#benchmarks--datasets)
- [Few-Shot / Class-Agnostic Counting](#few-shot--class-agnostic-counting)
- [Zero-Shot & Open-Vocabulary Counting](#zero-shot--open-vocabulary-counting)
- [Text-Guided Counting](#text-guided-counting)
- [Referring Expression Counting](#referring-expression-counting)
- [Training-Free Counting](#training-free-counting)
- [Real-Time & Efficient Counting](#real-time--efficient-counting)
- [Foundation-Model-based Counting](#foundation-model-based-counting)
- [Research Trends](#research-trends)
- [Contributing](#contributing)
- [Citation](#citation)

> Link convention: **Method**, *Title*. `Venue Year`. [[Paper]] — `[Paper]`
> currently points to a scholar search for the title; maintainers may replace it
> with the direct arXiv / project / code link.

## Featured / Highlighted

- **RT-Counter**, *Real-Time Object Counting*. `2025`. [[Paper]](https://scholar.google.com/scholar?q=RT-Counter+real-time+object+counting)
- **MambaCount**, *Efficient Text-guided Open-vocabulary Object Counting with Spatial Sparse State Space Duality*. `2025`. [[Paper]](https://scholar.google.com/scholar?q=MambaCount+object+counting+state+space)
- **OVID**, *Text-Guided Open-Vocabulary Dense Object Counting and Localization*. `2025`. [[Paper]](https://scholar.google.com/scholar?q=OVID+open-vocabulary+dense+object+counting)

## Foundation Papers

- **GMN**, *Class-Agnostic Counting*. `ACCV 2018`. [[Paper]](https://scholar.google.com/scholar?q=Class-Agnostic+Counting+Lu+Xie+Zisserman)
- **FamNet**, *Learning To Count Everything*. `CVPR 2021`. [[Paper]](https://scholar.google.com/scholar?q=Learning+To+Count+Everything) — introduces the **FSC-147** benchmark.

## Surveys

- *A Survey on Class-Agnostic / Few-Shot Object Counting*. [[Paper]](https://scholar.google.com/scholar?q=class-agnostic+few-shot+object+counting+survey)
- *Open-Vocabulary / Vision-Language Object Counting: A Review*. [[Paper]](https://scholar.google.com/scholar?q=open-vocabulary+vision-language+object+counting+survey)

## Benchmarks & Datasets

| Dataset | Task | Metric | Link |
|---|---|---|---|
| **FSC-147** | Few-shot / class-agnostic counting (147 categories) | MAE / RMSE | [[Paper]](https://scholar.google.com/scholar?q=FSC-147+Learning+To+Count+Everything) [[Repo]](https://github.com/cvlab-stonybrook/LearningToCountEverything) |
| **FSCD-147 / FSCD-LVIS** | Few-shot counting **and detection** | AP / MAE | [[Paper]](https://scholar.google.com/scholar?q=FSCD-LVIS+few-shot+counting+detection) |
| **CountBench** | Open-vocabulary counting (text prompts) | Acc / MAE | [[Paper]](https://scholar.google.com/scholar?q=Teaching+CLIP+to+Count+to+Ten+CountBench) |
| **REC-8K** | Referring expression counting | MAE / RMSE | [[Paper]](https://scholar.google.com/scholar?q=Referring+Expression+Counting+REC-8K) |
| **CARPK** | Object (vehicle) counting from drones | MAE / RMSE | [[Paper]](https://scholar.google.com/scholar?q=CARPK+drone+car+counting+LPN) |
| **PUCPR+** | Object (vehicle) counting | MAE / RMSE | [[Paper]](https://scholar.google.com/scholar?q=PUCPR+car+counting) |

## Few-Shot / Class-Agnostic Counting

- **FamNet**, *Learning To Count Everything*. `CVPR 2021`. [[Paper]](https://scholar.google.com/scholar?q=Learning+To+Count+Everything)
- **BMNet+**, *Represent, Compare, and Learn: A Similarity-Aware Framework for Class-Agnostic Counting*. `CVPR 2022`. [[Paper]](https://scholar.google.com/scholar?q=Represent+Compare+and+Learn+class-agnostic+counting)
- **SAFECount**, *Few-shot Object Counting with Similarity-Aware Feature Enhancement*. `WACV 2023`. [[Paper]](https://scholar.google.com/scholar?q=SAFECount+Similarity-Aware+Feature+Enhancement+few-shot+counting)
- **CounTR**, *CounTR: Transformer-based Generalised Visual Counting*. `BMVC 2022`. [[Paper]](https://scholar.google.com/scholar?q=CounTR+Transformer-based+Generalised+Visual+Counting)
- **LOCA**, *A Low-Shot Object Counting Network With Iterative Prototype Adaptation*. `ICCV 2023`. [[Paper]](https://scholar.google.com/scholar?q=LOCA+Low-Shot+Object+Counting+Iterative+Prototype+Adaptation)
- **CACViT**, *Vision Transformer Off-the-Shelf: A Surprising Baseline for Few-Shot Class-Agnostic Counting*. `AAAI 2024`. [[Paper]](https://scholar.google.com/scholar?q=CACViT+Vision+Transformer+Off-the-Shelf+class-agnostic+counting)
- **DAVE**, *DAVE — A Detect-and-Verify Paradigm for Low-Shot Counting*. `CVPR 2024`. [[Paper]](https://scholar.google.com/scholar?q=DAVE+Detect-and-Verify+Paradigm+Low-Shot+Counting)

## Zero-Shot & Open-Vocabulary Counting

- **OVID**, *Text-Guided Open-Vocabulary Dense Object Counting and Localization*. `2025`. [[Paper]](https://scholar.google.com/scholar?q=OVID+open-vocabulary+dense+object+counting)
- **MambaCount**, *Efficient Text-guided Open-vocabulary Object Counting*. `2025`. [[Paper]](https://scholar.google.com/scholar?q=MambaCount+open-vocabulary+object+counting)
- **ZSC**, *Zero-Shot Object Counting*. `CVPR 2023`. [[Paper]](https://scholar.google.com/scholar?q=Zero-Shot+Object+Counting)
- **CounTX**, *Open-world Text-specified Object Counting*. `BMVC 2023`. [[Paper]](https://scholar.google.com/scholar?q=CounTX+Open-world+Text-specified+Object+Counting)
- **CountGD**, *CountGD: Multi-Modal Open-World Counting*. `NeurIPS 2024`. [[Paper]](https://scholar.google.com/scholar?q=CountGD+Multi-Modal+Open-World+Counting)
- *Teaching CLIP to Count to Ten*. `ICCV 2023`. [[Paper]](https://scholar.google.com/scholar?q=Teaching+CLIP+to+Count+to+Ten)

## Text-Guided Counting

- **CLIP-Count**, *CLIP-Count: Towards Text-Guided Zero-Shot Object Counting*. `ACM MM 2023`. [[Paper]](https://scholar.google.com/scholar?q=CLIP-Count+Text-Guided+Zero-Shot+Object+Counting)
- **CounTX**, *Open-world Text-specified Object Counting*. `BMVC 2023`. [[Paper]](https://scholar.google.com/scholar?q=CounTX+Open-world+Text-specified+Object+Counting)
- **VLCounter**, *VLCounter: Text-aware Visual Representation for Zero-Shot Object Counting*. `AAAI 2024`. [[Paper]](https://scholar.google.com/scholar?q=VLCounter+Text-aware+Visual+Representation+Zero-Shot+Object+Counting)

## Referring Expression Counting

- **GroundingREC**, *Referring Expression Counting*. `CVPR 2024`. [[Paper]](https://scholar.google.com/scholar?q=Referring+Expression+Counting+GroundingREC)
- **OVID**, *Text-Guided Open-Vocabulary Dense Object Counting and Localization*. `2025`. [[Paper]](https://scholar.google.com/scholar?q=OVID+open-vocabulary+dense+object+counting+localization)

## Training-Free Counting

- **CountingDINO**, *A Training-free Pipeline for Class-Agnostic Counting*. `2025`. [[Paper]](https://scholar.google.com/scholar?q=CountingDINO+training-free+class-agnostic+counting)
- **TFPOC**, *Training-free Object Counting with Prompts*. `WACV 2024`. [[Paper]](https://scholar.google.com/scholar?q=Training-free+Object+Counting+with+Prompts)

## Real-Time & Efficient Counting

- **RT-Counter**, *Real-Time Object Counting*. `2025`. [[Paper]](https://scholar.google.com/scholar?q=RT-Counter+real-time+object+counting)
- **MambaCount**, *Efficient Object Counting with State Space Models*. `2025`. [[Paper]](https://scholar.google.com/scholar?q=MambaCount+state+space+object+counting)

## Foundation-Model-based Counting

- **DAVE**, *Detect-and-Verify with foundation detectors*. `CVPR 2024`. [[Paper]](https://scholar.google.com/scholar?q=DAVE+Detect-and-Verify+Low-Shot+Counting)
- **CountGD**, *GroundingDINO + SAM for open-world counting*. `NeurIPS 2024`. [[Paper]](https://scholar.google.com/scholar?q=CountGD+GroundingDINO+SAM+open-world+counting)
- **GroundingREC**, *Referring Expression Counting*. `CVPR 2024`. [[Paper]](https://scholar.google.com/scholar?q=Referring+Expression+Counting+GroundingREC)

## Research Trends

Object counting is moving from category-specific models toward **general,
promptable** systems. Recent work increasingly targets **class-agnostic,
few-/zero-shot and open-vocabulary** counting, leans on **vision-language and
foundation models** (CLIP, GroundingDINO, SAM), and is now pushing on
**efficiency / real-time** inference with state-space (Mamba) designs.

See the [live Research Radar](https://jason-mar1.github.io/Awesome-Object-Counting/)
for an auto-updated view of new papers, hot topics, SOTA tracking, venues, and
the method timeline.

## Contributing

Contributions are very welcome! To add a paper, open a pull request or an issue
including:

- **Method name** and **paper title**
- **Venue and year** (e.g., `CVPR 2024`, `CVPRW 2024`, `ICLR 2025`)
- Links: `[Paper]`, and optionally `[Website]` / `[Code]`
- The most appropriate section

Please keep the focus on **object counting** (class-agnostic / open-vocabulary /
few-shot, etc.) and entries in reverse-chronological order within each section
where possible.

## Citation

If this list helps your research, please consider citing it:

```bibtex
@misc{awesome_object_counting,
  author       = {Jason-Mar1},
  title        = {Awesome Object Counting: Research Radar},
  year         = {2026},
  howpublished = {\url{https://github.com/Jason-Mar1/Awesome-Object-Counting}}
}
```

---

<div align="center">
<sub>Maintained with the Object Counting Research Radar. Star ⭐ if it helps your reading flow.</sub>
</div>
