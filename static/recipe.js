/** processForm: get data from form and make AJAX call to our API. */

function showRecipes(evt) {
    evt.preventDefault();
 
    async function get_recipe() {
        // get user search input 
        query = $("#search-query").val()
        // Todo: check values of check boxes for intolerances. Create minProtein selector range or something
        intolerances = "gluten"
        // Todo: put apiKey in backend
        params =  {"apiKey": "67de1636f65f4322adffda4851c70b9d", "query": query,  "intolerances" : intolerances, "minProtein" : 10 , "number" : 2, "diet" : "vegan"}

        // get recipe from spoonacular using the complexSearch endpoint
        res = await axios.get("http://127.0.0.1:5000/api/get-recipe", {params: params}) 
        // res = await axios.get("https://api.spoonacular.com/recipes/complexSearch", {params: params}) 
        console.log(res.data.results) // recipe results JSON- id, image, nutrition(protien amt), title
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




