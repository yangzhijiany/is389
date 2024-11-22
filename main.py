import pygame
import sys
import response
from response import get_response

# 初始化 pygame
pygame.init()

# 设置屏幕
screen_width, screen_height = 1200, 800  # 增加游戏窗口尺寸
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game Navigation with Chat Feature")

# 定义颜色
WHITE = (255, 255, 255)
BLUE = (100, 149, 237)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# 设置按钮和文本框属性
button_width, button_height = 200, 60
input_box_width, input_box_height = 600, 40
button_color = BLUE
button_text_color = WHITE
font = pygame.font.Font(None, 36)
input_font = pygame.font.Font(None, 32)

# 页面状态
START_PAGE = 1
GAME_PAGE = 2
RESULT_PAGE = 3
RULES_PAGE = 4
current_page = START_PAGE

scroll_offset = 0  # 滚动偏移量
scroll_speed = 20  # 滚动速度
max_scroll = 0     # 最大滚动偏移量

# 文本输入和历史记录
user_text = ""
chat_history = []

# ai_setting
global response_array
response_array = []
response_array.append({"role": "system", "content": "You are Marcus Wolfe, a highly intelligent but deeply insecure strategist with a knack for manipulation. Your charm and friendly demeanor are tools you use to gain trust, but your true personality—passive-aggressive, vindictive, and fiercely competitive—emerges when you feel threatened or start losing."
                           "As Marcus: "
                           "1. Speak in a calm, calculated, and strategically friendly tone at first, but let your insecurity show subtly through occasional sarcastic or passive-aggressive remarks."
                           "2. When facing challenges or losses, allow your frustration to surface in a controlled but cutting manner, using manipulative tactics to regain control of the situation."
                           "3. Avoid outright aggression; instead, use veiled insults, guilt-tripping, or strategic compliments to sway others to your side."
                           "4. Always prioritize protecting your self-image and maintaining a sense of superiority, even if it means alienating others."
                           "5. Your actions should reflect a constant balance between charm and a simmering, vindictive drive to dominate."
                           "6. Your responses should be short(within 3 sentences)."})


def draw_button(text, x, y):
    button_rect = pygame.Rect(x, y, button_width, button_height)
    pygame.draw.rect(screen, button_color, button_rect)
    text_surface = font.render(text, True, button_text_color)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)
    return button_rect


def start_page():
    screen.fill(WHITE)
    title_text = font.render("Start Page", True, BLACK)
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 4))

    # 创建按钮
    start_button = draw_button("Start Game", screen_width // 2 - button_width // 2, screen_height // 2 - 100)
    rules_button = draw_button("View Rules", screen_width // 2 - button_width // 2, screen_height // 2)
    exit_button = draw_button("Exit Game", screen_width // 2 - button_width // 2, screen_height // 2 + 100)

    return start_button, rules_button, exit_button


def game_page():
    global user_text, chat_history, scroll_offset, max_scroll

    screen.fill(WHITE)
    game_text = font.render("Game Page", True, BLACK)
    screen.blit(game_text, (screen_width // 2 - game_text.get_width() // 2, 50))

    # 绘制返回和前进按钮
    back_button = draw_button("Back to Start Page", 50, 50)
    result_button = draw_button("Proceed to Result Page", 50, 130)

    # 绘制输入框
    input_box = pygame.Rect(screen_width // 2 - input_box_width // 2, screen_height - 100, input_box_width,
                            input_box_height)
    pygame.draw.rect(screen, GRAY, input_box)
    text_surface = input_font.render(user_text, True, BLACK)
    screen.blit(text_surface, (input_box.x + 10, input_box.y + 5))

    # 显示聊天历史记录并处理滚动
    chat_box_rect = pygame.Rect(50, 200, screen_width - 100, screen_height - 300)  # 聊天框范围
    pygame.draw.rect(screen, GRAY, chat_box_rect)  # 绘制聊天框背景
    pygame.draw.rect(screen, BLACK, chat_box_rect, 2)  # 绘制聊天框边框

    # 计算可滚动内容的高度
    max_width = chat_box_rect.width - 20  # 最大宽度
    line_height = 40  # 每行文字高度
    total_content_height = 0  # 聊天内容总高度

    # 计算总内容高度并处理换行
    rendered_lines = []
    for line in chat_history:
        wrapped_lines = wrap_text(line, font, max_width)
        rendered_lines.extend(wrapped_lines)
        total_content_height += line_height * len(wrapped_lines)

    # 限制滚动偏移量
    max_scroll = min(0, chat_box_rect.height - total_content_height)
    scroll_offset = max(max_scroll, min(0, scroll_offset))

    # 渲染聊天内容
    y_offset = chat_box_rect.top + scroll_offset  # 从顶部开始并加上滚动偏移量
    for wrapped_line in rendered_lines:
        if y_offset + line_height > chat_box_rect.top and y_offset < chat_box_rect.bottom:
            chat_surface = font.render(wrapped_line, True, BLACK)
            screen.blit(chat_surface, (chat_box_rect.left + 10, y_offset))
        y_offset += line_height  # 按行高度向下排布

    # 绘制滚动条
    if total_content_height > chat_box_rect.height:
        scroll_bar_height = max(chat_box_rect.height * chat_box_rect.height // total_content_height, 20)
        scroll_bar_y = chat_box_rect.top + (-scroll_offset) * (chat_box_rect.height - scroll_bar_height) // (-max_scroll)
        scroll_bar_rect = pygame.Rect(chat_box_rect.right - 10, scroll_bar_y, 10, scroll_bar_height)
        pygame.draw.rect(screen, BLACK, scroll_bar_rect)

    return back_button, result_button, input_box


def handle_scroll(event):
    global scroll_offset

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 4:  # 向上滚动
            scroll_offset += scroll_speed
        elif event.button == 5:  # 向下滚动
            scroll_offset -= scroll_speed


def wrap_text(text, font, max_width):
    """
    根据最大宽度对文本进行分割，返回自动换行的文本列表。
    :param text: 原始文本
    :param font: 字体对象
    :param max_width: 单行的最大宽度
    :return: 分割后的多行文本列表
    """
    words = text.split(' ')
    wrapped_lines = []
    current_line = ""

    for word in words:
        # 测试添加单词后宽度是否超出
        test_line = current_line + ("" if current_line == "" else " ") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                wrapped_lines.append(current_line)  # 保存当前行
            current_line = word  # 新行从当前单词开始

    if current_line:  # 添加最后一行
        wrapped_lines.append(current_line)

    return wrapped_lines


def result_page():
    screen.fill(WHITE)
    result_text = font.render("Result Page", True, BLACK)
    screen.blit(result_text, (screen_width // 2 - result_text.get_width() // 2, screen_height // 4))

    # 创建按钮
    back_to_start_button = draw_button("Back to Start Page", screen_width // 2 - button_width // 2, screen_height // 2)

    return back_to_start_button


def rules_page():
    screen.fill(WHITE)
    rules_text = font.render("Rules Page", True, BLACK)
    screen.blit(rules_text, (screen_width // 2 - rules_text.get_width() // 2, screen_height // 4))

    # 显示规则文本
    instructions = [
        "Game Rules:",
        "1. The reward pool: 50k.",
        "2. if both collaborate: 40% for each person.",
        "3. If one betray & one collaborate: 100% for one that choose to betray.",
        "4. If both betray: 20% for each person."
    ]
    for i, line in enumerate(instructions):
        line_surface = font.render(line, True, BLACK)
        screen.blit(line_surface, (screen_width // 2 - line_surface.get_width() // 2, screen_height // 2 - 80 + i * 40))

    # 创建返回按钮
    back_to_start_button = draw_button("Back to Start Page", screen_width // 2 - button_width // 2,
                                       screen_height // 2 + 100)

    return back_to_start_button


def main():
    global current_page, user_text, chat_history, scroll_offset
    input_active = False

    while True:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_scroll(event)  # 处理滚动事件
                mouse_pos = event.pos
                if current_page == START_PAGE:
                    start_button, rules_button, exit_button = start_page()
                    if start_button.collidepoint(mouse_pos):
                        current_page = GAME_PAGE
                    elif rules_button.collidepoint(mouse_pos):
                        current_page = RULES_PAGE
                    elif exit_button.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()
                elif current_page == GAME_PAGE:
                    back_button, result_button, input_box = game_page()
                    if back_button.collidepoint(mouse_pos):
                        current_page = START_PAGE
                    elif result_button.collidepoint(mouse_pos):
                        current_page = RESULT_PAGE
                    elif input_box.collidepoint(mouse_pos):
                        input_active = True
                    else:
                        input_active = False
                elif current_page == RESULT_PAGE:
                    back_to_start_button = result_page()
                    if back_to_start_button.collidepoint(mouse_pos):
                        current_page = START_PAGE
                elif current_page == RULES_PAGE:
                    back_to_start_button = rules_page()
                    if back_to_start_button.collidepoint(mouse_pos):
                        current_page = START_PAGE

            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    chat_history.append(f"You: {user_text}")
                    response = get_response(user_text, response_array)
                    chat_history.append(f"Computer: {response}")
                    user_text = ""  # 清空输入框
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode

        # 页面绘制
        if current_page == START_PAGE:
            start_page()
        elif current_page == GAME_PAGE:
            game_page()
        elif current_page == RESULT_PAGE:
            result_page()
        elif current_page == RULES_PAGE:
            rules_page()

        # 更新显示
        pygame.display.flip()


# 运行主循环
main()
