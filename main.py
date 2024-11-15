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

# 文本输入和历史记录
user_text = ""
chat_history = []

# ai_setting
global response_array
response_array = []
response_array.append({"role": "system", "content": ""})



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
    global user_text, chat_history

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

    # 显示聊天历史记录
    y_offset = 200
    for line in chat_history[-10:]:  # 仅显示最后10条记录
        chat_surface = font.render(line, True, BLACK)
        screen.blit(chat_surface, (50, y_offset))
        y_offset += 40

    return back_button, result_button, input_box


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
    global current_page, user_text, chat_history
    input_active = False

    while True:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
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
                    response: str = get_response("", user_text, response_array)
                    chat_history.append(f"Computer: {response}")
                    # response_array.append()
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
