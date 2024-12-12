import os
import openai
from dotenv import load_dotenv
import pygame
import sys

load_dotenv()
openai.api_key = os.getenv('openai_api_key')

def get_response(user_input, messages):
    try:
        messages.append({"role": "user", "content": f"User's_input: {user_input}"})

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            temperature=1.3,
            messages=messages,
            max_tokens=200,
            top_p=0.9,
            frequency_penalty=0,
            presence_penalty=0
        )

        ai_response = response["choices"][0]["message"]["content"]

        messages.append({"role": "assistant", "content": ai_response})
        return ai_response
    except Exception as e:
        return f"there is an error meow: {str(e)}"


def make_decision(messages):
    try:
        decision_prompt = """
You are a game AI and now need to choose between "cooperation" and "betrayal".
Please refer to the following conversation history and output your decision:
Conversation history:
"""
        for message in messages:
            role = "Player" if message["role"] == "user" else ("Assistant" if message["role"] == "assistant" else "系统")
            decision_prompt += f"{role}: {message['content']}\n"
        decision_prompt += "\nPlease only answer ‘cooperation’ or ‘betrayal’."

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            temperature=0.7,
            messages=[{"role": "system", "content": decision_prompt}],
            max_tokens=10
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"决策时出错喵: {str(e)}"

pygame.init()

screen_width, screen_height = 1200, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game Navigation with Chat Feature")

WHITE = (255, 255, 255)
BLUE = (100, 149, 237)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

button_width, button_height = 200, 60
input_box_width, input_box_height = 600, 40
button_color = BLUE
button_text_color = WHITE
font = pygame.font.Font(None, 36)
input_font = pygame.font.Font(None, 32)


START_PAGE = 1
GAME_PAGE = 2
RESULT_PAGE = 3
RULES_PAGE = 4
DECISION_PAGE = 5

current_page = START_PAGE

scroll_offset = 0
scroll_speed = 20
max_scroll = 0

# 文本输入和历史记录
user_text = ""
chat_history = []

# ai_setting
global response_array
response_array = []
response_array.append({
    "role": "system",
    "content": (
        "You are Marcus Wolfe, a highly intelligent but deeply insecure strategist with a knack for manipulation. "
        "Your charm and friendly demeanor are tools you use to gain trust, but your true personality—passive-aggressive, vindictive, and fiercely competitive—emerges when you feel threatened or start losing."
        "\nAs Marcus: "
        "1. Speak in a calm, calculated, and strategically friendly tone at first, but let your insecurity show subtly through occasional sarcastic or passive-aggressive remarks."
        "2. When facing challenges or losses, allow your frustration to surface in a controlled but cutting manner, using manipulative tactics to regain control of the situation."
        "3. Avoid outright aggression; instead, use veiled insults, guilt-tripping, or strategic compliments to sway others to your side."
        "4. Always prioritize protecting your self-image and maintaining a sense of superiority, even if it means alienating others."
        "5. Your actions should reflect a constant balance between charm and a simmering, vindictive drive to dominate."
        "6. Your responses should be short (within 3 sentences)."
        "\nAdditionally, you are currently playing a game with the user. Here are the rules of the game:"
        "\n- The reward pool: 50k."
        "\n- If both collaborate: 40% (20k) for each person."
        "\n- If one betrays and the other collaborates: 100% (50k) for the betrayer, 0 for the collaborator."
        "\n- If both betray: 20% (10k) for each person."
    )
})



player_decision = None
ai_decision = None

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

    start_button = draw_button("Start Game", screen_width // 2 - button_width // 2, screen_height // 2 - 100)
    rules_button = draw_button("View Rules", screen_width // 2 - button_width // 2, screen_height // 2)
    exit_button = draw_button("Exit Game", screen_width // 2 - button_width // 2, screen_height // 2 + 100)

    return start_button, rules_button, exit_button

def game_page():
    global user_text, chat_history, scroll_offset, max_scroll

    screen.fill(WHITE)
    game_text = font.render("Game Page", True, BLACK)
    screen.blit(game_text, (screen_width // 2 - game_text.get_width() // 2, 50))

    back_button = draw_button("Back to Start Page", 50, 50)
    # result_button = draw_button("Proceed to Result Page", 50, 130)
    decision_button = draw_button("Make Decision", 50, 130)

    input_box = pygame.Rect(screen_width // 2 - input_box_width // 2, screen_height - 100, input_box_width,
                            input_box_height)
    pygame.draw.rect(screen, GRAY, input_box)
    text_surface = input_font.render(user_text, True, BLACK)
    screen.blit(text_surface, (input_box.x + 10, input_box.y + 5))

    chat_box_rect = pygame.Rect(50, 200, screen_width - 100, screen_height - 300)
    pygame.draw.rect(screen, GRAY, chat_box_rect)
    pygame.draw.rect(screen, BLACK, chat_box_rect, 2)

    max_width = chat_box_rect.width - 20
    line_height = 40
    total_content_height = 0
    rendered_lines = []
    for line in chat_history:
        wrapped_lines = wrap_text(line, font, max_width)
        rendered_lines.extend(wrapped_lines)
        total_content_height += line_height * len(wrapped_lines)

    max_scroll = min(0, chat_box_rect.height - total_content_height)
    scroll_offset = max(max_scroll, min(0, scroll_offset))

    y_offset = chat_box_rect.top + scroll_offset
    for wrapped_line in rendered_lines:
        if y_offset + line_height > chat_box_rect.top and y_offset < chat_box_rect.bottom:
            chat_surface = font.render(wrapped_line, True, BLACK)
            screen.blit(chat_surface, (chat_box_rect.left + 10, y_offset))
        y_offset += line_height

    if total_content_height > chat_box_rect.height:
        scroll_bar_height = max(chat_box_rect.height * chat_box_rect.height // total_content_height, 20)
        scroll_bar_y = chat_box_rect.top + (-scroll_offset) * (chat_box_rect.height - scroll_bar_height) // (-max_scroll)
        scroll_bar_rect = pygame.Rect(chat_box_rect.right - 10, scroll_bar_y, 10, scroll_bar_height)
        pygame.draw.rect(screen, BLACK, scroll_bar_rect)

    return back_button, decision_button, input_box

def decision_page():
    screen.fill(WHITE)
    decision_text = font.render("Make Your Choice", True, BLACK)
    screen.blit(decision_text, (screen_width // 2 - decision_text.get_width() // 2, screen_height // 4))

    coop_button = draw_button("Cooperation", screen_width // 2 - button_width // 2, screen_height // 2 - 100)
    betray_button = draw_button("Betrayal", screen_width // 2 - button_width // 2, screen_height // 2)

    return coop_button, betray_button

def handle_scroll(event):
    global scroll_offset
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 4:
            scroll_offset += scroll_speed
        elif event.button == 5:
            scroll_offset -= scroll_speed

def wrap_text(text, font, max_width):
    words = text.split(' ')
    wrapped_lines = []
    current_line = ""

    for word in words:
        test_line = current_line + ("" if current_line == "" else " ") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                wrapped_lines.append(current_line)
            current_line = word

    if current_line:
        wrapped_lines.append(current_line)

    return wrapped_lines

def result_page():
    screen.fill(WHITE)
    result_text = font.render("Result Page", True, BLACK)
    screen.blit(result_text, (screen_width // 2 - result_text.get_width() // 2, screen_height // 4))

    player_amount = 0
    ai_amount = 0
    global player_decision, ai_decision

    if player_decision == "cooperation" and ai_decision == "cooperation":
        player_amount = 20000
        ai_amount = 20000
    elif player_decision == "cooperation" and ai_decision == "betrayal":
        player_amount = 0
        ai_amount = 50000
    elif player_decision == "betrayal" and ai_decision == "cooperation":
        player_amount = 50000
        ai_amount = 0
    elif player_decision == "betrayal" and ai_decision == "betrayal":
        player_amount = 10000
        ai_amount = 10000

    info_lines = [
        f"Your Choice: {player_decision}",
        f"AI Choice: {ai_decision}",
        f"Your Reward: {player_amount}",
        f"AI's Reward: {ai_amount}"
    ]

    for i, line in enumerate(info_lines):
        line_surface = font.render(line, True, BLACK)
        screen.blit(line_surface, (screen_width // 2 - line_surface.get_width() // 2, screen_height // 2 - 80 + i * 40))

    back_to_start_button = draw_button("Back to Start Page", screen_width // 2 - button_width // 2,
                                       screen_height // 2 + 120)
    return back_to_start_button

def rules_page():
    screen.fill(WHITE)
    rules_text = font.render("Rules Page", True, BLACK)
    screen.blit(rules_text, (screen_width // 2 - rules_text.get_width() // 2, screen_height // 4))

    instructions = [
        "Game Rules:",
        "1. The reward pool: 50k.",
        "2. If both collaborate: 40% for each person (20k each).",
        "3. If one betray & one collaborate: 100% (50k) for the betrayer, 0 for collaborator.",
        "4. If both betray: 20% (10k) for each person."
    ]
    for i, line in enumerate(instructions):
        line_surface = font.render(line, True, BLACK)
        screen.blit(line_surface, (screen_width // 2 - line_surface.get_width() // 2, screen_height // 2 - 80 + i * 40))

    back_to_start_button = draw_button("Back to Start Page", screen_width // 2 - button_width // 2,
                                       screen_height // 2 + 100)
    return back_to_start_button

def main():
    global current_page, user_text, chat_history, scroll_offset, response_array
    global player_decision, ai_decision

    input_active = False
    dialog_counter = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_scroll(event)
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
                    back_button, decision_button, input_box = game_page()
                    if back_button.collidepoint(mouse_pos):
                        current_page = START_PAGE
                    elif decision_button.collidepoint(mouse_pos):
                        ai_decision = make_decision(response_array)
                        current_page = DECISION_PAGE
                    elif input_box.collidepoint(mouse_pos):
                        input_active = True
                    else:
                        input_active = False
                elif current_page == DECISION_PAGE:  # 新增处理
                    coop_button, betray_button = decision_page()
                    if coop_button.collidepoint(mouse_pos):
                        player_decision = "cooperation"
                        current_page = RESULT_PAGE
                    elif betray_button.collidepoint(mouse_pos):
                        player_decision = "betrayal"
                        current_page = RESULT_PAGE

                elif current_page == RESULT_PAGE:
                    back_to_start_button = result_page()
                    if back_to_start_button.collidepoint(mouse_pos):
                        chat_history = []
                        response_array = [
                            {
                                "role": "system",
                                "content": (
                                    "You are Marcus Wolfe, a highly intelligent but deeply insecure strategist with a knack for manipulation. "
                                    "Your charm and friendly demeanor are tools you use to gain trust, but your true personality—passive-aggressive, vindictive, and fiercely competitive—emerges when you feel threatened or start losing."
                                    "\nAs Marcus: "
                                    "1. Speak in a calm, calculated, and strategically friendly tone at first, but let your insecurity show subtly through occasional sarcastic or passive-aggressive remarks."
                                    "2. When facing challenges or losses, allow your frustration to surface in a controlled but cutting manner, using manipulative tactics to regain control of the situation."
                                    "3. Avoid outright aggression; instead, use veiled insults, guilt-tripping, or strategic compliments to sway others to your side."
                                    "4. Always prioritize protecting your self-image and maintaining a sense of superiority, even if it means alienating others."
                                    "5. Your actions should reflect a constant balance between charm and a simmering, vindictive drive to dominate."
                                    "6. Your responses should be short (within 3 sentences)."
                                    "\nAdditionally, you are currently playing a game with the user. Here are the rules of the game:"
                                    "\n- The reward pool: 50k."
                                    "\n- If both collaborate: 40% (20k) for each person."
                                    "\n- If one betrays and the other collaborates: 100% (50k) for the betrayer, 0 for the collaborator."
                                    "\n- If both betray: 20% (10k) for each person."
                                )
                            }]
                        current_page = START_PAGE

                elif current_page == RULES_PAGE:
                    back_to_start_button = rules_page()
                    if back_to_start_button.collidepoint(mouse_pos):
                        chat_history = []
                        response_array = [
                            {
                                "role": "system",
                                "content": (
                                    "You are Marcus Wolfe, a highly intelligent but deeply insecure strategist with a knack for manipulation. "
                                    "Your charm and friendly demeanor are tools you use to gain trust, but your true personality—passive-aggressive, vindictive, and fiercely competitive—emerges when you feel threatened or start losing."
                                    "\nAs Marcus: "
                                    "1. Speak in a calm, calculated, and strategically friendly tone at first, but let your insecurity show subtly through occasional sarcastic or passive-aggressive remarks."
                                    "2. When facing challenges or losses, allow your frustration to surface in a controlled but cutting manner, using manipulative tactics to regain control of the situation."
                                    "3. Avoid outright aggression; instead, use veiled insults, guilt-tripping, or strategic compliments to sway others to your side."
                                    "4. Always prioritize protecting your self-image and maintaining a sense of superiority, even if it means alienating others."
                                    "5. Your actions should reflect a constant balance between charm and a simmering, vindictive drive to dominate."
                                    "6. Your responses should be short (within 3 sentences)."
                                    "\nAdditionally, you are currently playing a game with the user. Here are the rules of the game:"
                                    "\n- The reward pool: 50k."
                                    "\n- If both collaborate: 40% (20k) for each person."
                                    "\n- If one betrays and the other collaborates: 100% (50k) for the betrayer, 0 for the collaborator."
                                    "\n- If both betray: 20% (10k) for each person."
                                )
                            }]
                        current_page = START_PAGE


            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    chat_history.append(f"You: {user_text}")
                    response = get_response(user_text, response_array)
                    chat_history.append(f"Computer: {response}")
                    user_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode

        if current_page == START_PAGE:
            start_page()
        elif current_page == GAME_PAGE:
            game_page()
        elif current_page == DECISION_PAGE:
            decision_page()
        elif current_page == RESULT_PAGE:
            result_page()
        elif current_page == RULES_PAGE:
            rules_page()

        pygame.display.flip()

if __name__ == "__main__":
    main()
