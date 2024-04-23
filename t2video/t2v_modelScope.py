"""
Limitation - CUDA GPU is needed!
The model is:
https://huggingface.co/ali-vilab/text-to-video-ms-1.7b

By modelScope.
"""

import torch
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
from diffusers.utils import export_to_video
from dotenv import load_dotenv
import os

load_dotenv()

pipe = DiffusionPipeline.from_pretrained(os.getenv('MODEL_NAME_MODELSCOPE'), torch_dtype=torch.float16,
                                         variant=os.getenv('MODEL_VARIANT_MODELSCOPE'))
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe.enable_model_cpu_offload()

prompt = "Spider man is surfing"
# Run inference without specifying the device
video_frames = pipe(prompt, num_inference_steps=25).frames

# Set the device to CPU for processing the frames
device = torch.device('cpu')
video_frames = [frame.to(device) for frame in video_frames]

video_path = export_to_video(video_frames)
