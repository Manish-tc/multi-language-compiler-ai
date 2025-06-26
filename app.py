import code
from flask import Flask, render_template, request
  
import subprocess
import tempfile
import os
import re
from typing import Dict, List, Tuple
from datetime import datetime

app = Flask(__name__)

class Compiler:
    """Handles core compilation logic"""
    
    @staticmethod
    def tokenize(code: str) -> List[Dict[str, str]]:
        """Phase 1: Lexical Analysis"""
        token_spec = [
            ('NUMBER', r'\b\d+(\.\d+)?\b'),
            ('STRING', r'"[^"]*"|\'[^\']*\''),
            ('KEYWORD', r'\b(if|else|while|for|def|return|print|let|const|var|function|console\.log)\b'),
            ('OPERATOR', r'[+\-*/%=<>!&|^~?:]+'),
            ('SEPARATOR', r'[()\[\]{},;.]'),
            ('IDENTIFIER', r'[a-zA-Z_]\w*'),
            ('COMMENT', r'\/\/.*|\#.*'),
            ('NEWLINE', r'\n'),
            ('WHITESPACE', r'\s+'),
            ('MISMATCH', r'.')
        ]
        tokens = []
        for match in re.finditer('|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_spec), code):
            kind = match.lastgroup
            value = match.group()
            if kind not in ('WHITESPACE', 'COMMENT', 'NEWLINE'):
                tokens.append({'type': kind, 'value': value})
        return tokens

    @staticmethod
    def parse(tokens: List[Dict[str, str]]) -> bool:
        """Phase 2: Syntax Analysis (Simplified)"""
        # Basic check for balanced braces/parens
        stack = []
        for token in tokens:
            if token['value'] in '({[':
                stack.append(token['value'])
            elif token['value'] in ')}]':
                if not stack:
                    return False
                if (token['value'] == ')' and stack[-1] != '(') or \
                   (token['value'] == '}' and stack[-1] != '{') or \
                   (token['value'] == ']' and stack[-1] != '['):
                    return False
                stack.pop()
        return len(stack) == 0

    @staticmethod
    def analyze_semantics(code: str, language: str) -> List[str]:
        """Phase 3: Semantic Analysis"""
        issues = []
        if language == 'python':
            if '=' in code and not re.search(r'(def\s+\w+\(|class\s+\w+|import\s+)', code):
                issues.append("Possible missing variable declaration")
        elif language == 'javascript':
            if '=' in code and not re.search(r'(let|const|var)\s+', code):
                issues.append("Missing variable declaration (use let/const/var)")
        return issues

    @staticmethod
    def optimize(code: str) -> str:
        """Phase 5: Code Optimization"""
        optimizations = [
            (r'([a-zA-Z_]\w*)\s*([+\-])\s*0(?!\d)', r'\1'),
            (r'0\s*([+\-])\s*([a-zA-Z_]\w*)', r'\2'),
            (r'([a-zA-Z_]\w*)\s*([*/])\s*1(?!\d)', r'\1'),
            (r'if\s*\(\s*(true|false)\s*\)\s*{\s*([^}]*)\s*}\s*(else\s*{\s*([^}]*)\s*})?', 
             lambda m: m.group(2) if m.group(1) == 'true' else (m.group(4) if m.group(4) else '')),
        (r'if\s*(True|False)\s*:\s*([^\n]*)\s*(else:\s*([^\n]*))?', 
         lambda m: m.group(2) if m.group(1) == 'True' else (m.group(4) if m.group(4) else '')),
        
        # Remove empty statements
        (r';\s*(\n|$)', r'\1'),
        (r'\s+\n', r'\n')
        ]
        optimized = code
        for pattern, replacement in optimizations:
            optimized = re.sub(r'\n{3,}', '\n\n', optimized)
        return optimized.strip()

def execute_code(code: str, language: str) -> Tuple[str, str, float]:
    """Phase 6: Code Generation & Execution"""
    start_time = datetime.now()
    output, error = "", ""
    
    with tempfile.NamedTemporaryFile(
        suffix='.py' if language == 'python' else '.js',
        mode='w',
        delete=False
    ) as f:
        try:
            f.write(code)
            f.close()
            
            cmd = ['python', f.name] if language == 'python' else ['node', f.name]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            output = result.stdout
            error = result.stderr
        except subprocess.TimeoutExpired:
            error = "Timeout: Execution took too long"
        except Exception as e:
            error = f"Execution error: {str(e)}"
        finally:
            if os.path.exists(f.name):
                os.unlink(f.name)
    
    exec_time = (datetime.now() - start_time).total_seconds()
    return output, error, exec_time

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile():
    code = request.form.get('code', '')
    language = request.form.get('language', 'python')
    
    # Initialize compilation phases
    phases = {
        'lexical': False,
        'syntax': False,
        'semantic': False,
        'intermediate': False,  # Not implemented
        'optimization': False,
        'codegen': False
    }
    
    # Process code through phases
    tokens = []
    optimized_code = code
    semantics = []
    output, error = "", ""
    exec_time = 0.0
    
    try:
        # Phase 1: Lexical Analysis
        tokens = Compiler.tokenize(code)
        phases['lexical'] = True
        
        # Phase 2: Syntax Analysis
        phases['syntax'] = Compiler.parse(tokens)
        if not phases['syntax']:
            raise ValueError("Syntax error: Unbalanced brackets/parens")
        
        # Phase 3: Semantic Analysis
        semantics = Compiler.analyze_semantics(code, language)
        phases['semantic'] = True
        
        # Phase 5: Optimization (Skip intermediate for now)
        optimized_code = Compiler.optimize(code)
        phases['optimization'] = optimized_code != code
        
        # Phase 6: Code Generation & Execution
        output, error, exec_time = execute_code(optimized_code, language)
        phases['codegen'] = bool(output) and not error
        
    except Exception as e:
        error = f"Compilation error: {str(e)}"
    
    return render_template(
        'index.html',
        code=code,
        language=language,
        tokens=tokens,
        token_count=len(tokens),
        optimized_code=optimized_code,
        semantics=semantics,
        output=output,
        error=error,
        exec_time=exec_time,
        phases=phases
    )



if __name__ == '__main__':
    app.run(debug=True) 