document.addEventListener('DOMContentLoaded', function () {
    const backToTopButton = document.getElementById("backToTopBtn");

    if (backToTopButton) {
        // When the user scrolls down 100px from the top of the document, show the button
        window.onscroll = function() {
            if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
                backToTopButton.style.display = "block";
            } else {
                backToTopButton.style.display = "none";
            }
        };

        // When the user clicks on the button, scroll to the top of the document
        backToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});