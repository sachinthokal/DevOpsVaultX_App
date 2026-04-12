# tools/views.py
import json
from django.shortcuts import render
from django.http import JsonResponse

def tool_home(request):
    return render(request, 'tools/home.html')


import json
import re

def json_fix_view(request):
    context = {}
    if request.method == "POST":
        raw_json = request.POST.get("json_input", "").strip()
        action = request.POST.get("action", "format")

        if not raw_json:
            context.update({"result": "", "error": "Input cannot be empty.", "status": "error"})
            return render(request, 'tools/json_fix.html', context)

        try:
            # --- AUTO-FIX LOGIC ---
            # 1. Single quotes la double quotes madhe badla
            fixed_json = raw_json.replace("'", '"')
            
            # 2. Trailing commas remove kara (e.g., [1, 2,] -> [1, 2])
            fixed_json = re.sub(r',\s*([\]}])', r'\1', fixed_json)
            
            # 3. Unquoted keys la quotes lava (e.g., {name: "val"} -> {"name": "val"})
            fixed_json = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+?)\s*:', r'\1"\2":', fixed_json)

            # Parse fixed data
            parsed_data = json.loads(fixed_json)
            
            if action == "minify":
                result = json.dumps(parsed_data, separators=(',', ':'))
            else:
                result = json.dumps(parsed_data, indent=4)
            
            context.update({"result": result, "status": "success", "raw_input": raw_json})
            
        except Exception as e:
            context.update({
                "result": "", 
                "raw_input": raw_json, 
                "error": f"Could not auto-fix: {str(e)}", 
                "status": "error"
            })
            
    return render(request, 'tools/json_fix.html', context)

def yaml_json_view(request):
    """
    Renders the YAML/JSON Converter tool page.
    """
    context = {}
    if request.method == "POST":
        input_data = request.POST.get("input_data", "")
        conversion_type = request.POST.get("conversion_type", "yaml_to_json") # 'yaml_to_json' or 'json_to_yaml'

        if not input_data.strip():
            context["result"] = ""
            context["error"] = "Input cannot be empty."
            context["status"] = "error"
            return render(request, 'tools/yaml_json.html', context)

        try:
            if conversion_type == "yaml_to_json":
                import yaml
                parsed_data = yaml.safe_load(input_data)
                result = json.dumps(parsed_data, indent=4)
            else:
                parsed_data = json.loads(input_data)
                import yaml
                result = yaml.dump(parsed_data, default_flow_style=False)
            
            context["result"] = result
            context["status"] = "success"
        except Exception as e:
            # Maintain the raw input and show the error
            context["result"] = "" 
            context["raw_input"] = input_data
            context["error"] = f"Conversion Error: {str(e)}"
            context["status"] = "error"
            
    return render(request, 'tools/yaml_json.html', context)


def beautify_view(request):
    """
    Renders the Beautify tool page.
    """
    context = {}
    if request.method == "POST":
        raw_input = request.POST.get("raw_input", "")
        input_type = request.POST.get("input_type", "json") # 'json' or 'xml'

        if not raw_input.strip():
            context["result"] = ""
            context["error"] = "Input cannot be empty."
            context["status"] = "error"
            return render(request, 'tools/beautify.html', context)

        try:
            if input_type == "json":
                parsed_data = json.loads(raw_input)
                result = json.dumps(parsed_data, indent=4)
            else:
                import xml.dom.minidom
                dom = xml.dom.minidom.parseString(raw_input)
                result = dom.toprettyxml()
            
            context["result"] = result
            context["status"] = "success"
        except Exception as e:
            # Maintain the raw input and show the error
            context["result"] = "" 
            context["raw_input"] = raw_input
            context["error"] = f"Beautification Error: {str(e)}"
            context["status"] = "error"
            
    return render(request, 'tools/beautify.html', context)

def base64_view(request):
    """
    Renders the Base64 Encode/Decode tool page.
    """
    context = {}
    if request.method == "POST":
        raw_input = request.POST.get("raw_input", "")
        action = request.POST.get("action", "encode") # 'encode' or 'decode'

        if not raw_input.strip():
            context["result"] = ""
            context["error"] = "Input cannot be empty."
            context["status"] = "error"
            return render(request, 'tools/base64.html', context)

        try:
            import base64
            if action == "encode":
                result = base64.b64encode(raw_input.encode()).decode()
            else:
                result = base64.b64decode(raw_input.encode()).decode()
            
            context["result"] = result
            context["status"] = "success"
        except Exception as e:
            # Maintain the raw input and show the error
            context["result"] = "" 
            context["raw_input"] = raw_input
            context["error"] = f"Base64 Error: {str(e)}"
            context["status"] = "error"
            
    return render(request, 'tools/base64.html', context)

def secret_gen_view(request):
    """
    Renders the Secret Generator tool page.
    """
    context = {}
    if request.method == "POST":
        length = int(request.POST.get("length", 16))
        include_uppercase = request.POST.get("include_uppercase") == "on"
        include_lowercase = request.POST.get("include_lowercase") == "on"
        include_digits = request.POST.get("include_digits") == "on"
        include_special = request.POST.get("include_special") == "on"

        if length <= 0:
            context["result"] = ""
            context["error"] = "Length must be a positive integer."
            context["status"] = "error"
            return render(request, 'tools/secret_gen.html', context)

        try:
            import string
            import random

            character_pool = ""
            if include_uppercase:
                character_pool += string.ascii_uppercase
            if include_lowercase:
                character_pool += string.ascii_lowercase
            if include_digits:
                character_pool += string.digits
            if include_special:
                character_pool += string.punctuation

            if not character_pool:
                context["result"] = ""
                context["error"] = "At least one character type must be selected."
                context["status"] = "error"
                return render(request, 'tools/secret_gen.html', context)

            result = ''.join(random.choice(character_pool) for _ in range(length))
            context["result"] = result
            context["status"] = "success"
        except Exception as e:
            context["result"] = "" 
            context["error"] = f"Secret Generation Error: {str(e)}"
            context["status"] = "error"
            
    return render(request, 'tools/secret_gen.html', context)


def case_converter_view(request):
    """
    Renders the Case Converter tool page.
    """
    context = {}
    if request.method == "POST":
        raw_input = request.POST.get("raw_input", "")
        conversion_type = request.POST.get("conversion_type", "upper") # 'upper', 'lower', 'camel', 'snake'

        if not raw_input.strip():
            context["result"] = ""
            context["error"] = "Input cannot be empty."
            context["status"] = "error"
            return render(request, 'tools/case_converter.html', context)

        try:
            if conversion_type == "upper":
                result = raw_input.upper()
            elif conversion_type == "lower":
                result = raw_input.lower()
            elif conversion_type == "camel":
                result = ''.join(word.capitalize() for word in raw_input.split())
            elif conversion_type == "snake":
                result = '_'.join(raw_input.split()).lower()
            else:
                result = raw_input
            
            context["result"] = result
            context["status"] = "success"
        except Exception as e:
            # Maintain the raw input and show the error
            context["result"] = "" 
            context["raw_input"] = raw_input
            context["error"] = f"Case Conversion Error: {str(e)}"
            context["status"] = "error"
            
    return render(request, 'tools/case_converter.html', context)