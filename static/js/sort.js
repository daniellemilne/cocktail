document.addEventListener('DOMContentLoaded', () => {
    const sortOptions = document.getElementById('sort-options');
    const recipeList = document.getElementById('recipe-list');
  
    sortOptions.addEventListener('change', () => {
      const selectedOption = sortOptions.value;
      const listItems = Array.from(recipeList.getElementsByTagName('li'));
  
      if (selectedOption === 'a-z') {
        listItems.sort((a, b) => {
          return a.querySelector('h3').textContent.localeCompare(b.querySelector('h3').textContent);
        });
      } else if (selectedOption === 'z-a') {
        listItems.sort((a, b) => {
          return b.querySelector('h3').textContent.localeCompare(a.querySelector('h3').textContent);
        });
      } else {
        listItems.sort((a, b) => {
          return parseInt(a.dataset.defaultOrder) - parseInt(b.dataset.defaultOrder);
        });
      }
  
      listItems.forEach(item => {
        recipeList.appendChild(item);
      });
    });
  });
  
  