"""Zero Scope model for text to video generation.
Link:
   https://huggingface.co/cerspense/zeroscope_v2_576w
"""

import torch
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
from diffusers.utils import export_to_video
from dotenv import load_dotenv
import os

load_dotenv()

pipe = DiffusionPipeline.from_pretrained(os.getenv('ZERO_SCOPE_MODEL_NAME'), torch_dtype=torch.float16)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe.enable_model_cpu_offload()

prompt = "Darth Vader is surfing on waves"
video_frames = pipe(prompt, num_inference_steps=40, height=320, width=576, num_frames=24).frames
video_path = export_to_video(video_frames)
