import re

def tokenize(code):
    tokens = []
    patterns = [
        ('NUMBER', r'\b\d+\b'),
        ('STRING', r'".*?"'),
        ('KEYWORD', r'\b(if|else|for|while|def|print|let|const|var|function|console\.log)\b'),
        ('OPERATOR', r'[+\-*/=<>!]+'),
        ('SEPARATOR', r'[();,]'),
        ('IDENTIFIER', r'[a-zA-Z_]\w*')
    ]
    
    for match in re.finditer('|'.join(f'(?P<{name}>{pattern})' for name, pattern in patterns), code):
        tokens.append({'type': match.lastgroup, 'value': match.group()})
    return tokens

def optimize(code):
    """Consolidated optimization function with all patterns"""
    optimizations = [
        # Arithmetic optimizations
        (r'\b([a-zA-Z_]\w*)\s*\+\s*0(?!\d)', r'\1'),  # x + 0 → x
        (r'\b0\s*\+\s*([a-zA-Z_]\w*)\b', r'\1'),       # 0 + x → x
        (r'\b([a-zA-Z_]\w*)\s*\*\s*1(?!\d)', r'\1'),   # x * 1 → x
        (r'\b1\s*\*\s*([a-zA-Z_]\w*)\b', r'\1'),       # 1 * x → x
        
        # Boolean optimizations
        (r'if\s*\(\s*True\s*\)\s*{([^}]*)}', r'\1'),  # if (True) {x} → x
        (r'if\s*\(\s*False\s*\)\s*{([^}]*)}', r''),   # if (False) {x} → (empty)
        
        # Parentheses cleanup
        (r'\(\s*([a-zA-Z_]\w*)\s*\)', r'\1'),         # (x) → x
        
        # Whitespace cleanup
        (r';\s*;\s*', ';'),                           # ;; → ;
        (r'\s+\n', '\n'),                             # trailing spaces
        (r'\n{3,}', '\n\n')                           # multiple newlines
    ]
    
    optimized = code
    for i, (pattern, replacement) in enumerate(optimizations):
        before = optimized
        optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
        if before != optimized:
            print(f"\nApplied optimization {i+1}:")
            print("Pattern:", pattern)
            print("Before:", before)
            print("After:", optimized)
    
    print("\nFinal optimized code:\n", optimized)
    return optimized.strip()  # Should return ""