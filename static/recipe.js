/** processForm: get data from form and make AJAX call to our API. */

function showRecipes(evt) {
    evt.preventDefault();

    function show_recipe(results) {

        $("#search-results").empty()  // clear previous search results


        for (recipe of results) {
            title = recipe.title
            id = recipe.id
            protein = Math.floor(recipe.nutrition.nutrients[0].amount)
            time = recipe.readyInMinutes
            servings = recipe.servings

            newRecipe = document.createElement("div")
            title_header = document.createElement("h3")
            title_header.innerText = title
            protein_p = document.createElement("p")
            protein_p.innerText = `Protien: ${protein} //  Prep Time: ${time}  //  Serves: ${servings}`

            newRecipe.append(title_header, protein_p)

    
            $("#search-results").append(newRecipe)
        }
    }
 
    async function get_recipe() {
        // get user search input 
        query = $("#search-query").val()
        // Todo: check values of check boxes for intolerances. Create minProtein selector range or something
        intolerances = "gluten"
        
        params =  {"query": query,  "intolerances" : intolerances, "minProtein" : 10 , "number" : 2, "diet" : "vegan"}

        // get recipe from spoonacular using the complexSearch endpoint
        res = await axios.get("http://127.0.0.1:5000/api/get-recipe", {params: params})  
        results = res.data.results // recipe results JSON
     
        show_recipe(results)
    }
    resp = get_recipe() 

}



function Login() {   
}
function Signup() {
    evt.preventDefault();
    form = document.getElementById("sign-up-form")
}
function Signout() {
}


$("#search").on("click", showRecipes);




