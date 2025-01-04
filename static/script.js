// قائمة بالحروف العربية التي ستختار بشكل عشوائي
const arabicLetters = ['أ', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'هـ', 'و', 'ي'];

// اختيار حرف عشوائي
function getRandomLetter() {
    const randomIndex = Math.floor(Math.random() * arabicLetters.length);
    return arabicLetters[randomIndex];
}

// انيميشن حروف عشوائية
function animateRandomLetters() {
    let iterations = 10; // عدد التكرارات العشوائية لتحديد حرف عشوائي
    let letterInterval = setInterval(function() {
        const randomLetter = getRandomLetter();
        document.getElementById('selectedLetter').innerText = randomLetter;
    }, 100); // تحديد حرف عشواؐي على كل 0.1 ثانية

    // وقف الانميشين و اظهر الحرف العشوائي
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

            // Computer Vision detection put it Here my friendo :)
        })
        .catch((error) => {
            console.error('Error accessing webcam:', error);
            feedbackElement.innerText = 'حدث خطأ عند الوصول إلى الكاميرا.';
        });
}
