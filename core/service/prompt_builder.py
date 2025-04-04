from core.model.resource import Resource
from core.model.lora_weight import LoraWeight
from core.model.prompt import Prompt

class PromptBuilder:
    def build_from_xml(self, xml_root) -> Prompt:
        # Extract base model information
        base_model_hash = xml_root.find(".//base-model/hash").text
        base_model_page_url = xml_root.find(".//base-model/page-url").text
        base_model = Resource(hash=base_model_hash, page_url=base_model_page_url)

        # Extract Loras and their weights
        lora_weights = []
        for lora_elem in xml_root.findall(".//resources/lora"):
            lora_hash = lora_elem.find("hash").text
            lora_page_url = lora_elem.find("page-url").text
            lora_weight = float(lora_elem.find("weight").text)
            lora_weights.append(LoraWeight(
                lora=Resource(hash=lora_hash, page_url=lora_page_url),
                weight=lora_weight
            ))

        # Extract embeddings
        embeddings = []
        for embedding_elem in xml_root.findall(".//resources/embedding"):
            embedding_hash = embedding_elem.find("hash").text
            embedding_page_url = embedding_elem.find("page-url").text
            embeddings.append(Resource(hash=embedding_hash, page_url=embedding_page_url))

        # Extract VAE (optional)
        vae_elem = xml_root.find(".//vae")
        vae = None
        if vae_elem is not None:
            vae_hash = vae_elem.find("hash").text
            vae_page_url = vae_elem.find("page-url").text
            vae = Resource(hash=vae_hash, page_url=vae_page_url)

        # Extract other parameters
        positive_prompt_text = xml_root.find(".//positive-prompt").text
        negative_prompt_text = xml_root.find(".//negative-prompt").text if xml_root.find(".//negative-prompt") is not None else None
        image_width_px = int(xml_root.find(".//width").text)
        image_height_px = int(xml_root.find(".//height").text)
        generation_steps = int(xml_root.find(".//steps").text)
        sampler_name = xml_root.find(".//sampler").text
        cfg_scale = float(xml_root.find(".//cfg-scale").text)
        seed = xml_root.find(".//seed").text if xml_root.find(".//seed") is not None else None
        clip_skip = int(xml_root.find(".//clip-skip").text)

        # Create and return the parsed Prompt object
        return Prompt(
            base_model=base_model,
            lora_weights=lora_weights,
            embeddings=embeddings,
            vae=vae,
            positive_prompt_text=positive_prompt_text,
            negative_prompt_text=negative_prompt_text,
            image_width_px=image_width_px,
            image_height_px=image_height_px,
            generation_steps=generation_steps,
            sampler_name=sampler_name,
            cfg_scale=cfg_scale,
            seed=seed,
            clip_skip=clip_skip
        )
    