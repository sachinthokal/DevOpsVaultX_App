# tools/views.py
import json
from django.shortcuts import render
from django.http import JsonResponse

def tool_home(request):
    return render(request, 'tools/home.html')


def json_fix_view(request):
    """
    Renders the Futuristic JSON Fix tool page.
    """
    context = {}
    if request.method == "POST":
        raw_json = request.POST.get("json_input", "")
        action = request.POST.get("action", "format") # 'format' or 'minify'

        if not raw_json.strip():
            context["result"] = ""
            context["error"] = "Input cannot be empty."
            context["status"] = "error"
            return render(request, 'tools/json_fix.html', context)

        try:
            # Parse the input to check validity
            parsed_data = json.loads(raw_json)
            
            if action == "minify":
                # Remove all whitespace
                result = json.dumps(parsed_data, separators=(',', ':'))
            else:
                # Pretty print with 4-space indentation
                result = json.dumps(parsed_data, indent=4)
            
            context["result"] = result
            context["status"] = "success"
        except json.JSONDecodeError as e:
            # Maintain the raw input and show the error
            context["result"] = "" 
            context["raw_input"] = raw_json
            context["error"] = f"Invalid JSON Structure: {str(e)}"
            context["status"] = "error"
            
    return render(request, 'tools/json_fix.html', context)