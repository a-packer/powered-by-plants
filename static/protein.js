// ------------Protein amount slider -------------------
var slider = document.getElementById("protein_scale");
var output = document.getElementById("protein_amt");
output.innerHTML = slider.value; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
slider.oninput = function() {
  output.innerHTML = this.value;
}