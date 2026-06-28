# Awesome-Object-Counting

A curated list of resources for object counting in computer vision, with a focus on few-shot, zero-shot, and multimodal (image-text) approaches. This includes key papers, datasets, and code repositories. Object counting involves estimating the number of instances of a specific class in an image, often in dense or sparse scenes. While traditional methods rely on large labeled datasets, advanced techniques like few-shot and zero-shot enable generalization to novel classes with minimal or no examples.

This list draws from recent advancements in class-agnostic counting, where models handle arbitrary object categories without retraining.

## Datasets

| Dataset  | Describe                                                     | Download                                                     |
| -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| FSC147   | FSC-147 is a benchmark dataset for few-shot object counting that requires models to estimate the number of target instances in an image given only a few exemplar bounding boxes, with train and test categories being disjoint to evaluate cross-category generalization. | https://github.com/cvlab-stonybrook/LearningToCountEverything |
| FSC147-D | It provides a more consistent and fair benchmark for density-regression-based counting models, reducing ambiguity in density map generation that existed in earlier FSC-147 implementations. | https://github.com/niki-amini-naieni/countx                  |
| REC-8K   | REC-8K images are selected from below datasets and partially collected from the internet for diverse scenes and object attributes. Due to the restriction of the original dataset license, we provide the original download links for the datasets. | https://github.com/sydai/referring-expression-counting       |
| CARPK    | CARPK is a large-scale car counting dataset designed for object counting in parking lot scenes, where the goal is to estimate the number of cars in aerial images. | https://lafi.github.io/LPN/                                  |

## FSC-147 Benchmark and Derivatives
FSC-147 is the central benchmark for few-shot class-agnostic object counting. It has also motivated derivative datasets and task variants, including text-specified counting, few-shot counting with detection, cleaned/reference-less counting, and robustness-oriented open-vocabulary counting.

### Dataset / Benchmark Papers
- **Learning To Count Everything** (CVPR 2021): Introduces the FSC-147 dataset and the few-shot object counting setting, where a query image and a few exemplar boxes are used to predict a density map for arbitrary categories. Code/Dataset: https://github.com/cvlab-stonybrook/LearningToCountEverything
- **Open-world Text-specified Object Counting / CounTX** (arXiv 2023): Extends FSC-147 toward text-specified open-world counting and releases FSC-147-D with richer text descriptions. Project: https://www.robots.ox.ac.uk/~vgg/research/countx
- **Few-shot Object Counting and Detection / Counting-DETR** (ECCV 2022): Extends counting into joint counting-and-detection with FSCD-147 and FSCD-LVIS, using pseudo boxes and an uncertainty-aware DETR-style detector. Code: https://github.com/VinAIResearch/Counting-DETR
- **Learning to Count Anything** (arXiv 2022): Studies reference-less class-agnostic counting and proposes FSC-133, a cleaned variant that removes errors, ambiguities, and duplicate images from FSC-147.
- **A Survey on Class-Agnostic Counting** (arXiv 2025): Summarizes reference-based, reference-less, and open-world text-guided counting methods and reports a leaderboard on FSC-147 and CARPK.

### Representative FSC-147 Methods
- **FamNet / Learning To Count Everything** (CVPR 2021): Early density-regression baseline for exemplar-guided few-shot counting on FSC-147.
- **SAFECount: Few-shot Object Counting with Similarity-Aware Feature Enhancement** (arXiv 2022): Improves exemplar-query matching with similarity comparison and feature enhancement. Code: https://github.com/zhiyuanyou/SAFECount
- **CounTR: Transformer-based Generalised Visual Counting** (BMVC 2022): Uses a transformer architecture for generalized visual counting across zero-shot and few-shot settings.
- **LOCA: A Low-Shot Object Counting Network With Iterative Prototype Adaptation** (arXiv 2022): Iteratively adapts object prototypes by fusing exemplar shape/appearance with image features; supports both few-shot and no-shot settings.
- **CACViT: Vision Transformer Off-the-Shelf** (arXiv 2023): Shows that class-agnostic counting can be simplified with a plain pretrained ViT, using scale and magnitude embeddings.
- **Learning Spatial Similarity Distribution for Few-shot Object Counting / SSD** (arXiv 2024): Learns 4D spatial similarity distributions between exemplar and query features for stronger FSC-147/CARPK performance. Code: https://github.com/CBalance/SSD


## Few-Shot Object Counting
Few-shot object counting uses a small number of exemplars (e.g., 1-5 bounding boxes or images) to count objects of a novel class in a query image.

### Papers
- **Few-shot Object Counting and Detection** (ECCV 2022): Introduces a DETR-based model for counting and detecting with few exemplars.
- **Class-Agnostic Few-Shot Object Counting** (WACV 2021): Proposes CFOCNet for counting arbitrary classes with few shots.
- **Few-Shot Object Counting with Frequency Attention and Multi-Perception Head** (2025): Addresses feature degradation and multi-scale fusion in few-shot scenarios.
- **Few-Shot Object Counting Model Based on Self-Support Matching and Attention Mechanism** (2024): Combines self-support matching for improved few-shot accuracy.
- **Learning Spatial Similarity Distribution for Few-Shot Object Counting** (arXiv 2024): Focuses on spatial similarity for better generalization.
- **Few-Shot Object Counting With Similarity-Aware Feature Enhancement** (WACV 2023): Enhances features using similarity awareness.
- **A Lightweight Few-Shot Object Counting Method Based on Similarity Matching** (2025): Emphasizes efficiency in few-shot settings.
- **CounTR: Transformer-based Generalised Visual Counting** (BMVC 2022): Uses transformers for few-shot counting.
- **Accurate Few-Shot Object Counting with Hough Matching Feature Enhancement** (2023): Incorporates Hough transforms for precision.

### Datasets
- **FSC-147** (Few-Shot Counting-147): 6,135 images across 147 classes, with varying object densities. Primary benchmark for few-shot counting; includes train/val/test splits.
- **CARPK** (Car Parking Lot Dataset): Drone-captured images for vehicle counting, useful for few-shot evaluation.
- **MS COCO** (Microsoft Common Objects in Context): Adapted for few-shot counting tasks, with 330K images and 80 classes.
- **FSOD** (Few-Shot Object Detection Dataset): Extension of COCO/PASCAL VOC for detection, often used in counting pipelines.

## Zero-Shot Object Counting
Zero-shot counting relies only on class names (text prompts) without exemplars or training on the target class.

### Papers
- **Zero-Shot Object Counting** (CVPR 2023): Defines the ZSC task and proposes a model using class names only.
- **Zero-Shot Object Counting with Good Exemplars** (ECCV 2024): Improves exemplars via patch selection for better zero-shot performance.
- **Enhancing Zero-Shot Object Counting via Text-Guided Local Ranking and Number-Evoked Global Attention** (ICCV 2025): Uses VLMs for text-guided counting.
- **Zero-Shot Object Counting with Visual Feature Extraction and Language-Guidance** (2025): Focuses on language-guided feature extraction.
- **SAVE: Self-Attention on Visual Embedding for Zero-Shot Generic Object Counting** (2025): Outperforms zero/few-shot methods on FSC-147.
- **Towards Zero-Shot Object Counting via Deep Spatial Prior Cross-Modality Fusion** (2024): Uses DSPI network for multimodal alignment.
- **CLIP-Count: Towards Text-Guided Zero-Shot Object Counting** (ACM MM 2023): End-to-end pipeline using CLIP for zero-shot density maps.
- **Text Instructed Zero-Shot Object Counting with Spatial Prior Guidance Network** (2025): Extracts spatial positions from text.
- **Zero-Shot Improvement of Object Counting with CLIP** (NeurIPS 2023): Enhances CLIP's text embedding for better counting.
- **Expanding Zero-Shot Object Counting with Rich Prompts** (arXiv 2025): Refines text prompts for improved alignment.


## Text-Guided Open-Vocabulary Object Counting
Text-guided open-vocabulary object counting uses natural-language descriptions to specify target categories and aims to count arbitrary objects without a fixed closed-set label space.

### Papers
- **OVID: Open-Vocabulary Image-text Dense Framework for Counting and Localization** (ICASSP 2026): A unified image-text dense framework for text-guided object counting and point-level localization, built around multi-modal fusion and direct point prediction. Code: https://github.com/Jason-Mar1/OVID
- **MambaCount: Efficient Text-guided Open-vocabulary Object Counting with Spatial Sparse State Space Duality Block** (arXiv 2026): Introduces a Mamba-based efficient TOOC framework with Spatial Sparse State Space Duality (S^4D), Spatial Token Selection, and Multi-Granularity Prototypes; reports strong FSC-147 performance with linear complexity. Paper: https://arxiv.org/abs/2606.17650
- **RT-Counter: Real-Time Text-Guided Open-Vocabulary Object Counting** (arXiv 2026): A real-time TOOC framework using Visual Prototype Textualization and Weaving Transformer layers to improve the accuracy-speed trade-off; reports 112.48 FPS and competitive FSC-147 accuracy. Paper: https://arxiv.org/abs/2606.17561 Code: https://github.com/Jason-Mar1/RT-Counter
- **Test-Time Training for Robust Text-Guided Open-Vocabulary Object Counting** (arXiv 2026): Introduces Robust-TOOC and Dual-TTT for evaluating and improving TOOC under corruptions such as rain, fog, darkness, Gaussian noise, salt-and-pepper noise, and mixed corruption. Paper: https://arxiv.org/abs/2606.17601

## Multimodal Image-Text Object Counting
This category involves counting using both image and text modalities, often leveraging VLMs like CLIP for text-guided counting.

### Papers
- **CLIP-Count: Towards Text-Guided Zero-Shot Object Counting** (ACM MM 2023): Uses CLIP for multimodal zero-shot counting.
- **YOLO-Count: Differentiable Object Counting for Text-to-Image Generation** (ICCV 2025): Integrates counting into T2I with text prompts.
- **Towards Zero-Shot Object Counting via Deep Spatial Prior Cross-Modality Fusion** (2024): Fuses image and text with spatial priors.
- **CountGD: Multi-Modal Open-World Counting** (2023): Handles text and visual examples for multimodal counting.
- **CODNet: Context-Based Object Detection Network for Multimodal Image Captioning and Virtual Question Answering** (2025): Uses YOLOv6 for object detection in multimodal tasks.

### Datasets
- **MS COCO**: 330K images with captions and objects; ideal for image-text multimodal counting.
- **Flickr30K Entities**: 30K images with entity-linked captions for region-to-phrase correspondences.
- **WIT (Wikipedia-based Image Text Dataset)**: 37.5M image-text pairs across 108 languages.
- **Entity Image and Mixed-Modal Image Retrieval Datasets** (arXiv 2025): Includes EI and MMIR for entity-rich multimodal retrieval.
- **FSC-147**: Often extended with text prompts for multimodal evaluation.

## Code Repositories
- **OVID** (Jason-Mar1): Open-vocabulary image-text dense framework for counting and localization. https://github.com/Jason-Mar1/OVID
- **RT-Counter** (Jason-Mar1): Real-time text-guided open-vocabulary object counting. https://github.com/Jason-Mar1/RT-Counter
- **LearningToCountEverything / FSC-147** (cvlab-stonybrook): Original FSC-147 dataset and FamNet baseline. https://github.com/cvlab-stonybrook/LearningToCountEverything
- **SAFECount** (zhiyuanyou): Similarity-aware feature enhancement for few-shot object counting. https://github.com/zhiyuanyou/SAFECount
- **SSD** (CBalance): Spatial Similarity Distribution for few-shot object counting. https://github.com/CBalance/SSD
- **CounTX** (VGG): Text-specified open-world object counting and FSC-147-D. https://www.robots.ox.ac.uk/~vgg/research/countx
- **Awesome-Class-Agnostic-Counting** (RaccoonDML): Paper list and comparisons for class-agnostic counting.
- **Awesome-Few-Shot-Counting** (Tracyummy): Focused on few-shot class-agnostic counting.
- **Counting-DETR** (VinAIResearch): Implementation for few-shot counting and detection (ECCV 2022).
- **VA-Count** (HopooLinZ): Zero-shot counting with exemplar enhancement (ECCV 2024).
- **Awesome-Crowd-Counting** (gjy3035): Broader crowd/object counting resources, including code for C^3 Framework.

## Automated Paper Updates

This repository includes an automated paper radar for object-counting research. The workflow searches arXiv and OpenAlex every day, deduplicates papers, writes machine-readable files under `data/`, and refreshes the generated section below.

See [`docs/automation.md`](docs/automation.md) for setup and maintenance notes.

<!-- AUTO_PAPERS:START -->
## Latest Auto-Discovered Papers

This section will be updated automatically from arXiv and OpenAlex. After merging the automation PR, add `OPENALEX_API_KEY` as a GitHub Actions secret and run **Update object-counting papers** once from the Actions tab.
<!-- AUTO_PAPERS:END -->
