"""
代码块语法高亮模块 - 基于正则表达式的轻量级语法高亮引擎。

支持常见编程语言的语法高亮，使用ANSI颜色区分不同语法元素。
不依赖Pygments等外部库，完全基于Python标准库实现。

支持的语言：
- Python, JavaScript/TypeScript, Java, C/C++, Go, Rust
- HTML, CSS, JSON, YAML, Bash/Shell, SQL, Markdown
"""

import re
from typing import Dict, List, Optional, Tuple

from markview_pro.utils import ANSIStyle, colorize, DEFAULT_THEME


# ============================================================
# 语言关键字定义
# ============================================================

# Python 关键字
PYTHON_KEYWORDS = {
    "False", "None", "True", "and", "as", "assert", "async", "await",
    "break", "class", "continue", "def", "del", "elif", "else", "except",
    "finally", "for", "from", "global", "if", "import", "in", "is",
    "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
    "while", "with", "yield",
}

PYTHON_BUILTINS = {
    "print", "len", "range", "str", "int", "float", "list", "dict",
    "set", "tuple", "bool", "type", "isinstance", "hasattr", "getattr",
    "setattr", "delattr", "open", "input", "super", "property",
    "staticmethod", "classmethod", "abs", "all", "any", "bin", "chr",
    "dir", "divmod", "enumerate", "eval", "exec", "filter", "format",
    "frozenset", "globals", "hex", "id", "iter", "locals", "map",
    "max", "min", "next", "oct", "ord", "pow", "repr", "reversed",
    "round", "sorted", "sum", "vars", "zip", "__import__",
    "Exception", "ValueError", "TypeError", "KeyError", "IndexError",
    "AttributeError", "RuntimeError", "StopIteration", "IOError",
    "OSError", "FileNotFoundError", "ZeroDivisionError",
}

# JavaScript/TypeScript 关键字
JS_KEYWORDS = {
    "break", "case", "catch", "class", "const", "continue", "debugger",
    "default", "delete", "do", "else", "export", "extends", "false",
    "finally", "for", "function", "if", "import", "in", "instanceof",
    "let", "new", "null", "return", "super", "switch", "this", "throw",
    "true", "try", "typeof", "undefined", "var", "void", "while", "with",
    "yield", "async", "await", "of", "from", "as",
}

JS_BUILTINS = {
    "console", "document", "window", "Array", "Object", "String",
    "Number", "Boolean", "Date", "Math", "JSON", "Promise",
    "Map", "Set", "Symbol", "RegExp", "Error", "parseInt", "parseFloat",
    "isNaN", "isFinite", "encodeURI", "decodeURI", "setTimeout",
    "setInterval", "clearTimeout", "clearInterval", "fetch", "require",
    "module", "exports", "process", "global",
}

# Java 关键字
JAVA_KEYWORDS = {
    "abstract", "assert", "boolean", "break", "byte", "case", "catch",
    "char", "class", "const", "continue", "default", "do", "double",
    "else", "enum", "extends", "final", "finally", "float", "for",
    "goto", "if", "implements", "import", "instanceof", "int",
    "interface", "long", "native", "new", "package", "private",
    "protected", "public", "return", "short", "static", "strictfp",
    "super", "switch", "synchronized", "this", "throw", "throws",
    "transient", "try", "void", "volatile", "while", "true", "false",
    "null",
}

# C/C++ 关键字
C_KEYWORDS = {
    "auto", "break", "case", "char", "const", "continue", "default",
    "do", "double", "else", "enum", "extern", "float", "for", "goto",
    "if", "int", "long", "register", "return", "short", "signed",
    "sizeof", "static", "struct", "switch", "typedef", "union",
    "unsigned", "void", "volatile", "while",
    "NULL", "true", "false", "bool", "class", "namespace", "using",
    "public", "private", "protected", "virtual", "override", "template",
    "typename", "constexpr", "nullptr", "static_cast", "dynamic_cast",
    "reinterpret_cast", "const_cast", "new", "delete", "this",
    "try", "catch", "throw", "noexcept", "inline", "explicit",
    "operator", "friend", "mutable", "thread_local", "alignas",
    "alignof", "decltype", "static_assert",
}

# Go 关键字
GO_KEYWORDS = {
    "break", "case", "chan", "const", "continue", "default", "defer",
    "else", "fallthrough", "for", "func", "go", "goto", "if",
    "import", "interface", "map", "package", "range", "return",
    "select", "struct", "switch", "type", "var",
    "nil", "true", "false",
}

GO_BUILTINS = {
    "append", "cap", "close", "copy", "delete", "len", "make", "new",
    "panic", "print", "println", "recover", "real", "imag", "complex",
    "string", "int", "int8", "int16", "int32", "int64", "uint",
    "uint8", "uint16", "uint32", "uint64", "float32", "float64",
    "bool", "byte", "rune", "error", "fmt", "os", "io", "log",
}

# Rust 关键字
RUST_KEYWORDS = {
    "as", "break", "const", "continue", "crate", "else", "enum",
    "extern", "fn", "for", "if", "impl", "in", "let", "loop",
    "match", "mod", "move", "mut", "pub", "ref", "return", "self",
    "Self", "static", "struct", "super", "trait", "type", "unsafe",
    "use", "where", "while", "async", "await", "dyn",
    "true", "false",
}

RUST_BUILTINS = {
    "println", "eprintln", "format", "vec", "String", "Vec", "Box",
    "Option", "Result", "Some", "None", "Ok", "Err", "panic",
    "assert", "assert_eq", "assert_ne", "todo", "unimplemented",
    "unreachable", "derive", "Clone", "Copy", "Debug", "Default",
    "PartialEq", "Eq", "PartialOrd", "Ord", "Hash", "Serialize",
    "Deserialize", "From", "Into", "FromStr", "Display", "ToString",
    "i8", "i16", "i32", "i64", "i128", "u8", "u16", "u32", "u64",
    "u128", "f32", "f64", "bool", "char", "str", "usize", "isize",
}

# SQL 关键字
SQL_KEYWORDS = {
    "SELECT", "FROM", "WHERE", "INSERT", "INTO", "UPDATE", "DELETE",
    "CREATE", "ALTER", "DROP", "TABLE", "INDEX", "VIEW", "JOIN",
    "LEFT", "RIGHT", "INNER", "OUTER", "FULL", "CROSS", "ON",
    "AND", "OR", "NOT", "IN", "EXISTS", "BETWEEN", "LIKE", "IS",
    "NULL", "AS", "ORDER", "BY", "GROUP", "HAVING", "LIMIT",
    "OFFSET", "UNION", "ALL", "DISTINCT", "SET", "VALUES",
    "PRIMARY", "KEY", "FOREIGN", "REFERENCES", "CONSTRAINT",
    "DEFAULT", "CHECK", "UNIQUE", "CASCADE", "GRANT", "REVOKE",
    "BEGIN", "COMMIT", "ROLLBACK", "TRANSACTION", "TRIGGER",
    "FUNCTION", "PROCEDURE", "IF", "ELSE", "END", "CASE", "WHEN",
    "THEN", "ASC", "DESC", "TRUE", "FALSE", "COUNT", "SUM", "AVG",
    "MIN", "MAX", "COALESCE", "CAST", "CONVERT", "EXTRACT",
}

# Bash/Shell 关键字
BASH_KEYWORDS = {
    "if", "then", "else", "elif", "fi", "case", "esac", "for",
    "while", "until", "do", "done", "in", "function", "select",
    "time", "coproc", "|", "&&", "||", "!", "&", ";",
    "echo", "printf", "read", "cd", "pwd", "ls", "mkdir", "rm",
    "cp", "mv", "cat", "grep", "sed", "awk", "find", "sort",
    "head", "tail", "wc", "chmod", "chown", "chgrp", "export",
    "source", "alias", "unset", "set", "shift", "exit", "return",
    "true", "false", "test", "expr", "let", "local", "declare",
    "typeset", "readonly", "trap", "exec", "eval", "break",
    "continue",
}

# CSS 属性关键字
CSS_KEYWORDS = {
    "color", "background", "background-color", "background-image",
    "font", "font-size", "font-weight", "font-family", "font-style",
    "margin", "margin-top", "margin-right", "margin-bottom", "margin-left",
    "padding", "padding-top", "padding-right", "padding-bottom", "padding-left",
    "border", "border-top", "border-right", "border-bottom", "border-left",
    "display", "position", "width", "height", "top", "right", "bottom", "left",
    "float", "clear", "overflow", "z-index", "opacity", "visibility",
    "text-align", "text-decoration", "text-transform", "text-indent",
    "line-height", "letter-spacing", "word-spacing", "white-space",
    "flex", "flex-direction", "flex-wrap", "justify-content", "align-items",
    "grid", "grid-template", "grid-area", "gap",
    "transition", "transform", "animation", "box-shadow", "border-radius",
    "content", "cursor", "list-style", "max-width", "min-width",
    "max-height", "min-height", "box-sizing", "outline",
}

# HTML 标签
HTML_TAGS = {
    "a", "abbr", "address", "area", "article", "aside", "audio",
    "b", "base", "bdi", "bdo", "blockquote", "body", "br", "button",
    "canvas", "caption", "cite", "code", "col", "colgroup", "data",
    "datalist", "dd", "del", "details", "dfn", "dialog", "div", "dl",
    "dt", "em", "embed", "fieldset", "figcaption", "figure",
    "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "head",
    "header", "hgroup", "hr", "html", "i", "iframe", "img", "input",
    "ins", "kbd", "label", "legend", "li", "link", "main", "map",
    "mark", "meta", "meter", "nav", "noscript", "object", "ol",
    "optgroup", "option", "output", "p", "param", "picture", "pre",
    "progress", "q", "rp", "rt", "ruby", "s", "samp", "script",
    "section", "select", "slot", "small", "source", "span", "strong",
    "style", "sub", "summary", "sup", "table", "tbody", "td",
    "template", "textarea", "tfoot", "th", "thead", "time", "title",
    "tr", "track", "u", "ul", "var", "video", "wbr",
}

# YAML 特殊关键字
YAML_KEYWORDS = {
    "true", "false", "null", "yes", "no", "on", "off",
}


# ============================================================
# 语法高亮引擎
# ============================================================

class SyntaxHighlighter:
    """
    基于正则表达式的轻量级语法高亮引擎。

    使用ANSI颜色转义码为不同语法元素着色，
    支持多种编程语言和自定义颜色主题。

    Attributes:
        theme: 颜色主题字典
        no_color: 是否禁用颜色输出
    """

    def __init__(self, theme: Optional[Dict[str, str]] = None,
                 no_color: bool = False) -> None:
        """
        初始化语法高亮器。

        Args:
            theme: 自定义颜色主题，若为None则使用默认主题
            no_color: 是否禁用颜色
        """
        self.theme = theme or DEFAULT_THEME
        self.no_color = no_color

    def highlight(self, code: str, language: str) -> str:
        """
        对代码进行语法高亮。

        根据指定的语言对代码进行语法分析和高亮渲染。

        Args:
            code: 源代码文本
            language: 编程语言标识（如 "python", "javascript" 等）

        Returns:
            带有ANSI颜色码的高亮代码
        """
        language = language.lower().strip()

        # 语言别名映射
        lang_map = {
            "py": "python", "js": "javascript", "ts": "typescript",
            "jsx": "javascript", "tsx": "typescript",
            "c++": "cpp", "cc": "cpp", "h": "cpp", "hpp": "cpp",
            "sh": "bash", "shell": "bash", "zsh": "bash",
            "yml": "yaml", "md": "markdown",
            "rs": "rust", "rb": "ruby",
            "cs": "csharp", "c#": "csharp",
            "obj-c": "objectivec", "objc": "objectivec",
            "plain": "text", "": "text",
        }
        language = lang_map.get(language, language)

        # 获取对应语言的高亮方法
        highlighters = {
            "python": self._highlight_python,
            "javascript": self._highlight_javascript,
            "typescript": self._highlight_javascript,
            "java": self._highlight_java,
            "c": self._highlight_c,
            "cpp": self._highlight_c,
            "go": self._highlight_go,
            "rust": self._highlight_rust,
            "html": self._highlight_html,
            "css": self._highlight_css,
            "json": self._highlight_json,
            "yaml": self._highlight_yaml,
            "bash": self._highlight_bash,
            "sql": self._highlight_sql,
            "markdown": self._highlight_markdown,
            "text": lambda code: code,
        }

        highlighter = highlighters.get(language)
        if highlighter:
            return highlighter(code)
        return code

    def _apply_token_color(self, text: str, token_type: str) -> str:
        """
        为指定类型的token应用颜色。

        Args:
            text: token文本
            token_type: token类型（keyword, string, comment等）

        Returns:
            着色后的文本
        """
        style = self.theme.get(token_type, "")
        return colorize(text, style, self.no_color)

    # --------------------------------------------------------
    # 通用高亮辅助方法
    # --------------------------------------------------------

    def _highlight_strings(self, code: str) -> List[Tuple[str, str]]:
        """
        提取并标记代码中的字符串字面量。

        Args:
            code: 源代码

        Returns:
            (token_type, text) 元组列表
        """
        tokens: List[Tuple[str, str]] = []
        # 匹配三引号字符串、双引号字符串、单引号字符串
        string_patterns = [
            (r'(f?"""[\s\S]*?""")', "string"),
            (r"(f?'''[\s\S]*?''')", "string"),
            (r'(f?"[^"\\]*(?:\\.[^"\\]*)*")', "string"),
            (r"(f?'[^'\\]*(?:\\.[^'\\]*)*')", "string"),
            (r'("""[\s\S]*?""")', "string"),
            (r"('''[\s\S]*?''')", "string"),
            (r'("[^"\\]*(?:\\.[^"\\]*)*")', "string"),
            (r"('[^'\\]*(?:\\.[^'\\]*)*')", "string"),
        ]
        return tokens

    def _tokenize_common(self, code: str) -> List[Tuple[str, str]]:
        """
        通用代码分词器。

        将代码分解为 (token_type, text) 元组列表。

        Args:
            code: 源代码

        Returns:
            token列表
        """
        tokens: List[Tuple[str, str]] = []
        i = 0
        n = len(code)

        while i < n:
            # 单行注释
            if code[i] == "#" or (code[i:i+2] == "//"):
                end = code.find("\n", i)
                if end == -1:
                    end = n
                tokens.append(("comment", code[i:end]))
                i = end
                continue

            # 多行注释 (/* ... */)
            if code[i:i+2] == "/*":
                end = code.find("*/", i + 2)
                if end == -1:
                    end = n
                else:
                    end += 2
                tokens.append(("comment", code[i:end]))
                i = end
                continue

            # 三引号字符串
            if code[i:i+3] in ('"""', "'''"):
                quote = code[i:i+3]
                end = code.find(quote, i + 3)
                if end == -1:
                    end = n
                else:
                    end += 3
                tokens.append(("string", code[i:end]))
                i = end
                continue

            # 双引号字符串
            if code[i] == '"':
                j = i + 1
                while j < n and code[j] != '"':
                    if code[j] == '\\':
                        j += 2
                    else:
                        j += 1
                if j < n:
                    j += 1
                tokens.append(("string", code[i:j]))
                i = j
                continue

            # 单引号字符串
            if code[i] == "'":
                j = i + 1
                while j < n and code[j] != "'":
                    if code[j] == '\\':
                        j += 2
                    else:
                        j += 1
                if j < n:
                    j += 1
                tokens.append(("string", code[i:j]))
                i = j
                continue

            # 数字
            if code[i].isdigit() or (code[i] == '.' and i + 1 < n and code[i+1].isdigit()):
                j = i
                # 十六进制
                if code[i] == '0' and i + 1 < n and code[i+1] in ('x', 'X'):
                    j = i + 2
                    while j < n and (code[j].isalnum() or code[j] == '_'):
                        j += 1
                else:
                    while j < n and (code[j].isdigit() or code[j] == '.'
                                    or code[j] in ('e', 'E', '+', '-')):
                        j += 1
                    # 处理类型后缀 (如 10L, 5.0f)
                    if j < n and code[j] in ('L', 'l', 'f', 'F', 'd', 'D', 'U', 'u'):
                        j += 1
                tokens.append(("number", code[i:j]))
                i = j
                continue

            # 标识符/关键字
            if code[i].isalpha() or code[i] == '_':
                j = i
                while j < n and (code[j].isalnum() or code[j] == '_'):
                    j += 1
                tokens.append(("identifier", code[i:j]))
                i = j
                continue

            # 装饰器 (@decorator)
            if code[i] == '@':
                j = i + 1
                while j < n and (code[j].isalnum() or code[j] == '_'):
                    j += 1
                tokens.append(("decorator", code[i:j]))
                i = j
                continue

            # 运算符
            if code[i] in "+-*/%=<>!&|^~?:.":
                j = i + 1
                while j < n and code[j] in "+-*/%=<>!&|^~?:.":
                    j += 1
                tokens.append(("operator", code[i:j]))
                i = j
                continue

            # 标点符号
            if code[i] in "()[]{};,:":
                tokens.append(("punctuation", code[i]))
                i += 1
                continue

            # 其他字符（空白等）
            if code[i] in " \t\n\r":
                j = i
                while j < n and code[j] in " \t\n\r":
                    j += 1
                tokens.append(("whitespace", code[i:j]))
                i = j
                continue

            # 未识别字符
            tokens.append(("text", code[i]))
            i += 1

        return tokens

    def _render_tokens(self, tokens: List[Tuple[str, str]],
                       keywords: Optional[set] = None,
                       builtins: Optional[set] = None) -> str:
        """
        将token列表渲染为带ANSI颜色的文本。

        Args:
            tokens: (token_type, text) 元组列表
            keywords: 关键字集合
            builtins: 内置函数/类型集合

        Returns:
            着色后的代码文本
        """
        result = []
        for token_type, text in tokens:
            if token_type == "whitespace" or token_type == "text":
                result.append(text)
            elif token_type == "identifier":
                if keywords and text in keywords:
                    result.append(self._apply_token_color(text, "keyword"))
                elif builtins and text in builtins:
                    result.append(self._apply_token_color(text, "builtin"))
                else:
                    result.append(self._apply_token_color(text, "variable"))
            elif token_type in ("string", "comment", "number",
                                "operator", "punctuation", "decorator"):
                result.append(self._apply_token_color(text, token_type))
            else:
                result.append(text)
        return "".join(result)

    # --------------------------------------------------------
    # 各语言高亮实现
    # --------------------------------------------------------

    def _highlight_python(self, code: str) -> str:
        """
        Python 语法高亮。

        Args:
            code: Python 源代码

        Returns:
            高亮后的代码
        """
        tokens = self._tokenize_common(code)
        return self._render_tokens(tokens, PYTHON_KEYWORDS, PYTHON_BUILTINS)

    def _highlight_javascript(self, code: str) -> str:
        """
        JavaScript/TypeScript 语法高亮。

        Args:
            code: JavaScript 源代码

        Returns:
            高亮后的代码
        """
        tokens = self._tokenize_common(code)
        return self._render_tokens(tokens, JS_KEYWORDS, JS_BUILTINS)

    def _highlight_java(self, code: str) -> str:
        """
        Java 语法高亮。

        Args:
            code: Java 源代码

        Returns:
            高亮后的代码
        """
        tokens = self._tokenize_common(code)
        return self._render_tokens(tokens, JAVA_KEYWORDS)

    def _highlight_c(self, code: str) -> str:
        """
        C/C++ 语法高亮。

        Args:
            code: C/C++ 源代码

        Returns:
            高亮后的代码
        """
        tokens = self._tokenize_common(code)
        return self._render_tokens(tokens, C_KEYWORDS)

    def _highlight_go(self, code: str) -> str:
        """
        Go 语法高亮。

        Args:
            code: Go 源代码

        Returns:
            高亮后的代码
        """
        tokens = self._tokenize_common(code)
        return self._render_tokens(tokens, GO_KEYWORDS, GO_BUILTINS)

    def _highlight_rust(self, code: str) -> str:
        """
        Rust 语法高亮。

        Args:
            code: Rust 源代码

        Returns:
            高亮后的代码
        """
        tokens = self._tokenize_common(code)
        return self._render_tokens(tokens, RUST_KEYWORDS, RUST_BUILTINS)

    def _highlight_html(self, code: str) -> str:
        """
        HTML 语法高亮。

        高亮HTML标签、属性名和属性值。

        Args:
            code: HTML 源代码

        Returns:
            高亮后的代码
        """
        result = []
        i = 0
        n = len(code)

        while i < n:
            # 注释
            if code[i:i+4] == "<!--":
                end = code.find("-->", i + 4)
                if end == -1:
                    end = n
                else:
                    end += 3
                result.append(self._apply_token_color(code[i:end], "comment"))
                i = end
                continue

            # 标签
            if code[i] == '<':
                # 找到标签结束
                end = code.find(">", i)
                if end == -1:
                    end = n
                else:
                    end += 1
                tag_content = code[i:end]
                # 高亮标签
                tag_match = re.match(r"<(/?)(\w+)(.*?)(/?)>", tag_content, re.DOTALL)
                if tag_match:
                    result.append(self._apply_token_color("<", "punctuation"))
                    result.append(self._apply_token_color(tag_match.group(1), "punctuation"))
                    result.append(self._apply_token_color(tag_match.group(2), "tag"))
                    # 属性
                    attrs = tag_match.group(3)
                    if attrs.strip():
                        # 高亮属性
                        attr_pattern = re.compile(
                            r'(\w[-\w]*)'   # 属性名
                            r'(?:\s*=\s*'   # =
                            r'(?:"([^"]*)"|\'([^\']*)\'|(\S+))'  # 属性值
                            r')?'
                        )
                        for m in attr_pattern.finditer(attrs):
                            result.append(self._apply_token_color(m.group(1), "attribute"))
                            if m.group(2) is not None:
                                result.append(self._apply_token_color(
                                    f'="{m.group(2)}"', "value"))
                            elif m.group(3) is not None:
                                result.append(self._apply_token_color(
                                    f"'{m.group(3)}'", "value"))
                            elif m.group(4) is not None:
                                result.append(self._apply_token_color(
                                    f"={m.group(4)}", "value"))
                    if tag_match.group(4):
                        result.append(self._apply_token_color("/", "punctuation"))
                    result.append(self._apply_token_color(">", "punctuation"))
                else:
                    result.append(self._apply_token_color(tag_content, "tag"))
                i = end
                continue

            # 普通文本
            result.append(code[i])
            i += 1

        return "".join(result)

    def _highlight_css(self, code: str) -> str:
        """
        CSS 语法高亮。

        高亮选择器、属性名、属性值和注释。

        Args:
            code: CSS 源代码

        Returns:
            高亮后的代码
        """
        tokens = self._tokenize_common(code)
        result = []
        for token_type, text in tokens:
            if token_type == "comment":
                result.append(self._apply_token_color(text, "comment"))
            elif token_type == "string":
                result.append(self._apply_token_color(text, "value"))
            elif token_type == "number":
                result.append(self._apply_token_color(text, "number"))
            elif token_type == "identifier":
                if text in CSS_KEYWORDS:
                    result.append(self._apply_token_color(text, "keyword"))
                else:
                    result.append(self._apply_token_color(text, "tag"))
            elif token_type == "operator":
                result.append(self._apply_token_color(text, "punctuation"))
            elif token_type == "punctuation":
                result.append(self._apply_token_color(text, "punctuation"))
            else:
                result.append(text)
        return "".join(result)

    def _highlight_json(self, code: str) -> str:
        """
        JSON 语法高亮。

        高亮键名、字符串值、数字和布尔值。

        Args:
            code: JSON 源代码

        Returns:
            高亮后的代码
        """
        result = []
        i = 0
        n = len(code)

        while i < n:
            # 字符串
            if code[i] == '"':
                j = i + 1
                while j < n and code[j] != '"':
                    if code[j] == '\\':
                        j += 2
                    else:
                        j += 1
                if j < n:
                    j += 1
                string_val = code[i:j]

                # 判断是否为键名（后面跟着冒号）
                k = j
                while k < n and code[k] in " \t\n\r":
                    k += 1
                if k < n and code[k] == ':':
                    result.append(self._apply_token_color(string_val, "attribute"))
                else:
                    result.append(self._apply_token_color(string_val, "string"))
                i = j
                continue

            # 数字
            if code[i].isdigit() or (code[i] == '-' and i + 1 < n and code[i+1].isdigit()):
                j = i
                if code[j] == '-':
                    j += 1
                while j < n and (code[j].isdigit() or code[j] in '.eE+-'):
                    j += 1
                result.append(self._apply_token_color(code[i:j], "number"))
                i = j
                continue

            # 布尔值和null
            if code[i:i+4] == "true":
                result.append(self._apply_token_color("true", "keyword"))
                i += 4
                continue
            if code[i:i+5] == "false":
                result.append(self._apply_token_color("false", "keyword"))
                i += 5
                continue
            if code[i:i+4] == "null":
                result.append(self._apply_token_color("null", "keyword"))
                i += 4
                continue

            # 其他字符
            result.append(code[i])
            i += 1

        return "".join(result)

    def _highlight_yaml(self, code: str) -> str:
        """
        YAML 语法高亮。

        高亮键名、字符串值、数字和特殊值。

        Args:
            code: YAML 源代码

        Returns:
            高亮后的代码
        """
        result = []
        for line in code.split("\n"):
            stripped = line.lstrip()
            indent = len(line) - len(stripped)

            # 注释
            if stripped.startswith("#"):
                result.append(self._apply_token_color(line, "comment"))
                result.append("\n")
                continue

            # 键值对
            if ":" in stripped and not stripped.startswith("-"):
                colon_pos = stripped.index(":")
                key = stripped[:colon_pos]
                value = stripped[colon_pos + 1:].strip()

                result.append(" " * indent)
                result.append(self._apply_token_color(key, "attribute"))
                result.append(":")
                if value:
                    result.append(self._highlight_yaml_value(value))
                result.append("\n")
            elif stripped.startswith("- "):
                result.append(" " * indent)
                result.append(self._apply_token_color("-", "punctuation"))
                result.append(self._highlight_yaml_value(stripped[1:]))
                result.append("\n")
            else:
                result.append(line)
                result.append("\n")

        # 移除末尾多余的换行
        if result and result[-1] == "\n":
            result.pop()
        return "".join(result)

    def _highlight_yaml_value(self, value: str) -> str:
        """
        高亮YAML值。

        Args:
            value: YAML值字符串

        Returns:
            高亮后的值
        """
        value = value.strip()
        if not value:
            return ""
        if value.startswith('"') or value.startswith("'"):
            return self._apply_token_color(value, "string")
        if value in YAML_KEYWORDS:
            return self._apply_token_color(value, "keyword")
        try:
            float(value)
            return self._apply_token_color(value, "number")
        except ValueError:
            pass
        return self._apply_token_color(value, "variable")

    def _highlight_bash(self, code: str) -> str:
        """
        Bash/Shell 语法高亮。

        高亮命令、关键字、字符串、变量和注释。

        Args:
            code: Bash 源代码

        Returns:
            高亮后的代码
        """
        tokens = self._tokenize_common(code)
        result = []
        for token_type, text in tokens:
            if token_type == "comment":
                result.append(self._apply_token_color(text, "comment"))
            elif token_type == "string":
                result.append(self._apply_token_color(text, "string"))
            elif token_type == "identifier":
                if text in BASH_KEYWORDS:
                    result.append(self._apply_token_color(text, "keyword"))
                else:
                    result.append(self._apply_token_color(text, "function"))
            elif token_type == "number":
                result.append(self._apply_token_color(text, "number"))
            elif token_type == "operator":
                result.append(self._apply_token_color(text, "operator"))
            elif token_type == "punctuation":
                result.append(self._apply_token_color(text, "punctuation"))
            else:
                result.append(text)
        return "".join(result)

    def _highlight_sql(self, code: str) -> str:
        """
        SQL 语法高亮。

        高亮关键字、字符串、数字和注释。

        Args:
            code: SQL 源代码

        Returns:
            高亮后的代码
        """
        tokens = self._tokenize_common(code)
        return self._render_tokens(tokens, SQL_KEYWORDS)

    def _highlight_markdown(self, code: str) -> str:
        """
        Markdown 语法高亮。

        高亮Markdown的标题、粗体、斜体、链接等语法元素。

        Args:
            code: Markdown 源代码

        Returns:
            高亮后的代码
        """
        result = []
        for line in code.split("\n"):
            stripped = line.lstrip()

            # 标题
            if stripped.startswith("#"):
                level = 0
                for ch in stripped:
                    if ch == '#':
                        level += 1
                    else:
                        break
                if level <= 6 and (len(stripped) == level or stripped[level] == ' '):
                    hashes = stripped[:level]
                    content = stripped[level:].strip()
                    result.append(self._apply_token_color(hashes, "keyword"))
                    result.append(" ")
                    result.append(self._apply_token_color(content, "tag"))
                    result.append("\n")
                    continue

            # 引用
            if stripped.startswith(">"):
                result.append(self._apply_token_color(">", "comment"))
                result.append(stripped[1:])
                result.append("\n")
                continue

            # 列表
            if stripped.startswith("- ") or stripped.startswith("* "):
                result.append(self._apply_token_color(stripped[:2], "punctuation"))
                result.append(stripped[2:])
                result.append("\n")
                continue

            # 代码块标记
            if stripped.startswith("```"):
                result.append(self._apply_token_color(stripped, "string"))
                result.append("\n")
                continue

            # 链接
            link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
            m = link_pattern.search(line)
            if m:
                before = line[:m.start()]
                result.append(before)
                result.append(self._apply_token_color("[", "punctuation"))
                result.append(self._apply_token_color(m.group(1), "tag"))
                result.append(self._apply_token_color("](", "punctuation"))
                result.append(self._apply_token_color(m.group(2), "string"))
                result.append(self._apply_token_color(")", "punctuation"))
                result.append("\n")
                continue

            result.append(line)
            result.append("\n")

        if result and result[-1] == "\n":
            result.pop()
        return "".join(result)
