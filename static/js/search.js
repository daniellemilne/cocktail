document.addEventListener("DOMContentLoaded", function () {
  const searchForm = document.querySelector("#search-form");
  const searchResults = document.querySelector("#search-results");

  // Check if the elements exist before adding the event listener
  if (searchForm && searchResults) {
      searchForm.addEventListener("submit", async (e) => {
          e.preventDefault();
          const ingredient = document.querySelector("#ingredient").value;

          console.log(`Searching for ${ingredient}`);

          const response = await fetch("/search", {
              method: "POST",
              headers: {
                  "Content-Type": "application/json",
              },
              body: JSON.stringify({ ingredient: ingredient }),
          });

          console.log(`Received response from server`);

          const cocktails = await response.json();

          console.log(`Cocktails:`, cocktails);

          searchResults.innerHTML = "";

          for (const cocktail of cocktails.cocktails) {
              console.log(cocktail);

              const cocktailDiv = document.createElement("div");
              cocktailDiv.innerHTML = `
              <h3><a href="/cocktail/${cocktail.id}">${cocktail.name}</a></h3>
              <img src="${cocktail.image}" alt="${cocktail.name}" />
              <p>${cocktail.description}</p>
              `;

              searchResults.appendChild(cocktailDiv);
          }
      });
  }
});

