const menu = document.querySelector('#mobile-menu');
const menuLinks = document.querySelector('.navbar_menu');

menu.addEventListener('click', function() {
    menu.classList.toggle('is-active');
    menuLinks.classList.toggle('active');

});
/* ^ This creates the drop down menu for the nav */

window.onload = () => {
    // Search form logic
    const searchForm = document.querySelector("#search-form");
    const searchResults = document.querySelector("#search-results");
    // ... rest of the search form code ...

    // Save cocktail form logic
    const saveCocktailForm = document.getElementById("save-cocktail-form");
    if (saveCocktailForm) {
        saveCocktailForm.addEventListener("submit", function (event) {
            event.preventDefault();
            
            var cocktail_id_input = document.getElementById("cocktail_id");
            console.log("Cocktail ID input:", cocktail_id_input);

            var cocktail_id = cocktail_id_input ? cocktail_id_input.value : "";

            saveCocktail(cocktail_id);
        });
    }
};


async function saveCocktail(cocktail_id) {
    if (!cocktail_id) {
        console.error("Missing cocktail_id");
        return;
    }

    try {
        const response = await fetch("/save-cocktail", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `cocktail_id=${encodeURIComponent(cocktail_id)}`,
        });

        if (response.ok) {
            window.location.href = "/saved-drinks";
        } else {
            console.error("Error saving cocktail:", response.status, response.statusText);
        }
    } catch (error) {
        console.error("Error saving cocktail:", error);
    }
}


  

  
  /*searchForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const ingredients = document.querySelector("#ingredients").value.split(',');

    const response = await fetch("/search", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ ingredients }),
    });

    const cocktails = await response.json();
    searchResults.innerHTML = "";

    for (const cocktail of cocktails) {
        const cocktailDiv = document.createElement("div");
        cocktailDiv.innerHTML = `
            <h3>${cocktail.name}</h3>
            <img src="${cocktail.image}" alt="${cocktail.name}" />
            <p>${cocktail.description}</p>
            <ul>${cocktail.ingredients.map(i => `<li>${i}</li>`).join('')}</ul>
        `;
        searchResults.appendChild(cocktailDiv);
    }
});*/


function filter() {
    var criteria = document.getElementById('filter-criteria').value.toLowerCase();
    fetch('/filter?criteria=' + criteria)
        .then(response => response.json())
        .then(cocktails => {
            var html = '';
            cocktails.forEach(cocktail => {
                html += '<div>';
                html += '<h2>' + cocktail.name + '</h2>';
                html += '<img src="' + cocktail.image + '">';
                html += '<p>' + cocktail.description + '</p>';
                html += '<ul>';
                cocktail.ingredients.forEach(ingredient => {
                    html += '<li>' + ingredient + '</li>';
                });
                html += '</ul>';
                html += '</div>';
            });
            document.getElementById('cocktails').innerHTML = html;
        });
}

  

