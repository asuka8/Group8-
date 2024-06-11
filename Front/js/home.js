document.addEventListener("DOMContentLoaded", function() {
    const container = document.querySelector(".container");
    let currentIndex = 0;

    function handleSwipe(offset) {
        if (offset < 0 && currentIndex < 2) { // Swipe left
            currentIndex++;
        } else if (offset > 0 && currentIndex > 0) { // Swipe right
            currentIndex--;
        }
        container.style.transform = `translateX(-${currentIndex * 100}vw)`;
    }

    let startX;

    container.addEventListener("touchstart", function(e) {
        startX = e.touches[0].clientX;
    });

    container.addEventListener("touchmove", function(e) {
        const moveX = e.touches[0].clientX;
        const offset = startX - moveX;

        // Only trigger swipe if the move is significant
        if (Math.abs(offset) > 50) {
            handleSwipe(offset);
            startX = null; // Reset startX to prevent repeated swipes
        }
    });

    window.addEventListener("resize", function() {
        container.style.transform = `translateX(-${currentIndex * 100}vw)`;
    });
});