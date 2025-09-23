/*!
* Start Bootstrap - Creative v7.0.7 (https://startbootstrap.com/theme/creative)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-creative/blob/master/LICENSE)
*/
//
// Scripts
// 

window.addEventListener('DOMContentLoaded', event => {

    // Navbar shrink function
    var navbarShrink = function () {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) {
            return;
        }
        // Always add navbar-shrink class to ensure it's visible
        navbarCollapsible.classList.add('navbar-shrink');
    };

    // Shrink the navbar 
    navbarShrink();

    // Shrink the navbar when page is scrolled
    document.addEventListener('scroll', navbarShrink);

    // Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            rootMargin: '0px 0px -40%',
        });
    };

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

    // Activate SimpleLightbox plugin for portfolio items
    new SimpleLightbox({
        elements: '#portfolio a.portfolio-box'
    });

    // --- PLO Hand Form Randomizer ---
    const randomButton = document.getElementById('random-button');
    if (randomButton) {
        randomButton.addEventListener('click', function() {
            const ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'];
            const suits = ['s', 'h', 'd', 'c'];
            let deck = [];
            for (const suit of suits) {
                for (const rank of ranks) {
                    deck.push(rank + suit);
                }
            }

            // Fisher-Yates shuffle
            for (let i = deck.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [deck[i], deck[j]] = [deck[j], deck[i]];
            }

            function dealCards(num) {
                return deck.splice(0, num).join('');
            }

            // Deal cards for each field
            document.getElementById('hero_hand').value = dealCards(4);
            document.getElementById('opponent_hand').value = dealCards(4);
            
            const boardCardCount = [3, 4, 5][Math.floor(Math.random() * 3)];
            document.getElementById('board').value = dealCards(boardCardCount);

            document.getElementById('small_blind').value = 1;
            document.getElementById('big_blind').value = 2;
            document.getElementById('hero_stack').value = Math.floor(Math.random() * 801) + 200;
            document.getElementById('opponent_stack').value = Math.floor(Math.random() * 801) + 200;

            const potSize = Math.floor(Math.random() * 91) + 10;
            document.getElementById('pot_size').value = potSize;

            const betSize = Math.floor(Math.random() * (potSize + 1));
            document.getElementById('bet_size').value = betSize;

            const positionOptions = Array.from(document.getElementById('hero_position').options);
            document.getElementById('hero_position').selectedIndex = Math.floor(Math.random() * positionOptions.length);
            document.getElementById('opponent_position').selectedIndex = Math.floor(Math.random() * positionOptions.length);
        });
    }
});
