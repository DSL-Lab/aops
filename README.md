<div align="center">
  <h1>Leveraging Online Olympiad-Level Math Problems for LLMs Training and Contamination-Resistant Evaluation</h1>
  <p>
  <a href="https://livemathbench.github.io/">Project Website</a> |
  <a href="https://arxiv.org/pdf/2501.14275">📝Paper</a> |
  <a href="https://huggingface.co/datasets/jojo23333/LiveAoPSBench-2024">📐LiveAopsBench</a>  |
  <a href="https://huggingface.co/datasets/DeepStudentLlama/AoPS-Instruct">📊AoPS-Ins (Third party)</a> 
  </p>
</div>

<!-- # Leveraging Online Olympiad-Level Math Problems for LLMs Training and Contamination-Resistant Evaluation -->

This repository contains the code and instructions for reproducing the data collection and processing pipeline described in our paper "Leveraging Online Olympiad-Level Math Problems for LLMs Training and Contamination-Resistant Evaluation".

## Environment Setup
To install the required dependencies:
```bash
pip install -r requirements.txt
```
By default, we use a setup of 4xA100 GPU with 80GB memory each.

## Data Collection

To construct the `AoPS-Instruct` dataset:

1. To crawl the data, run the following script:
   ```bash
   bash scripts/crawl_raw.sh
   ```
   This will produce a raw jsonlines file: out/items_raw.jl to be processed in the next steps.

   Note: To perform a test run to make sure the whole pipeline is working, in the crawling script, you can add the `test_mode` option to crawl only 1000 datapoints:
   ```bash
   bash scripts/crawl_raw.sh --test_mode True
   ```
   Then, you can run the rest of the pipeline to make sure everything is runnable before running a larger script file. Make sure to delete the entire test-run folder `./out` before rerunning the pipeline since the pipeline is designed to resume unless the entire folder is removed.


2. Modify and run the reproduction script:
   - `WORKDIR`: The working directory for the script.
   - `NUM_GPUS`: The number of GPUS to use for parsing models. This variable should be an even number. Ensure that the `CUDA_VISIBLE_DEVICES` is set correctly. We assume 80GB A100/H100 is used and a minimum of 2 GPUs are needed.
   - `ITEMS_RAW_PATH`: The path to raw crawled data (from step 2).
   - Optionally change the parsing and rewriting models (default is Qwen 2.5 models).

   Then run 
   ```bash
   bash scripts/reproduce.sh
   ```

   This will process the raw crawled data and create the final training dataset in the specified format. The script supports resuming, so if interrupted, it will pick up where it left off.

## Processed Data
We provide the full code for reproducing AoPS-Ins and LiveAoPSBench, making it easy for you to explore and experiment with these tools. Processed data is also available through a third-party effort, accessible on Hugging Face: Hugging Face Dataset. Please note that we disclaim any liability for the use of this third-party dataset. Processed data is available thanks to a community reproduction effort, accessible here: [Hugging Face Dataset](https://huggingface.co/datasets/DeepStudentLlama/AoPS-Instruct). We disclaim any liability for the use of this third-party dataset.

## Evaluation Code

To run evaluation on the LiveAoPS Bench, please refer to `eval` directory.

## Questions/Issues

Please submit a GitHub issue if you have any questions or find any bugs.

## Citation

If you use this code or dataset in your research, please cite our paper:

```bibtex
@misc{aopsdataset,
      title={Leveraging Online Olympiad-Level Math Problems for LLMs Training and Contamination-Resistant Evaluation}, 
      author={Sadegh Mahdavi and Muchen Li and Kaiwen Liu and Christos Thrampoulidis and Leonid Sigal and Renjie Liao},
      year={2025},
      eprint={2501.14275},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2501.14275}, 
}
```
