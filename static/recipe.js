/** processForm: get data from form and make AJAX call to our API. */

function showRecipes(evt) {
    evt.preventDefault();

    function show_recipe(results) {
 
        $("#search-results").empty()  // clear previous search results

        console.log(results)

        if (!results.error) {
            for (recipe of results) {

                title = recipe.title
                id = recipe.id 
                protein = Math.floor(recipe.nutrition.nutrients[0].amount)
                time = recipe.readyInMinutes
                servings = recipe.servings
    
                newRecipe = document.createElement("div")
                link = document.createElement("button")
                link.innerHTML = `<a href="http://127.0.0.1:5000/recipe/${recipe.id}">See Recipe</a>`
                title_header = document.createElement("h3")
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
        console.log(params)

        // get recipe from spoonacular using the complexSearch endpoint
        res = await axios.get("http://127.0.0.1:5000/api/get-recipes", {params: params})  
   
        console.log(res)
        results = res.data.results // recipe results JSON
        console.log(results)
     
        show_recipe(results)
    }
    
    resp = get_recipe() 

}


// // ------------Protein amount slider -------------------
// var slider = document.getElementById("protein_scale");
// var output = document.getElementById("demo");
// output.innerHTML = slider.value; // Display the default slider value

// // Update the current slider value (each time you drag the slider handle)
// slider.oninput = function() {
//   output.innerHTML = this.value;
// }
// // -------------------------------


function Login() {   
}
function Signup() {
    evt.preventDefault();
    form = document.getElementById("sign-up-form")
}
function Signout() {
}


// -------------Favorite Button-----------

// fav_btn = document.getElementById("favorite_button");
// fav_btn.addEventListener('click', function(e) {
// e.preventDefault()

// if ("fav_true" in fav_btn.classList) {
//     fav_btn.innerText = "Remove Favorite"
//     fav_btn.classList.remove("fav_true")
// }
// else {    
//     fav_btn.innerText = "hello"  
//     fav_btn.classList.add("fav_true")
// }
// })  



$("#search").on("click", showRecipes);









