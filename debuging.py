import pyautogui
from template_finder import TemplateFinder


def main():
    finder = TemplateFinder(threshold=0.8)
    # Первый поиск
    finder.templates = [
        'templates/bait.png',
        'templates/bait_low.png',
        'templates/bait_small.png',
        'templates/bait_small_low.png'
    ]
    result1 = finder.find_and_move(delay=0.2)

    if result1:
        # Действия при успешном нахождении
        pyautogui.click()

    # Второй поиск (другие шаблоны)
    finder.templates = [
        'templates/use_bait.png',
        'templates/use_bait_small.png'
    ]
    result2 = finder.find_and_move(delay=0.1)

    # Трерий поиск (другие шаблоны)
    finder.templates = [
        'templates/use_the_bait.png',
        'templates/use_the_bait_small.png'
    ]
    result3 = finder.find_and_move(delay=0.5)

if __name__ == '__main__':
    main()
