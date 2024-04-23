"""
This is a Latent Consistency Model (LCM) for video generation.
 High computational complexity for my PC...
 Try this shit in some other place.

 Link:
    https://huggingface.co/wangfuyun/AnimateLCM
 """

import torch
from diffusers import AnimateDiffPipeline, LCMScheduler, MotionAdapter
from diffusers.utils import export_to_gif

from dotenv import load_dotenv
import os

load_dotenv()

adapter = MotionAdapter.from_pretrained(os.getenv('ADAPTER_NAME_ANIMATE_LCM'), torch_dtype=torch.float16)
pipe = AnimateDiffPipeline.from_pretrained(os.getenv("MODEL_NAME_ANIMATE_LCM"), motion_adapter=adapter,
                                           torch_dtype=torch.float16)
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config, beta_schedule="linear")

pipe.load_lora_weights(os.getenv('WEIGHTS_ANIMATE_LCM'),
                       weight_name=os.getenv('WEIGHT_NAME_ANIMATE_LCM'),
                       adapter_name=os.getenv('ADAPTER'))
pipe.set_adapters(["lcm-lora"], [0.8])

pipe.enable_vae_slicing()
pipe.enable_model_cpu_offload()

output = pipe(
    prompt="A space rocket with trails of smoke behind it launching into space from the desert, 4k, high resolution",
    negative_prompt="bad quality, worse quality, low resolution",
    num_frames=16,
    guidance_scale=2.0,
    num_inference_steps=6,
    generator=torch.Generator("cpu").manual_seed(0),
)
frames = output.frames[0]
export_to_gif(frames, "animatelcm.gif")
