import ast
import pprint
import json
from _ast import *
import astunparse

def translate_node(node, translation_rules, language):

    is_inside_function = False

    if isinstance(node, ast.FunctionDef):
        is_inside_function = True
        function_name = node.name
        # Obtener las reglas de traducción para la definición de la función
        translation_rule = translation_rules.get("function_definition", {}).get(language, {})
        if translation_rule:
            function_return_type = "void"
            function_args = ""
            function_body = (astunparse.unparse(node.body).strip())
            translated_function_body = translate_code(function_body, translation_rules)
            body =""
            for letra in translated_function_body:
                if ";" in letra:
                    body = body + ";"+ "\n"
                    continue
                if "[" in letra:
                    body = body + "{" + "\n"
                    continue
                if "]" in letra:
                    body = body + "}" + "\n"
                    continue
                if "," in letra:
                    continue
                if '"' in letra:
                    continue
                else:
                    body = body + letra

            # Aplicar la plantilla de traducción y obtener la traducción resultante
            translated_code = translation_rule.format(
                function_name=function_name,
                function_return_type=function_return_type,
                function_args=function_args,
                function_body=body)
            # Imprimir o almacenar la traducción resultante según sea necesario
            print(translated_code)

    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "print":
        arguments = []
        print_content = astunparse.unparse(node.value.args[0]).strip()
        for arg in node.value.args:
            arg_translation = translate_node(arg, translation_rules, language)
            if arg_translation is not None:
                arguments.append(arg_translation)
        translated_print = translation_rules.get("print", {}).get(language, "")
        return translated_print.format(print_content=print_content)
    
    if isinstance(node, ast.Assign):
        variable_name = node.targets[0].id
        variable_value = astunparse.unparse(node.value).strip()
        variable_type = "int"
        if isinstance(node.value, ast.List):
            value = [translate_node(element, translation_rules, language) for element in node.value.elts]
            array_translation_rule = translation_rules.get("arrays", {}).get(language, "")
            if array_translation_rule:
                translated_assignment = array_translation_rule.format(variable_type=variable_type,
                                                                    variable_name=variable_name,
                                                                    value = value)

        translation_rule = translation_rules.get("assigment", {}).get(language, {})
        if translation_rule:
            translated_assignment = translation_rule.format(variable_name = variable_name, 
                                                      variable_value = variable_value,
                                                      variable_type = variable_type)
            
            return translated_assignment
        
    elif isinstance(node, ast.If):
        condition = translate_node(node.test, translation_rules, language)
        body = []
        for stmt in node.body:
            stmt_translation = translate_node(stmt, translation_rules, language)
            if stmt_translation is not None:
                body.append(stmt_translation)
        else_body = []
        for stmt in node.orelse:
            stmt_translation = translate_node(stmt, translation_rules, language)
            if stmt_translation is not None:
                else_body.append(stmt_translation)
        translated_if = translation_rules.get("if_statement", {}).get(language, "")
        return translated_if.format(condition=condition, body="\n".join(body))

    elif isinstance(node, ast.Compare) or isinstance(node, ast.BoolOp):
        translated_comparison = translate_condition(node, translation_rules, language)
        return translated_comparison
    
    elif isinstance(node, ast.For):
        translated_for = translate_for(node, translation_rules, language)
        return translated_for

    elif isinstance(node, ast.While):
        translated_while = translate_while(node, translation_rules, language)
        return translated_while
    
    elif isinstance(node, ast.Try):
        translated_try = translate_try(node, translation_rules, language)
        return translated_try
    
    elif isinstance(node, ast.ClassDef):
        translated_class = translate_class(node, translation_rules, language)
        return translated_class
    
    elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
              
        if isinstance(node.value.func, ast.Name):
            function_name = node.value.func.id
            arguments = []
            for arg in node.value.args:
                arg_translation = translate_node(arg, translation_rules, language)
                if arg_translation is not None:
                    arguments.append(arg_translation)
        if function_name == "len":
            # Obtener las reglas de traducción para la función len()
            translation_rule = translation_rules.get("len", {}).get(language, {})
            if translation_rule:
                translated_code = translation_rule.format(list_name=node.value.args[0].id)
                return translated_code

            translated_call = translation_rules.get("function_call", {}).get(language, "").format(
                function_name=function_name,
                arguments=", ".join(arguments)
            )
            return translated_call


    
    elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
        
        print_content = astunparse.unparse(node.value.args[0]).strip()
        function_name = node.value.func.id
        if function_name == "print":
            # Obtener las reglas de traducción para la función print()
            translation_rule = translation_rules.get("print", {}).get(language, {})
            if translation_rule:
                # Aplicar la plantilla de traducción y obtener la traducción resultante
                translated_code = translation_rule.format(argument=node.value.args[0].s, print_content=print_content)
                # Imprimir o almacenar la traducción resultante según sea necesario
                return translated_code + "\n"   
            
    for child_node in ast.iter_child_nodes(node):
        translate_node(child_node, translation_rules, language)


def translate_class(node, translation_rules, language):
    class_name = node.name
    body = []
    for stmt in node.body:
        stmt_translation = translate_node(stmt, translation_rules, language)
        if stmt_translation is not None:
            body.append(stmt_translation)
    translated_class = translation_rules.get("class", {}).get(language, "")
    translated_body = "\n".join(body)
    translated_class = translated_class.format(class_name=class_name, body=translated_body)

    return translated_class

def translate_try(try_node, translation_rules, language):
    translated_try = translation_rules.get("try_exception", {}).get(language, "")
    translated_body = []
    for stmt in try_node.body:
        stmt_translation = translate_node(stmt, translation_rules, language)
        if stmt_translation is not None:
            translated_body.append(stmt_translation)

    translated_body = "\n".join(translated_body)

    if isinstance (try_node, ast.ExceptHandler):
        exception_name = try_node.name
        exception_body = []
        for stmt in try_node.body:
            stmt_translation = translate_node(stmt, translation_rules, language)
            if stmt_translation is not None:
                exception_body.append(stmt_translation)

    exception_body = "\n".join(exception_body)
    translated_try = translated_try.format(body=translated_body, exception_name=exception_name, exception_body=exception_body)

    return translated_try


def translate_condition(node, translation_rules, language):
    if isinstance(node, ast.Compare):
        left = astunparse.unparse(node.left).strip()

        if node.ops[0].__class__.__name__ == 'Lt':
            operator = "<"
        elif node.ops[0].__class__.__name__ == 'Gt':
            operator = ">"
        elif node.ops[0].__class__.__name__ == 'Eq':
            operator = "=="
        elif node.ops[0].__class__.__name__ == 'GtE':
            operator = ">="
        elif node.ops[0].__class__.__name__ == 'LtE':
            operator = "<="
        elif node.ops[0].__class__.__name__ == 'NotEq':
            operator = "!="
        elif node.ops[0].__class__.__name__ == 'In':
            operator = "in"

        right = astunparse.unparse(node.comparators[0]).strip()
        translated_comparison = translation_rules.get("comparison_operator", {}).get(language, "")
        return translated_comparison.format(left=left, right=right, operator=operator)
    
    elif isinstance(node, ast.BoolOp):
        operator = "&&" if isinstance(node.op, ast.And) else "||" if isinstance(node.op, ast.Or) else None
        conditions = [translate_condition(value, translation_rules, language) for value in node.values]
        return f" {operator} ".join(conditions)

    return None

def translate_for(node, translation_rules, language):
    target = astunparse.unparse(node.target).strip()
    variable_condition = ""

    if isinstance(node.iter, ast.Name):
        iter_obj = node.iter.id
    elif isinstance(node.iter, ast.Call) and node.iter.func.id == "range":
        iter_args = [astunparse.unparse(arg).strip() for arg in node.iter.args]
        if len(iter_args) == 1:
            iter_obj = iter_args[0]
            variable_condition = iter_args[0]
        elif len(iter_args) == 2:
            iter_obj = f"{iter_args[0]}, {iter_args[1]}"
            variable_condition = iter_args[1]
        elif len(iter_args) == 3:
            iter_obj = f"{iter_args[0]}, {iter_args[1]}, {iter_args[2]}"
            variable_condition = iter_args[1]
        else:
            iter_obj = ""
            variable_condition = ""

    elif isinstance(node.iter, ast.Call) and node.iter.func.id != "range":
        array_name = node.iter.func.id
        translation_rule = translation_rules.get("len", {}).get(language, "")
        if translation_rule:
            translated_code = translation_rule.format(list_name=array_name)
            variable_condition = translated_code

    else:
        iter_obj = astunparse.unparse(node.iter).strip()
        variable_condition = iter_obj


    
    if variable_condition.startswith("len(") == True:
        #Obtener las reglas de traducción para la función len()
        translation_rule = translation_rules.get("len", {}).get(language, {})
        if translation_rule:
            #Aplicar la plantilla de traducción y obtener la traducción resultante
            translated_code = translation_rule.format(list_name=variable_condition[4:-1])
            #Imprimir o almacenar la traducción resultante según sea necesario
            variable_condition = translated_code

    iter_obj.split(",")
    iter_obj = iter_obj[0]

    translated_for = translation_rules.get("for_loop", {}).get(language, "")
    if translated_for:
        translated_for = translated_for.format(
            variable_type="int",
            variable_name=target,
            variable_value=iter_obj,
            variable_condition=variable_condition,
            body="{body}"
        )
        body = translate_code(astunparse.unparse(node.body).strip(), translation_rules)
        translated_for = translated_for.replace("{body}", body.strip("['']"))

    return translated_for

def translate_while(node, translation_rules, language):
    condition = translate_condition(node.test, translation_rules, language)
    translated_while = translation_rules.get("while_loop", {}).get(language, "")
    if translated_while:
        translated_while = translated_while.format(
            condition=condition,
            body="{body}"
        )
        body = translate_code(astunparse.unparse(node.body).strip(), translation_rules)
        translated_while = translated_while.replace("{body}", body.strip("['']"))
        translated_while = translated_while.replace("'", "").replace(",", "")

    return translated_while
    
def translate_code(code, translation_rules):
    tree = ast.parse(code)
    translated_code = []
    for node in ast.iter_child_nodes(tree):
        translated_node = translate_node(node, translation_rules, language)
        translated_code.append(translated_node)

    return (str(translated_code))

def translate_ast(tree, translation_rules, language):
    translated_code = []
    for node in ast.iter_child_nodes(tree):
        translated_node = translate_node(node, translation_rules, language)
        if translated_node:
            translated_code.append(translated_node)
    return "\n".join(translated_code)

def translate_program(node, translation_rules, language):
    main_body = []
    class_defs = []
    for stmt in node.body:
        if isinstance(stmt, ast.ClassDef):
            class_translation = translate_class(stmt, translation_rules, language)
            class_defs.append(class_translation)
        else:
            stmt_translation = translate_node(stmt, translation_rules, language)
            if stmt_translation is not None:
                main_body.append(stmt_translation)
    translated_program = ""
    if class_defs:
        translated_program += "\n".join(class_defs) + "\n\n"
    if main_body:
        translated_program += translation_rules.get("main", {}).get(language, {})
        translated_program += "\n".join(main_body)
        translated_program += "\n}"
    return translated_program


file_path = "programa1.py"

# Cargar las reglas de traducción desde el archivo JSON
with open("python.json") as f:
    translation_rules = json.load(f)

with open(file_path, "r") as file:
        file_content = file.read()
        ast_tree = ast.parse(file_content)
        pprint.pprint(ast.dump(ast_tree, annotate_fields=False))

#Menu de lenguajes
print("Selecciona el lenguaje de salida: \n 1. Java \n 2. JavaScript \n 3. C++")
opc = input()
if opc == "1":
    language = "java"
elif opc == "2":
    language = "javascript"
elif opc == "3":
    language = "c++"        

translated_code = translate_program(ast_tree, translation_rules, language)
if translated_code:
    print(translated_code)
