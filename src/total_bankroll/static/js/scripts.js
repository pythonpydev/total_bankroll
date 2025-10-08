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
        randomButton.addEventListener('click', function () {
            const ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'];
            const suits = ['s', 'h', 'd', 'c'];
            const deck = suits.flatMap(suit => ranks.map(rank => rank + suit));
 
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
            document.getElementById('board').value = dealCards(3);
 
            // --- Realistic Scenario Generation ---
            const sb = 1;
            const bb = 2;
            const startingStackBB = 100; // Standard 100bb stack
            const startingStack = startingStackBB * bb;
 
            document.getElementById('small_blind').value = sb;
            document.getElementById('big_blind').value = bb;
 
            // Simulate a simple pre-flop scenario: single raise and a call
            const openRaiseSizeBB = 3; // A standard 3x open
            const openRaiseSize = openRaiseSizeBB * bb;
 
            // Pot on the flop: SB post + BB post + Raiser's bet + Caller's bet
            const potOnFlop = sb + bb + openRaiseSize + openRaiseSize;
 
            // Stacks on the flop
            let heroStack = startingStack;
            let opponentStack = startingStack;
 
            // Randomly decide who was in the blinds to make it more varied
            const heroIsInBlinds = Math.random() < 0.5;
            const opponentIsInBlinds = !heroIsInBlinds && Math.random() < 0.5;
 
            if (heroIsInBlinds) {
                heroStack -= (Math.random() < 0.5 ? sb : bb); // Assume hero was SB or BB
            }
            if (opponentIsInBlinds) {
                opponentStack -= (Math.random() < 0.5 ? sb : bb);
            }
 
            // Both players put in the raise amount to see the flop
            heroStack -= openRaiseSize;
            opponentStack -= openRaiseSize;
 
            document.getElementById('hero_stack').value = heroStack.toFixed(0);
            document.getElementById('opponent_stack').value = opponentStack.toFixed(0);
            document.getElementById('pot_size').value = potOnFlop;

            // Randomize bet size, from 0 up to the pot size.
            // Make a bet ~66% of the time to simulate checking.
            let randomBetSize = 0;
            if (Math.random() < 0.66) {
                randomBetSize = Math.floor(Math.random() * (potOnFlop + 1));
            }
            document.getElementById('bet_size').value = randomBetSize;
 
            // Randomize positions, ensuring they are not the same
            const positionOptions = Array.from(document.getElementById('hero_position').options);
            let heroPosIndex = Math.floor(Math.random() * positionOptions.length);
            let oppPosIndex;
            do {
                oppPosIndex = Math.floor(Math.random() * positionOptions.length);
            } while (heroPosIndex === oppPosIndex);

             document.getElementById('hero_position').selectedIndex = heroPosIndex;
             document.getElementById('opponent_position').selectedIndex = oppPosIndex;
         });
     }

    // --- Hand Strength Evaluator Randomizer ---
    const randomHandButton = document.getElementById('random-hand-button');
    if (randomHandButton) {
        randomHandButton.addEventListener('click', function() {
            const ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'];
            const suits = ['s', 'h', 'd', 'c'];
            const deck = suits.flatMap(suit => ranks.map(rank => rank + suit));

            // Fisher-Yates shuffle
            for (let i = deck.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [deck[i], deck[j]] = [deck[j], deck[i]];
            }

            // Deal 4 cards for the hand
            const randomHand = deck.splice(0, 4).join('');
            document.getElementById('hand').value = randomHand;

            // Select a random position
            const positionSelect = document.getElementById('position');
            if (positionSelect && positionSelect.options.length > 0) {
                const randomIndex = Math.floor(Math.random() * positionSelect.options.length);
                positionSelect.selectedIndex = randomIndex;
            }
        });
    }
 });
