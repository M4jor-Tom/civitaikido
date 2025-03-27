model_search_input_selector: str = 'div > div > div > div > div > div > input[placeholder="Search Civitai"]'
generation_unavailable_selector: str = "//*[text()='4 jobs in queue']"
remaining_buzz_count_and_no_more_buzz_triangle_svg_selector: str = "//div[text()='Generate']/following-sibling::div/span/div/div/*"
no_more_buzz_triangle_svg_selector: str = "svg.tabler-icon.tabler-icon-alert-triangle-filled"
generation_button_selector: str = "//button//*[text()='Generate']"
generation_info_button_selector: str = "//button[.//*[text()='Generate']]/following-sibling::*"
creator_tip_selector: str = "//div[text()='Creator Tip']//input"
civitai_tip_selector: str = "//div[text()='Civitai Tip']//input"
images_selector: str = "//img[contains(@src,'orchestration.civitai.com')]"
page_model_hash_selector: str = "(//*[*/text()='Hash']/following-sibling::*/*/*)[2]/*/text()"

global_timeout: int = 60000

# ANSI color codes for colored output
COLOR_OK = "\033[92m"       # Green
COLOR_ERROR = "\033[91m"    # Red
COLOR_WARNING = "\033[93m"  # Yellow
COLOR_RESET = "\033[0m"     # Reset color