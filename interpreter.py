# Винятки для обробки помилок
class LexicalError(Exception):
    """Виняток, що виникає при помилках лексичного аналізу."""
    pass

class ParsingError(Exception):
    """Виняток, що виникає при помилках синтаксичного аналізу."""
    pass

# Визначення типів токенів
class TokenType:
    """Перелік можливих типів токенів."""
    INTEGER = "INTEGER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EOF = "EOF"  # Кінець вхідного рядка

class Token:
    """Клас для представлення токену."""
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Lexer:
    """Лексичний аналізатор."""
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def advance(self):
        """Переміщує 'вказівник' на наступний символ вхідного рядка."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Означає кінець введення
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        """Пропускає пробільні символи."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        """Повертає ціле число, зібране з послідовності цифр."""
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
        """Розбиває вхідний рядок на токени."""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.integer())

            if self.current_char == "+":
                self.advance()
                return Token(TokenType.PLUS, "+")

            if self.current_char == "-":
                self.advance()
                return Token(TokenType.MINUS, "-")

            if self.current_char == "*":
                self.advance()
                return Token(TokenType.MUL, "*")

            if self.current_char == "/":
                self.advance()
                return Token(TokenType.DIV, "/")

            if self.current_char == "(":
                self.advance()
                return Token(TokenType.LPAREN, "(")

            if self.current_char == ")":
                self.advance()
                return Token(TokenType.RPAREN, ")")

            raise LexicalError("Помилка лексичного аналізу")

        return Token(TokenType.EOF, None)

# Класи для побудови абстрактного синтаксичного дерева (AST)
class AST:
    """Базовий клас для вузлів AST."""
    pass

class BinOp(AST):
    """Вузол бінарної операції в AST."""
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Num(AST):
    """Вузол для представлення числа в AST."""
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Parser:
    """Синтаксичний аналізатор."""
    
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        """Викидає виняток при помилці синтаксичного аналізу."""
        raise ParsingError("Помилка синтаксичного аналізу")

    def eat(self, token_type):
        """
        Порівнює поточний токен з очікуваним типом токена.
        Якщо вони збігаються, 'поглинає' поточний токен і переходить до наступного.
        """
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        """Обробляє фактори: числа та вирази в дужках."""
        token = self.current_token
        if token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return Num(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        self.error()

    def term(self):
        """Обробляє множення та ділення."""
        node = self.factor()

        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            if token.type == TokenType.MUL:
                self.eat(TokenType.MUL)
            elif token.type == TokenType.DIV:
                self.eat(TokenType.DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def expr(self):
        """Обробляє додавання та віднімання."""
        node = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

def print_ast(node, level=0):
    """Функція для виведення AST у читабельному форматі."""
    indent = "  " * level
    if isinstance(node, Num):
        print(f"{indent}Num({node.value})")
    elif isinstance(node, BinOp):
        print(f"{indent}BinOp:")
        print(f"{indent}  left: ")
        print_ast(node.left, level + 2)
        print(f"{indent}  op: {node.op.type}")
        print(f"{indent}  right: ")
        print_ast(node.right, level + 2)
    else:
        print(f"{indent}Unknown node type: {type(node)}")

class Interpreter:
    """Інтерпретатор для обчислення результату виразу."""
    
    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):
        """Обчислює результат бінарної операції."""
        if node.op.type == TokenType.PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == TokenType.MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == TokenType.MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == TokenType.DIV:
            return self.visit(node.left) / self.visit(node.right)

    def visit_Num(self, node):
        """Повертає значення числового вузла."""
        return node.value

    def interpret(self):
        """Інтерпретує вираз та повертає результат."""
        tree = self.parser.expr()
        return self.visit(tree)

    def visit(self, node):
        """Відвідує вузол AST та викликає відповідний метод."""
        method_name = "visit_" + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Викликається, якщо немає конкретного методу візиту для типу вузла."""
        raise Exception(f"Немає методу visit_{type(node).__name__}")

def main():
    """Головна функція для запуску інтерпретатора."""
    while True:
        try:
            text = input('Введіть вираз (або "exit" для виходу): ')
            if text.lower() == "exit":
                print("Вихід із програми.")
                break
            lexer = Lexer(text)
            parser = Parser(lexer)
            interpreter = Interpreter(parser)
            result = interpreter.interpret()
            print(result)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()
