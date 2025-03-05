const arabicLetters = [
    'ط', 'م', 'ن', 'س', 'ع', 'ح', 'ك', 'ظ', 'غ', 'ت',
    'ف', 'ش', 'خ', 'ب', 'ل', 'و', 'ق', 'د', 'ز', 'ج',
    'ص', 'ر', 'ث', 'ض', 'ه', 'ذ', 'ي', 'ا'
];

function getRandomLetter() {
    const randomIndex = Math.floor(Math.random() * arabicLetters.length);
    return arabicLetters[randomIndex];
}

function animateRandomLetters() {
    let iterations = 10;
    let letterInterval = setInterval(function() {
        const randomLetter = getRandomLetter();
        document.getElementById('selectedLetter').innerText = randomLetter;
    }, 100);

    setTimeout(function() {
        clearInterval(letterInterval);
        const finalLetter = getRandomLetter();
        document.getElementById('selectedLetter').innerText = finalLetter;
    }, 1500);
}

document.getElementById('randomLetterBtn').addEventListener('click', function() {
    animateRandomLetters();
});
