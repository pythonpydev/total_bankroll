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
        randomButton.addEventListener('click', () => {
            populateRandomHandData();
        });
    }

    function createDeck() {
        const suits = ['h', 'd', 'c', 's'];
        const ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'];
        let deck = [];
        for (const suit of suits) {
            for (const rank of ranks) {
                deck.push(rank + suit);
            }
        }
        return deck;
    }

    function shuffleDeck(deck) {
        for (let i = deck.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [deck[i], deck[j]] = [deck[j], deck[i]];
        }
    }

    function populateRandomHandData() {
        const deck = createDeck();
        shuffleDeck(deck);

        const dealCards = (num) => {
            let hand = '';
            for (let i = 0; i < num; i++) {
                hand += deck.pop();
            }
            return hand;
        };

        const heroHand = dealCards(4);
        const opponentHand = dealCards(4);
        const board = dealCards(5);

        const positions = ['UTG', 'HJ', 'CO', 'BTN', 'SB', 'BB'];
        let heroPosition = positions[Math.floor(Math.random() * positions.length)];
        let opponentPosition;
        do {
            opponentPosition = positions[Math.floor(Math.random() * positions.length)];
        } while (opponentPosition === heroPosition);

        document.getElementById('small_blind').value = 1;
        document.getElementById('big_blind').value = 2;
        document.getElementById('hero_stack').value = Math.floor(Math.random() * 400) + 100; // 100-499
        document.getElementById('hero_position').value = heroPosition;
        document.getElementById('hero_hand').value = heroHand;
        document.getElementById('opponent_stack').value = Math.floor(Math.random() * 400) + 100; // 100-499
        document.getElementById('opponent_position').value = opponentPosition;
        document.getElementById('opponent_hand').value = opponentHand;
        document.getElementById('board').value = board;
        document.getElementById('pot_size').value = Math.floor(Math.random() * 50) + 10; // 10-59
        document.getElementById('bet_size').value = 0;
    }
});
