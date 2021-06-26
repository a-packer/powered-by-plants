/** processForm: get data from form and make AJAX call to our API. */

function showRecipes(evt) {
    evt.preventDefault();

    function show_recipe(results) {
 
        $("#search-results").empty()  // clear previous search results

        if (!results.error) {
            for (recipe of results) {

                title = recipe.title
                id = recipe.id 
                protein = Math.floor(recipe.nutrition.nutrients[0].amount)
                time = recipe.readyInMinutes
                servings = recipe.servings
    
                newRecipe = document.createElement("article")
                link = document.createElement("button")
                link.classList.add("btn")
                link.innerHTML = `<a href="http://127.0.0.1:5000/recipe/${recipe.id}">See Recipe</a>`
                title_header = document.createElement("h4")
                link.append(title_header)
                link.href = `/recipe/${id}`
                title_header.innerText = title
                recipe_details = document.createElement("p")
                recipe_details.innerText = `Protien: ${protein} //  Prep Time: ${time}  //  Serves: ${servings}`
    
                newRecipe.append(title_header, recipe_details, link)
    
        
                $("#search-results").append(newRecipe)
            }
        }
        else {
            newRecipe = document.createElement("div")
            error = document.createElement("p")
            error.innerText = "Sorry, try a different search key"
        }
        
    }
 
    async function get_recipe() {
        // get user search input 
        query = $("#search-query").val()
      
        gluten_free = $("#gluten_free").prop("checked")
        
        intolerances = ""
        if (gluten_free) {
            intolerances = 'gluten'
        }

        protein = $("#protein_scale").val()
        
        params =  {"query": query, intolerances : intolerances, "minProtein" : protein , "number" : 1, "diet" : "vegan"}

        // get recipe from spoonacular using the complexSearch endpoint
        res = await axios.get("/api/get-recipes", {params: params})  

        results = res.data.results // recipe results JSON   
        show_recipe(results)
    }
    
    resp = get_recipe() 

}


$("#search").on("click", showRecipes);









