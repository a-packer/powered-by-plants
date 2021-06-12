// --------------- Other Cuisine Button -----------------
var cuisineForm = document.getElementById("cuisine_form");
cuisineForm.addEventListener("submit", function(evt) {
    evt.preventDefault()
    var select = document.getElementById("other_cuisine")
    s_index = select.selectedIndex 
    s_cuisine = select.options[s_index].text // get cuisine selected by user
    window.location.replace(`/cuisine/${s_cuisine}`) // redirect to selected cuisine template
})
