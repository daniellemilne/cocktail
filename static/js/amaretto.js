const menu = document.querySelector('#mobile-menu');
const menuLinks = document.querySelector('.navbar_menu');

menu.addEventListener('click', function() {
    menu.classList.toggle('is-active');
    menuLinks.classList.toggle('active');

});
/* ^ This creates the drop down menu for the nav */

//modal items

const modal = document.getElementById('email-modal');
const openBtn = document.querySelector('.main-btn');
const closeBtn = document.querySelector('.close-btn');


//Click events
openBtn.addEventListener('click', () => {
    modal.style.display = 'block';
});

closeBtn.addEventListener('click', () =>{
    modal.style.display = 'none';
});

window.addEventListener('click', (e) =>{
    if(e.target === modal) {
        modal.style.display = 'none';
    }
});

//Form Validation
const form = document.getElementById('form'); //targets full form
const name = document.getElementById('name');
const email = document.getElementById('email');
const password = document.getElementById('password');
const passwordConfirm = document.getElementById('password-confirm');

//show error message

function showError(input, message) {
    const formValidation = input.parentElement;
    formValidation.className = 'form-validation error';

    const errorMessage = formValidation.querySelector('p');
    errorMessage.innerText = message;
}

//Show valid message
function showValid(input) {
    const formValidation = input.parentElement;
    formValidation.className = 'form-validation valid'; 
}

//Check required fields
function checkRequired(inputArr) {
    inputArr.forEach(function(input){
        if(input.value.trim() === '') {
            showError(input, `${getFieldName(input)} is required`);
        } else {
            showValid(input);
        }
    })
    
}

//Check input length
function checkLength(input, min, max){
    if(input.value.length < min) {
        showError(input, `${getFieldName(input)} must be at least ${min} characters`);
    }else if (input.value.length > max) {
        showError(input, `${getFieldName(input)} must be less than ${max} characters`);
    } else {
        showValid(input);
    }
}

//Check passwords match
function passwordMatch(input1, input2){
    if(input1.value !== input2.value) {
        showError(input2, 'Passwords do not match');
    }
}

//Get field name
function getFieldName(input) {
    return input.name.charAt(0).toUpperCase() + input.name.slice(1);
}

//Event Listeners
form.addEventListener('submit', (e) =>{
    e.preventDefault();

    checkRequired([name, email, password, passwordConfirm]);
    checkLength(name, 3, 30);
    checkLength(password, 8, 25);
    checkLength(passwordConfirm, 8, 25);
    passwordMatch(password, passwordConfirm);
}) 

//Image Gallery
let galleryImages = document.querySelectorAll('.services-cell');
let getLatestOpenedImg;
let windowWidth = window.innerWidth;

galleryImages.forEach(function(image, index){
    image.onclick = function() {

        getLatestOpenedImg = index + 1;
        
        let container = document.body;
        let newImgWindow = document.createElement('div');
        container.appendChild(newImgWindow);
        newImgWindow.setAttribute('class', 'img-window');
        newImgWindow.setAttribute('onclick', 'closeImg()');

        let newImg = image.firstElementChild.cloneNode();
        newImgWindow.appendChild(newImg)
        newImg.classList.remove('services-cell_img');
        newImg.classList.add('popup-img');
        newImg.setAttribute('id', 'current-img');

        newImg.onload = function() {

            let newNextBtn = document.createElement('a');
            newNextBtn.innerHTML = '<i class="fas fa-chevron-right mixology 101"></i>';
            container.appendChild(newNextBtn);
            newNextBtn.setAttribute('class', 'img-btn-next');
            newNextBtn.setAttribute('onclick', 'changeImg(1)');

            let newPrevBtn = document.createElement('a');
            newPrevBtn.innerHTML = '<i class="fas fa-chevron-left prev"></i>';
            container.appendChild(newPrevBtn);
            newPrevBtn.setAttribute('class', 'img-btn-prev');
            newPrevBtn.setAttribute('onclick', 'changeImg(0)');

        }
    }
})


function closeImg() {
    document.querySelector('.img-window').remove();
    document.querySelector('.img-btn-next').remove();
    document.querySelector('.img-btn-prev').remove();
}

window.onload = function(){
    document.querySelector('.cont_modal').className = "cont_modal";    
    }
    var c = 0;
    function open_close(){
      if(c % 2 == 0){    
    document.querySelector('.cont_modal').className = "cont_modal cont_modal_active";  
    c++;
      }else {
    document.querySelector('.cont_modal').className = "cont_modal";  
    c++;    
      }  
    } 
     