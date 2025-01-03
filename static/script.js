// List of Arabic letters
const arabicLetters = ['أ', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'هـ', 'و', 'ي'];

// Select random letter
function getRandomLetter() {
    const randomIndex = Math.floor(Math.random() * arabicLetters.length);
    return arabicLetters[randomIndex];
}

// Function to animate random letters quickly
function animateRandomLetters() {
    let iterations = 10; // Number of iterations for the animation
    let letterInterval = setInterval(function() {
        const randomLetter = getRandomLetter();
        document.getElementById('selectedLetter').innerText = randomLetter;
    }, 100); // Update every 100ms to create the effect of quickly changing letters

    // Stop the animation after a short period and display the final letter
    setTimeout(function() {
        clearInterval(letterInterval); // Stop the interval
        const finalLetter = getRandomLetter(); // Get the final letter
        document.getElementById('selectedLetter').innerText = finalLetter; // Display final letter
        startCamera(finalLetter); // Start the camera with the selected letter
    }, 1500); // Stop after 1.5 seconds
}

// Display the selected letter when the button is clicked
document.getElementById('randomLetterBtn').addEventListener('click', function() {
    // Start the random letter animation
    animateRandomLetters();
});

// Start the camera and detection for the selected letter
function startCamera(letter) {
    const video = document.createElement('video');
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    const feedbackElement = document.getElementById('feedback');
    const cameraFeed = document.getElementById('cameraFeed');
    cameraFeed.innerHTML = '';
    cameraFeed.appendChild(video);

    // Get the user's webcam
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            video.srcObject = stream;
            video.play();

            // Here, you can add the object detection logic if needed
        })
        .catch((error) => {
            console.error('Error accessing webcam:', error);
            feedbackElement.innerText = 'حدث خطأ عند الوصول إلى الكاميرا.';
        });
}
