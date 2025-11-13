import re
import tkinter as tk
from tkinter import scrolledtext, messagebox

# ========================
# Your existing compiler code
# ========================

TOKEN_TYPES = {
    'INT_KEYWORD': r'\bint\b',
    'RETURN_KEYWORD': r'\breturn\b',
    'IDENTIFIER': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    'NUMBER': r'\b\d+\b',
    'LPAREN': r'\(',
    'RPAREN': r'\)',
    'LBRACE': r'{',
    'RBRACE': r'}',
    'SEMICOLON': r';',
    'WHITESPACE': r'\s+',   # Must be ignored
    'UNKNOWN': r'.',        # Any other character
}

# Regex for all token types
token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_TYPES.items())

def lexical_analyzer(code: str) -> list[tuple[str, str]]:
    """FUNCTION 1: Lexical Analyzer (Lexer). Breaks code into tokens."""
    print("--- Running Lexical Analyzer ---")
    tokens = []
    for match in re.finditer(token_regex, code):
        token_type = match.lastgroup
        token_value = match.group()

        if token_type == 'WHITESPACE':
            continue
        elif token_type == 'UNKNOWN':
            print(f"Lexical Error: Unknown character '{token_value}'")
            continue
        
        tokens.append((token_type, token_value))
    
    print(f"Found {len(tokens)} tokens.")
    return tokens

class SimpleParser:
    """Helper class to manage parsing state."""
    def __init__(self, tokens: list[tuple[str, str]]):
        self.tokens = tokens
        self.current_token_index = 0

    def get_current_token_type(self):
        """Gets the current token's type, or None if at end."""
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index][0]
        return None

    def advance(self):
        """Move to the next token."""
        self.current_token_index += 1

    def expect(self, expected_type: str):
        """Consumes the current token if it matches, else raises SyntaxError."""
        current_type = self.get_current_token_type()
        
        if current_type == expected_type:
            print(f"  Syntax: Matched '{expected_type}'")
            self.advance()
        else:
            raise SyntaxError(
                f"Expected token type '{expected_type}' but got '{current_type}'"
            )

def syntax_analyzer(tokens: list[tuple[str, str]]) -> bool:
    """FUNCTION 2: Syntax Analyzer (Parser). Validates token order."""
    print("\n--- Running Syntax Analyzer ---")
    parser = SimpleParser(tokens)
    
    try:
        # Expect grammar: int main() { return 0; }
        parser.expect('INT_KEYWORD')
        parser.expect('IDENTIFIER')
        parser.expect('LPAREN')
        parser.expect('RPAREN')
        parser.expect('LBRACE')
        parser.expect('RETURN_KEYWORD')
        parser.expect('NUMBER')
        parser.expect('SEMICOLON')
        parser.expect('RBRACE')
        
        if parser.get_current_token_type() is not None:
            raise SyntaxError("Unexpected tokens at end of file.")
            
        print("Syntax Analysis Successful!")
        return True
        
    except SyntaxError as e:
        print(f"Syntax Analysis Failed: {e}")
        return False

# ========================
# GUI code (the "window")
# ========================

def run_compiler():
    # Get code from the text box
    code = code_input.get("1.0", tk.END)

    # Clear previous output
    output_box.delete("1.0", tk.END)

    # Run lexical analyzer
    tokens = lexical_analyzer(code)

    # Show tokens in the output box
    output_box.insert(tk.END, "Tokens:\n")
    for token_type, token_value in tokens:
        output_box.insert(tk.END, f"{token_type}: {token_value}\n")

    # Run syntax analyzer
    ok = syntax_analyzer(tokens)

    output_box.insert(tk.END, "\nSyntax Result:\n")
    if ok:
        output_box.insert(tk.END, "Syntax Analysis Successful! ✅\n")
        messagebox.showinfo("Compiler", "Syntax Analysis Successful!")
    else:
        output_box.insert(tk.END, "Syntax Analysis Failed. ❌\n(See console for details.)\n")
        messagebox.showerror("Compiler", "Syntax Analysis Failed.\nCheck console for details.")

# Create main window
root = tk.Tk()
root.title("Mini Compiler")

# Code input label + text box
label_input = tk.Label(root, text="Source Code:")
label_input.pack(anchor="w", padx=10, pady=(10, 0))

code_input = scrolledtext.ScrolledText(root, width=80, height=15)
code_input.pack(padx=10, pady=5)

# Put a default example in the box
code_input.insert(tk.END, "int main() { return 0; }")

# Run button
run_button = tk.Button(root, text="Run Compiler", command=run_compiler)
run_button.pack(pady=5)

# Output label + text box
label_output = tk.Label(root, text="Output:")
label_output.pack(anchor="w", padx=10, pady=(10, 0))

output_box = scrolledtext.ScrolledText(root, width=80, height=15, state="normal")
output_box.pack(padx=10, pady=(0, 10))

# Start the GUI event loop
root.mainloop()