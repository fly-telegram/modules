#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import ast
import operator
import math


# Supported operators
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

# Supported functions
FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "abs": abs,
    "round": round,
    "ceil": math.ceil,
    "floor": math.floor,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
}

# Constants
CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}


def safe_eval(node):
    """Safely evaluate math expression"""
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        op_type = type(node.op)
        if op_type in OPERATORS:
            return OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported operator: {op_type}")
    elif isinstance(node, ast.UnaryOp):
        operand = safe_eval(node.operand)
        if isinstance(node.op, ast.USub):
            return -operand
        elif isinstance(node.op, ast.UAdd):
            return +operand
        raise ValueError(f"Unsupported unary operator: {type(node.op)}")
    elif isinstance(node, ast.Call):
        func_name = node.func.id if isinstance(node.func, ast.Name) else None
        if func_name in FUNCTIONS:
            args = [safe_eval(arg) for arg in node.args]
            return FUNCTIONS[func_name](*args)
        raise ValueError(f"Unknown function: {func_name}")
    elif isinstance(node, ast.Name):
        if node.id in CONSTANTS:
            return CONSTANTS[node.id]
        raise ValueError(f"Unknown variable: {node.id}")
    elif isinstance(node, ast.Expression):
        return safe_eval(node.body)
    else:
        raise ValueError(f"Unsupported expression: {type(node)}")


async def calc_cmd(self):
    """Calculate math expression - usage: .calc <expression>"""
    message = self.message
    
    # Get expression
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.calc <expression></code>\n\n"
            "📝 <b>Examples:</b>\n"
            "• <code>.calc 2 + 2</code>\n"
            "• <code>.calc sqrt(16)</code>\n"
            "• <code>.calc 2 ** 10</code>\n"
            "• <code>.calc pi * 2</code>\n"
            "• <code>.calc sin(pi/2)</code>"
        )
        return
    
    expression = args[1]
    
    try:
        # Parse and evaluate
        tree = ast.parse(expression, mode="eval")
        result = safe_eval(tree)
        
        # Format result
        if isinstance(result, float):
            if result == int(result):
                result = int(result)
            else:
                result = round(result, 10)
        
        await message.edit(
            f"🔢 <b>Calculator</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Expression:</b> <code>{expression}</code>\n"
            f"✅ <b>Result:</b> <code>{result}</code>"
        )
    except ZeroDivisionError:
        await message.edit("❌ <b>Division by zero!</b>")
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")