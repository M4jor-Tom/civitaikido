# model_search_input_selector: str = 'div > div > div > div > div > div > input[placeholder="Search Civitai"]'
model_search_input_selector: str = ".//input[@placeholder='Search Civitai']"
generation_unavailable_selector: str = "//*[text()='4 jobs in queue']"
remaining_buzz_count_and_no_more_buzz_triangle_svg_selector: str = "//div[text()='Generate']/following-sibling::div/span/div/div/*"
no_more_buzz_triangle_svg_selector: str = "svg.tabler-icon.tabler-icon-alert-triangle-filled"
all_jobs_done_selector: str = "//*[text()='4 jobs available']"
generation_button_selector: str = "//button//*[text()='Generate']"
generation_info_button_selector: str = "//button[.//*[text()='Generate']]/following-sibling::*"
creator_tip_selector: str = "//*[text()='Creator Tip']//input"
civitai_tip_selector: str = "//*[text()='Civitai Tip']//input"
images_selector: str = "//img[contains(@src,'orchestration.civitai.com')]"
page_model_hash_selector: str = "(//*[*/text()='Hash']/following-sibling::*/*/*)[2]/*/text()"
feed_perspective_button_selector: str = "//*[text()='Feed']"

profile_icon_selector: str = "//*[contains(@title, 'Avatar') and string-length(text()) = 2 and translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', '') = '']"
profile_settings_button_selector: str = 'a[href="/user/account"]'
show_mature_content_selector: str = '//*[text()="Show mature content"]'
blur_mature_content_selector: str = '//*[text()="Blur mature content"]'
pg_13_content_selector: str = '//*[text()="PG-13"]'
r_content_selector: str = '//*[text()="R"]'
x_content_selector: str = '//*[text()="X"]'
xxx_content_selector: str = '//*[text()="XXX"]'

# resource_option_selector: str = "img[src][class][style][alt][loading]"
resource_option_selector: str = "*[role='option']"

create_with_resource_selector: str = 'button[data-activity="create:model"]'
additional_resource_accordion_selector: str = "//*[text()='Additional Resources']"
# lora_weight_selector: str = "(//*[div/div/div/div/text()='Additional Resources']/following-sibling::*//input[@type][@inputmode])[1]"
lora_weight_selector: str = "(//*[.//text()='Additional Resources']/following-sibling::*//input[@type][@inputmode])[1]"
cfg_scale_input_selector: str = "#input_cfgScale-label + div > :nth-child(2) input"
sampler_input_selector: str = "#input_sampler"
sampler_option_selector_prefix: str = "//*[@role='option' and .//text()='"
sampler_option_selector_suffix: str = "']"
steps_input_selector: str = "#input_steps-label + div > :nth-child(2) input"

# create_prompt_header_button_selector: str = 'button[data-activity="create:navbar"]'
create_prompt_header_button_selector: str = "//button[.//text()='Create']/following-sibling::button"
generate_dropdown_option_selector: str = 'a[href="/generate"]'

claim_buzz_button_selector: str = 'button:has-text("Claim 25 Buzz")'
like_image_button_selector: str = ".tabler-icon-thumb-up"
generation_quantity_input_selector: str = "input#input_quantity"

close_buy_buzz_popup_selector: str = "(//*[.//text()='Buy Buzz']/following-sibling::*//button)[1]"
