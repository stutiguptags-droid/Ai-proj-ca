import streamlit as st
import json
import subprocess
from data.recipes import RECIPE_DATA

# Enhanced page configuration
st.set_page_config(
    page_title="AI Chef 🍽️",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for enhanced UI
st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .recipe-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
            border-left: 4px solid #FF6B6B;
            transition: transform 0.2s;
        }
        .recipe-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .recipe-title {
            color: #2C3E50;
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .recipe-meta {
            color: #7F8C8D;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        .ingredient-tag {
            display: inline-block;
            background: #E8F5E9;
            color: #2E7D32;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            margin: 0.2rem;
            font-size: 0.85rem;
        }
        .instructions-box {
            background: #F5F5F5;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            line-height: 1.6;
        }
        .stButton>button {
            background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0.5rem 2rem;
            font-weight: bold;
            font-size: 1rem;
            width: 100%;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        .input-box {
            background: #F8F9FA;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# Enhanced header
st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem;">👩‍🍳 AI Recipe Generator</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem;">Enter your ingredients and discover amazing recipes! 🔥</p>
    </div>
""", unsafe_allow_html=True)

# Input section with enhanced styling
st.markdown('<div class="input-box">', unsafe_allow_html=True)
ingredients = st.text_input(
    "**🥕 Ingredients (comma separated)**",
    "",
    placeholder="e.g., chicken, tomato, onion, garlic, spices",
    help="Enter the ingredients you have available, separated by commas"
)
st.markdown('</div>', unsafe_allow_html=True)

# Number of recipes selector
num_recipes = st.slider("**Number of recipes to generate:**", min_value=2, max_value=5, value=3, step=1)

def parse_json_from_text(text):
    import re

    text = text.strip()

    # Basic JSON fix attempt
    if text.count("{") > text.count("}"):
        text += "}"

    if text.count("[") > text.count("]"):
        text += "]"

    try:
        return json.loads(text)
    except:
        pass

    # Try to find array first (for multiple recipes)
    array_match = re.search(r"\[.*\]", text, re.DOTALL)
    if array_match:
        json_candidate = array_match.group(0)
        try:
            return json.loads(json_candidate)
        except:
            pass

    # Try to find single object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        json_candidate = match.group(0)
        try:
            return json.loads(json_candidate)
        except:
            return None

    return None


def generate_recipe_with_ai(ingredients_list, num_recipes=3):
    prompt = f"""
    Create {num_recipes} different and creative recipes using these ingredients: {ingredients_list}.
    Make each recipe unique and interesting. Return ONLY valid JSON format as an array:

    [
        {{
            "name": "Recipe Name 1",
            "ingredients": ["item1", "item2"],
            "instructions": "Step 1... Step 2...",
            "time": "X minutes"
        }},
        {{
            "name": "Recipe Name 2",
            "ingredients": ["item1", "item2"],
            "instructions": "Step 1... Step 2...",
            "time": "X minutes"
        }}
    ]

    Return exactly {num_recipes} recipes in the array. Each recipe should be creative and different.
    """

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=60
        )
        parsed = parse_json_from_text(result.stdout)
        # Ensure we return a list
        if isinstance(parsed, dict):
            return [parsed]
        elif isinstance(parsed, list):
            return parsed[:num_recipes]  # Limit to requested number
        return None
    except Exception as e:
        st.error(f"Error generating recipes: {str(e)}")
        return None


def display_recipe_card(recipe, index):
    """Display a single recipe in an enhanced card format"""
    st.markdown(f"""
        <div class="recipe-card">
            <div class="recipe-title">🍽️ {recipe.get('name', 'Unnamed Recipe')}</div>
            <div class="recipe-meta">⏱️ <strong>Time:</strong> {recipe.get('time', 'N/A')}</div>
            <div style="margin-bottom: 0.5rem;"><strong>📝 Ingredients:</strong></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Display ingredients as tags
    ingredients_list = recipe.get("ingredients", [])
    if isinstance(ingredients_list, str):
        ingredients_list = [x.strip() for x in ingredients_list.split(",")]
    
    cols = st.columns(min(len(ingredients_list), 5))
    for idx, ing in enumerate(ingredients_list):
        with cols[idx % len(cols)]:
            st.markdown(f'<span class="ingredient-tag">{ing.strip()}</span>', unsafe_allow_html=True)
    
    # Display instructions
    instructions = recipe.get("instructions", "No instructions provided.")
    st.markdown(f"""
        <div class="instructions-box">
            <strong>📌 Instructions:</strong><br>
            {instructions.replace(chr(10), '<br>')}
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")


if st.button("🚀 Generate Recipes", use_container_width=True):
    if not ingredients.strip():
        st.warning("⚠️ Please enter ingredients first!")
    else:
        user_ingredients = [x.strip().lower() for x in ingredients.split(",") if x.strip()]

        with st.spinner(f"🍳 Cooking up {num_recipes} amazing recipes with AI... This may take a moment..."):
            ai_recipes = generate_recipe_with_ai(user_ingredients, num_recipes)

        if ai_recipes and len(ai_recipes) > 0:
            st.success(f"✨ Generated {len(ai_recipes)} delicious recipe(s)!")
            st.markdown("---")
            
            for idx, recipe in enumerate(ai_recipes, 1):
                display_recipe_card(recipe, idx)
        else:
            st.error("🤖 AI couldn't generate recipes — showing best matches from our database.")
            st.markdown("---")
            
            # Show matching recipes with enhanced UI
            matching_recipes = []
            for recipe in RECIPE_DATA:
                recipe_ingredients_lower = [i.lower() for i in recipe["ingredients"]]
                if any(ing in recipe_ingredients_lower for ing in user_ingredients):
                    matching_recipes.append(recipe)
            
            if matching_recipes:
                st.info(f"📚 Found {len(matching_recipes)} matching recipe(s) in our database!")
                # Limit to requested number
                for idx, recipe in enumerate(matching_recipes[:num_recipes], 1):
                    display_recipe_card(recipe, idx)
            else:
                st.warning("😔 No matching recipes found. Try different ingredients or check your spelling! 😊")
