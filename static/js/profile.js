document.getElementById('user-profile').addEventListener('click', () => {
    const profileUrl = document.getElementById('user-profile').dataset.profileUrl;
    window.location.href = profileUrl;
});


// Use the global loggedInUser variable that's set in the HTML template
const userProfileDiv = document.getElementById('user-profile');
const profilePicture = document.getElementById('profile-picture');
const userName = document.getElementById('user-name');

if (loggedInUser.isLoggedIn) {
    // Update the profile picture and user name
    profilePicture.src = window.loggedInUser.profile_picture_url;
    userName.textContent = window.loggedInUser.name;


    // Show the user-profile div
    userProfileDiv.style.display = 'flex';
} else {
    // Hide the user-profile div if the user is not logged in
    userProfileDiv.style.display = 'none';
}
