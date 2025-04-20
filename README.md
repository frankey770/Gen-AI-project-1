# Gen-AI-project1
**FoodieAI** is a FastAPI web app that uses Google Gemini to generate personalized recipes based on ingredients, cuisine, or dietary needs. Features include nutrition info, recipe search, PDF download, and shareable pages with a clean Jinja2-powered UI.

**Problem Statement**
In the modern world, people often struggle to find personalized, nutritious, and time-efficient meal ideas tailored to their preferences, ingredients on hand, or dietary restrictions. This leads to repetitive meals, unhealthy eating habits, or wasted ingredients. Additionally, many individuals lack culinary knowledge or inspiration to create meals on their own.

**Goal of the Project**
To address these challenges, we present FoodieAI — an intelligent, FastAPI-based web application that uses Google's Gemini model to generate customized recipes based on user inputs like available ingredients, cuisine types, and dietary needs. FoodieAI not only creates recipes but also provides nutritional insights, shareable links, and downloadable PDFs, helping users cook smarter and eat better.
The goal is to bridge the gap between convenience and creativity in the kitchen by offering AI-powered guidance and simplifying meal planning for everyone — from beginners to home chefs.

**INTRODUCTION**
Model-View-Template (MVT) in Django (Conceptual Reference)
Model: Defines the structure of the recipe (ingredients, steps, nutrition, etc.).
View: Handles user input, interacts with the Gemini model, and returns rendered results.
Template: Renders HTML pages for user interaction and display of AI-generated content.

**User Interaction and Authentication**
While FoodieAI does not require user authentication in its current version, it is designed with extensibility in mind to support future features like saving user history, preferences, and personalized recommendations.

**Google Gemini API Integration**
The core of FoodieAI relies on Gemini’s Generative AI capabilities to:
Generate recipes in JSON format from user-provided ingredients.
Estimate nutritional values (calories, proteins, fats, carbs).
Generate multiple recipes based on filters (cuisine, meal type, dietary restrictions).
FoodieAI uses structured prompting and regex-based parsing to handle AI responses robustly.

**Advantages**
Ingredient-Based Generation: Instant recipe suggestions based on what you have.
Nutrition Estimation: AI-predicted nutrition facts for healthier choices.
Downloadable PDFs: Professionally formatted recipes ready to print or share.
Shareable Links: Easily share recipes with friends or family.
Dynamic UI: Clean Jinja2 templates for a user-friendly experience.
Scalable & Modular: Built with FastAPI for scalability and future extensibility.

**Limitations**
AI Dependency: Relies on the Gemini model’s accuracy; poor prompts may yield invalid results.
No Persistent Database: Recipes are temporarily stored in memory.
Requires External Tools: Needs wkhtmltopdf installed locally for PDF generation.
Basic UI/UX: Minimal frontend design in current release.

**CASE STUDY**
Case Study 1: Recipe Discovery Assistant
Problem: A user wants to make dinner using leftovers like mushrooms, spinach, and pasta but doesn’t know what to cook.
Solution: FoodieAI instantly generates a delicious spinach-mushroom pasta recipe, complete with steps and nutritional facts, downloadable as a PDF.
Impact: Saves time, reduces food waste, and provides a fresh idea — all in under a minute.

Case Study 2: Custom Meal Planner
Problem: A fitness enthusiast seeks high-protein, vegetarian, Indian lunch ideas.
Solution: FoodieAI filters recipes using input parameters and presents 3 high-protein Indian vegetarian meals.
Impact: Helps users meet dietary goals while exploring variety in meals.

**Conclusion**
FoodieAI showcases the powerful intersection of AI and everyday life. It empowers users to cook creatively, eat healthily, and make the most of what’s in their kitchen. With AI integration, dynamic recipe creation, and ease of use, FoodieAI is a step toward intelligent and enjoyable cooking experiences.


