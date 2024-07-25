"""
This file is used to create the config file before fine tune the voice model.
Before running the script, you need to make sure that all the paths that are requested exist in the
directories you've mentioned in the flags.
To run the script, type in the command line:

    python create_config_file --output_path <OUTPUT_PATH> \
                          --dataset_name <DATASET_NAME> \
                          --dataset_path <DATASET_PATH> \
                          --name <CONFIG_FILENAME> (OPTIONAL)
"""

import argparse
import json
import os

current_directory = os.getcwd()
config = {
    "output_path": "output",
    "logger_uri": None,
    "run_name": "run",
    "project_name": None,
    "run_description": "\ud83d\udc38Coqui trainer run.",
    "print_step": 25,
    "plot_step": 100,
    "model_param_stats": False,
    "wandb_entity": None,
    "dashboard_logger": "tensorboard",
    "save_on_interrupt": True,
    "log_model_step": None,
    "save_step": 10000,
    "save_n_checkpoints": 5,
    "save_checkpoints": True,
    "save_all_best": False,
    "save_best_after": 10000,
    "target_loss": None,
    "print_eval": False,
    "test_delay_epochs": 0,
    "run_eval": True,
    "run_eval_steps": None,
    "distributed_backend": "nccl",
    "distributed_url": "tcp://localhost:54321",
    "mixed_precision": False,
    "precision": "fp16",
    "epochs": 1000,
    "batch_size": 32,
    "eval_batch_size": 16,
    "grad_clip": 0.0,
    "scheduler_after_epoch": True,
    "lr": 0.001,
    "optimizer": "radam",
    "optimizer_params": None,
    "lr_scheduler": None,
    "lr_scheduler_params": {},
    "use_grad_scaler": False,
    "allow_tf32": False,
    "cudnn_enable": True,
    "cudnn_deterministic": False,
    "cudnn_benchmark": False,
    "training_seed": 54321,
    "model": "xtts",
    "num_loader_workers": 0,
    "num_eval_loader_workers": 0,
    "use_noise_augment": False,
    "audio": {
        "sample_rate": 22050,
        "output_sample_rate": 24000
    },
    "use_phonemes": False,
    "phonemizer": None,
    "phoneme_language": None,
    "compute_input_seq_cache": False,
    "text_cleaner": None,
    "enable_eos_bos_chars": False,
    "test_sentences_file": "",
    "phoneme_cache_path": None,
    "characters": None,
    "add_blank": False,
    "batch_group_size": 0,
    "loss_masking": None,
    "min_audio_len": 1,
    "max_audio_len": float('inf'),
    "min_text_len": 1,
    "max_text_len": float('inf'),
    "compute_f0": False,
    "compute_energy": False,
    "compute_linear_spec": False,
    "precompute_num_workers": 0,
    "start_by_longest": False,
    "shuffle": False,
    "drop_last": False,
    "datasets": [
        {
            "formatter": "ljspeech",
            "dataset_name": "",
            "path": "",
            "meta_file_train": "",
            "ignored_speakers": None,
            "language": "en",
            "phonemizer": "",
            "meta_file_val": "",
            "meta_file_attn_mask": ""
        }
    ],
    "test_sentences": [],
    "eval_split_max_size": None,
    "eval_split_size": 0.01,
    "use_speaker_weighted_sampler": False,
    "speaker_weighted_sampler_alpha": 1.0,
    "use_language_weighted_sampler": False,
    "language_weighted_sampler_alpha": 1.0,
    "use_length_weighted_sampler": False,
    "length_weighted_sampler_alpha": 1.0,
    "model_args": {
        "gpt_batch_size": 1,
        "enable_redaction": False,
        "kv_cache": True,
        "gpt_checkpoint": None,
        "clvp_checkpoint": None,
        "decoder_checkpoint": None,
        "num_chars": 255,
        "tokenizer_file": "",
        "gpt_max_audio_tokens": 605,
        "gpt_max_text_tokens": 402,
        "gpt_max_prompt_tokens": 70,
        "gpt_layers": 30,
        "gpt_n_model_channels": 1024,
        "gpt_n_heads": 16,
        "gpt_number_text_tokens": 6681,
        "gpt_start_text_token": None,
        "gpt_stop_text_token": None,
        "gpt_num_audio_tokens": 1026,
        "gpt_start_audio_token": 1024,
        "gpt_stop_audio_token": 1025,
        "gpt_code_stride_len": 1024,
        "gpt_use_masking_gt_prompt_approach": True,
        "gpt_use_perceiver_resampler": True,
        "input_sample_rate": 22050,
        "output_sample_rate": 24000,
        "output_hop_length": 256,
        "decoder_input_dim": 1024,
        "d_vector_dim": 512,
        "cond_d_vector_in_each_upsampling_layer": True,
        "duration_const": 102400
    },
    "model_dir": None,
    "languages": [
        "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "hu", "ko", "ja", "hi"
    ],
    "temperature": 0.75,
    "length_penalty": 1.0,
    "repetition_penalty": 5.0,
    "top_k": 50,
    "top_p": 0.85,
    "num_gpt_outputs": 1,
    "gpt_cond_len": 30,
    "gpt_cond_chunk_len": 4,
    "max_ref_len": 30,
    "sound_norm_refs": False
}


def validate_path(output_path, dataset_name, dataset_path):
    output_path_exist = os.path.exists(output_path) and os.path.isdir(output_path)
    dataset_exist = os.path.exists(dataset_path) and os.path.isdir(dataset_path)
    is_dataset_exist = os.path.exists(os.path.join(dataset_path, dataset_name))
    return output_path_exist and dataset_exist and is_dataset_exist


def create_json(output_path, dataset_name, dataset_path, name=None):
    if validate_path(output_path, dataset_name, dataset_path):
        config["output_path"] = output_path
        config["datasets"][0]["dataset_name"] = dataset_name
        config["datasets"][0]["path"] = dataset_path

        config_filename = name if name else 'config.json'
        with open(config_filename, 'w') as json_file:
            json.dump(config, json_file, indent=4)
    else:
        print("Failed creating the config file. Check your paths before running the script again.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate config.json file.')
    parser.add_argument('--output_path', type=str, required=True, help='Output path for the config.')
    parser.add_argument('--dataset_name', type=str, required=True, help='Name of the dataset.')
    parser.add_argument('--dataset_path', type=str, required=True, help='Path to the dataset.')
    parser.add_argument('--name', type=str, required=False,
                        help="The name of the generated file, default is config.json")
    args = parser.parse_args()
    output_path_ = os.path.join(current_directory, args.output_path)
    dataset_path_ = os.path.join(current_directory, args.dataset_path)
    name_ = args.name if args.name else None
    create_json(output_path_, args.dataset_name, dataset_path_, name_)
