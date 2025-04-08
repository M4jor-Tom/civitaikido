model_search_input_selector: str = 'div > div > div > div > div > div > input[placeholder="Search Civitai"]'
generation_unavailable_selector: str = "//*[text()='4 jobs in queue']"
remaining_buzz_count_and_no_more_buzz_triangle_svg_selector: str = "//div[text()='Generate']/following-sibling::div/span/div/div/*"
no_more_buzz_triangle_svg_selector: str = "svg.tabler-icon.tabler-icon-alert-triangle-filled"
all_jobs_done_selector: str = "//*[text()='4 jobs available']"
generation_button_selector: str = "//button//*[text()='Generate']"
generation_info_button_selector: str = "//button[.//*[text()='Generate']]/following-sibling::*"
creator_tip_selector: str = "//div[text()='Creator Tip']//input"
civitai_tip_selector: str = "//div[text()='Civitai Tip']//input"
images_selector: str = "//img[contains(@src,'orchestration.civitai.com')]"
page_model_hash_selector: str = "(//*[*/text()='Hash']/following-sibling::*/*/*)[2]/*/text()"
feed_perspective_button_selector: str = "//*[text()='Feed']"

profile_icon_selector: str = 'div[title]'
profile_settings_button_selector: str = 'a[href="/user/account"]'
show_mature_content_selector: str = '//*[text()="Show mature content"]'
blur_mature_content_selector: str = '//*[text()="Blur mature content"]'
pg_13_content_selector: str = '//*[text()="Revealing clothing, violence, or light gore"]'
r_content_selector: str = '//*[text()="Adult themes and situations, partial nudity, graphic violence, or death"]'
x_content_selector: str = '//*[text()="Graphic nudity, adult objects, or settings"]'
xxx_content_selector: str = '//*[text()="Overtly sexual or disturbing graphic content"]'

# resource_option_selector: str = "img[src][class][style][alt][loading]"
resource_option_selector: str = "*[role='option']"

# create_prompt_header_button_selector: str = 'button[data-activity="create:navbar"]'
create_prompt_header_button_selector: str = "//button[div/span/div/div/text()='Create']/following-sibling::button"
generate_dropdown_option_selector: str = 'a[href="/generate"]'

claim_buzz_button_selector: str = 'button:has-text("Claim 25 Buzz")'
like_image_button_selector: str = ".tabler-icon-thumb-up"
generation_quantity_input_selector: str = "input#input_quantity"
