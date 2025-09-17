/**
 * Utility functions for sorting and displaying playing cards.
 */

const rankOrder = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'];
const suitOrder = ['s', 'h', 'd', 'c'];

/**
 * Sorts an array of card strings (e.g., ['As', 'Td']) by rank, then suit.
 * @param {string[]} cards - The array of card strings to sort.
 * @returns {string[]} The sorted array of cards.
 */
function sortCards(cards) {
  return cards.sort((a, b) => {
    const rankA = rankOrder.indexOf(a[0]);
    const rankB = rankOrder.indexOf(b[0]);
    if (rankA !== rankB) return rankA - rankB;
    const suitA = suitOrder.indexOf(a[1]);
    const suitB = suitOrder.indexOf(b[1]);
    return suitA - suitB;
  });
}

/**
 * Displays card images in a specified container element.
 * @param {string[]} hand - The array of card strings to display.
 * @param {HTMLElement} container - The DOM element to append the card images to.
 * @param {string} cardImagePath - The base path to the card image directory.
 */
function displayCards(hand, container, cardImagePath) {
  hand.forEach(card => {
    const img = document.createElement('img');
    img.src = `${cardImagePath}${card}.png`;
    img.alt = card;
    img.classList.add('card-image');
    container.appendChild(img);
  });
}