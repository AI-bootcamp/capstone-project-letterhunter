// قائمة بالحروف العربية التي ستختار بشكل عشوائي
const arabicLetters = ['أ', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'هـ', 'و', 'ي'];

// اختيار حرف عشوائي
function getRandomLetter() {
    const randomIndex = Math.floor(Math.random() * arabicLetters.length);
    return arabicLetters[randomIndex];
}

// انيميشن حروف عشوائية
function animateRandomLetters() {
    let iterations = 10; // عدد التكرارات العشوائية لتحديد حرف عشوائي
    let letterInterval = setInterval(function() {
        const randomLetter = getRandomLetter();
        document.getElementById('selectedLetter').innerText = randomLetter;
    }, 100); // تحديد حرف عشوائي على كل 0.1 ثانية

    // وقف الانميشن و اظهر الحرف العشوائي
    setTimeout(function() {
        clearInterval(letterInterval); // إيقاف التكرار
        const finalLetter = getRandomLetter(); // الحصول على الحرف النهائي
        document.getElementById('selectedLetter').innerText = finalLetter; // عرض الحرف النهائي
        // يمكنك إضافة وظائف إضافية هنا إذا لزم الأمر
    }, 1500); // التوقف بعد 1.5 ثانية
}

// عرض الحرف المختار عند النقر على الزر
document.getElementById('randomLetterBtn').addEventListener('click', function() {
    // بدء انيميشن الحروف العشوائية
    animateRandomLetters();
});
