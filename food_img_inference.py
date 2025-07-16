from PIL import Image
from transformers import LlavaNextForConditionalGeneration,LlavaNextProcessor
import torch
import os

from transformers import BlipProcessor, BlipForConditionalGeneration

def blip_img_captioning(images:list):
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"     # Disable symbolic link warnings

    model_id  = 'Salesforce/blip-image-captioning-base'
    processor = BlipProcessor.from_pretrained(model_id)
    model     = BlipForConditionalGeneration.from_pretrained(model_id)

    # 이미지 전처리
    image        = images[0]
    inputs       = processor(images=image, return_tensors='pt')
    pixel_values = inputs['pixel_values']

    # 이미지 캡션 생성
    with torch.no_grad():
        output_ids = model.generate(
            pixel_values,
            num_beams=3, # 빔서치 (토큰생성 경우의 수)
            max_length=30,
        )
    return processor.batch_decode(output_ids, skip_special_tokens=True)

def ko_bllossom_vis_8B(images:list):
    ################################################ 모델 선언
    # https://huggingface.co/Bllossom/llama-3.1-Korean-Bllossom-Vision-8B
    model_id    = "Bllossom/llama-3.1-Korean-Bllossom-Vision-8B"
    processor   = LlavaNextProcessor.from_pretrained(model_id)
    model       = LlavaNextForConditionalGeneration.from_pretrained(
      model_id,
      torch_dtype=torch.bfloat16,
      device_map='auto'
    )

    ################################################ 이미지 전처리
    image  = images[0]
    PROMPT = """
    당신은 전 세계 음식들을 모두 다 알고 있는 음식전문가입니다.
    
    당신은 사용자가 제시한 음식 이미지의 정확한 음식명을 반환해야 합니다.
    - 답변은 반드시 음식명을 단답형으로 대답해야 합니다.
    - 음식명은 반드시 한글이름이어야 합니다.
    - 답변은 ["음식명"] 과 같이 배열로 감싼 형태여야 합니다.
    - 이미지에 음식의 개수가 여러가지라면, 최대 5개의 음식을 배열로 감싸서 반환합니다.
    
    < 답변 예시 >
    ["짜장면"]
    ["햄버거", "베이컨 연어 셀러드"]
    """

    instruction = '이 음식의 이름이 무엇인가요?'
    messages = [
        {'role': 'system', 'content': PROMPT},
        {'role': 'user'  , 'content': f"<image>\n{instruction}"}
    ]

    chat_messages = processor.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = processor(
        chat_messages,
        image,
        return_tensors='pt',
    )

    output = model.generate(
        **inputs,
        max_new_tokens=1024,
    )

    print(processor.tokenizer.decode(output[0]))

if __name__ == '__main__':
    image = Image.open('food1.jpg').convert('RGB')
    blip_img_captioning([image])
    ko_bllossom_vis_8B([image])