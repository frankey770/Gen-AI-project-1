from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
import jinja2
import pdfkit
import json
import os
import shutil
from fastapi import BackgroundTasks
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="FoodieAI: Recipe Generator")

# Configure templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create necessary directories
os.makedirs("static", exist_ok=True)
os.makedirs("temp", exist_ok=True)

# Load Gemini API key securely from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables.")
genai.configure(api_key=GEMINI_API_KEY)

# Configure Gemini model - using correct model name
model = genai.GenerativeModel('gemini-2.0-flash')

# Data Model
class Recipe(BaseModel):
    name: str
    ingredients: List[str]
    steps: List[str]
    time: str
    servings: int
    cuisine: Optional[str] = None
    meal_type: Optional[str] = None
    dietary_type: Optional[str] = None
    nutrition: Optional[dict] = None

# In-memory storage
recipes_storage = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/ingredients", response_class=HTMLResponse)
async def ingredients_page(request: Request):
    return templates.TemplateResponse("ingredients.html", {"request": request})

@app.post("/generate-recipe")
async def generate_recipe(request: Request, ingredients: str = Form(...)):
    ingredients_list = [i.strip() for i in ingredients.split(',')]
    prompt = f"""Generate a recipe using these ingredients: {ingredients_list}.
    Format your response as JSON with the following structure:
    {{
      "name": "Recipe Name",
      "ingredients": ["ingredient1", "ingredient2", ...],
      "steps": ["step1", "step2", ...],
      "time": "Total time in minutes",
      "servings": number
    }}
    Please respond with valid JSON only. Do not include any extra text or explanation. Only the raw JSON object.
    """

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        if not raw_text:
            raise ValueError("Empty response from Gemini model.")

        # Extract only the JSON part from Gemini's response
        import re
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not json_match:
            raise ValueError(f"Expected JSON but received:\n{raw_text}")

        result = json.loads(json_match.group())
        recipe_id = f"recipe_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        recipes_storage[recipe_id] = Recipe(**result)

        return templates.TemplateResponse("recipe_details.html", {
            "request": request,
            "recipe": recipes_storage[recipe_id],
            "recipe_id": recipe_id
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recipe: {str(e)}")

@app.get("/recipe-search", response_class=HTMLResponse)
async def recipe_search_page(request: Request):
    return templates.TemplateResponse("recipe_search.html", {"request": request})

@app.post("/search-recipes")
async def search_recipes(
    request: Request, 
    cuisine: str = Form(...), 
    meal_type: str = Form(...), 
    dietary_type: str = Form(...)
):
    prompt = f"""Generate 3 recipes for {cuisine} cuisine, {meal_type} meal that are {dietary_type}.
    Format your response as JSON with the following structure:
    {{
      "recipes": [
        {{
          "name": "Recipe Name",
          "ingredients": ["ingredient1", "ingredient2", ...],
          "steps": ["step1", "step2", ...],
          "time": "Total time in minutes",
          "servings": number,
          "cuisine": "{cuisine}",
          "meal_type": "{meal_type}",
          "dietary_type": "{dietary_type}"
        }},
        ...
      ]
    }}
    Please respond with valid JSON only. Do not include any extra text or explanation. Only the raw JSON object.
    """
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        if not raw_text:
            raise ValueError("Empty response from Gemini model.")

        import re
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not json_match:
            raise ValueError(f"Expected JSON but received:\n{raw_text}")

        result = json.loads(json_match.group())
        recipe_ids = []

        for recipe_data in result["recipes"]:
            recipe_id = f"recipe_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(recipe_ids)}"
            recipes_storage[recipe_id] = Recipe(**recipe_data)
            recipe_ids.append(recipe_id)

        return templates.TemplateResponse("search_results.html", {
            "request": request,
            "recipes": [(recipes_storage[rid], rid) for rid in recipe_ids],
            "cuisine": cuisine,
            "meal_type": meal_type,
            "dietary_type": dietary_type
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching recipes: {str(e)}")

@app.get("/nutrition/{recipe_id}", response_class=HTMLResponse)
async def nutrition_page(request: Request, recipe_id: str):
    if recipe_id not in recipes_storage:
        raise HTTPException(status_code=404, detail="Recipe not found")

    recipe = recipes_storage[recipe_id]

    if not recipe.nutrition:
        prompt = f"""Estimate the nutritional information for this recipe:
        Name: {recipe.name}
        Ingredients: {recipe.ingredients}
        Format your response as JSON with the following structure:
        {{
          "calories": "number per serving",
          "protein": "grams per serving",
          "carbs": "grams per serving",
          "fat": "grams per serving"
        }}
        Please respond with valid JSON only. Do not include any extra text or explanation. Only the raw JSON object.
        """
        try:
            response = model.generate_content(prompt)
            raw_text = response.text.strip()

            if not raw_text:
                raise ValueError("Empty response from Gemini model.")

            import re
            json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if not json_match:
                raise ValueError(f"Expected JSON but received:\n{raw_text}")

            nutrition_info = json.loads(json_match.group())
            recipe.nutrition = nutrition_info
            recipes_storage[recipe_id] = recipe
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating nutritional info: {str(e)}")

    return templates.TemplateResponse("nutrition.html", {
        "request": request,
        "recipe": recipe,
        "recipe_id": recipe_id
    })

@app.get("/nutrition", response_class=HTMLResponse)
async def nutrition_page(request: Request, food_item: Optional[str] = None):
    nutrition = None

    if food_item:
        prompt = f"""Provide the nutritional information for the following food item:
        Food Item: {food_item}
        Format your response as JSON with the following structure:
        {{
          "calories": "number per serving",
          "protein": "grams per serving",
          "carbs": "grams per serving",
          "fat": "grams per serving"
        }}
        Please respond with valid JSON only. Do not include any extra text or explanation. Only the raw JSON object.
        """
        try:
            response = model.generate_content(prompt)
            raw_text = response.text.strip()

            if not raw_text:
                raise ValueError("Empty response from Gemini model.")

            import re
            json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if not json_match:
                raise ValueError(f"Expected JSON but received:\n{raw_text}")

            nutrition = json.loads(json_match.group())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching nutritional info: {str(e)}")

    return templates.TemplateResponse("nutrition.html", {
        "request": request,
        "food_item": food_item,
        "nutrition": nutrition
    })

@app.get("/share/{recipe_id}", response_class=HTMLResponse)
async def share_page(request: Request, recipe_id: str):
    if recipe_id not in recipes_storage:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return templates.TemplateResponse("share.html", {
        "request": request,
        "recipe": recipes_storage[recipe_id],
        "recipe_id": recipe_id
    })

@app.get("/download-pdf/{recipe_id}")
async def download_pdf(recipe_id: str, background_tasks: BackgroundTasks):
    if recipe_id not in recipes_storage:
        raise HTTPException(status_code=404, detail="Recipe not found")

    recipe = recipes_storage[recipe_id]

    # Load and render the HTML template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    try:
        template = env.get_template("recipe_pdf.html")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template loading error: {str(e)}")

    html_content = template.render(
    recipe=recipe,
    generated_on=datetime.now().strftime("%B %d, %Y")
)


    # Ensure 'temp' directory exists
    pdf_dir = Path("temp")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = pdf_dir / f"{recipe_id}.pdf"

    # Path to wkhtmltopdf (update this path as per your installation)
    try:
        config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdfkit.from_string(html_content, str(pdf_path), configuration=config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

    # Schedule background cleanup of the PDF file after response is sent
    background_tasks.add_task(pdf_path.unlink, missing_ok=True)

    # Return the file
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{recipe.name}.pdf"
    )
# Cleanup function for temporary files
@app.on_event("shutdown")
async def cleanup():
    try:
        shutil.rmtree("temp")
        os.makedirs("temp", exist_ok=True)
    except Exception:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
