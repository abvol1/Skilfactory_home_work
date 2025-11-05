def print_board(board):
    """Выводит игровое поле"""
    for i in range(3):
        print(f" {board[i*3]} | {board[i*3+1]} | {board[i*3+2]} ")
        if i < 2:
            print("-----------")

def check_winner(board):
    """Проверяет, есть ли победитель"""
    # Все возможные выигрышные комбинации
    win_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # горизонтальные
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # вертикальные
        [0, 4, 8], [2, 4, 6]              # диагональные
    ]
    
    for combo in win_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != " ":
            return board[combo[0]]
    return None

def is_board_full(board):
    """Проверяет, заполнено ли поле"""
    return " " not in board

def main():
    """Основная функция игры"""
    board = [" "] * 9  # пустое поле 3x3
    current_player = "X"
    
    print("Добро пожаловать в Крестики-Нолики!")
    print("Вводите числа от 1 до 9 для хода:")
    print(" 1 | 2 | 3 ")
    print("-----------")
    print(" 4 | 5 | 6 ")
    print("-----------")
    print(" 7 | 8 | 9 ")
    print()
    
    while True:
        print_board(board)
        
        # Ход игрока
        try:
            move = int(input(f"Игрок {current_player}, ваш ход (1-9): ")) - 1
            if move < 0 or move > 8:
                print("Введите число от 1 до 9!")
                continue
            if board[move] != " ":
                print("Эта клетка уже занята!")
                continue
        except ValueError:
            print("Введите корректное число!")
            continue
        
        # Делаем ход
        board[move] = current_player
        
        # Проверяем победу
        winner = check_winner(board)
        if winner:
            print_board(board)
            print(f"Игрок {winner} победил!")
            break
        
        # Проверяем ничью
        if is_board_full(board):
            print_board(board)
            print("Ничья!")
            break
        
        # Меняем игрока
        current_player = "O" if current_player == "X" else "X"

# Запуск игры
if __name__ == "__main__":
    main()