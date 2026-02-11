# Awesome-Object-Counting

A curated list of resources for object counting in computer vision, with a focus on few-shot, zero-shot, and multimodal (image-text) approaches. This includes key papers, datasets, and code repositories. Object counting involves estimating the number of instances of a specific class in an image, often in dense or sparse scenes. While traditional methods rely on large labeled datasets, advanced techniques like few-shot and zero-shot enable generalization to novel classes with minimal or no examples.

This list draws from recent advancements in class-agnostic counting, where models handle arbitrary object categories without retraining.

## Datasets

| Dataset  | Describe                                                     | Download                                                     |
| -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| FSC147   | FSC-147 is a benchmark dataset for few-shot object counting that requires models to estimate the number of target instances in an image given only a few exemplar bounding boxes, with train and test categories being disjoint to evaluate cross-category generalization. | https://github.com/cvlab-stonybrook/LearningToCountEverything |
| FSC147-D | It provides a more consistent and fair benchmark for density-regression-based counting models, reducing ambiguity in density map generation that existed in earlier FSC-147 implementations. | https://github.com/niki-amini-naieni/countx                  |
| REC-8K   | REC-8K images are selected from below datasets and partially collected from the internet for diverse scenes and object attributes. Due to the restriction of the original dataset license, we provide the original download links for the datasets. | https://github.com/sydai/referring-expression-counting       |



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

### Datasets
- **FSC-147**: Commonly used for zero-shot evaluation due to its class diversity.
- **CARPK**: Adapted for zero-shot vehicle counting benchmarks.

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
- **Awesome-Class-Agnostic-Counting** (RaccoonDML): Paper list and comparisons for class-agnostic counting.
- **Awesome-Few-Shot-Counting** (Tracyummy): Focused on few-shot class-agnostic counting.
- **Counting-DETR** (VinAIResearch): Implementation for few-shot counting and detection (ECCV 2022).
- **VA-Count** (HopooLinZ): Zero-shot counting with exemplar enhancement (ECCV 2024).
- **Awesome-Crowd-Counting** (gjy3035): Broader crowd/object counting resources, including code for C^3 Framework.
