const tableImages = {
    layout1: {
        src: "../static/images/tables/poker_table_pot_btn_chips1.png",
        name: "Button on seat 1"
    },
    layout2: {
        src:  "../static/images/tables/poker_table_pot_btn_chips2.png",
        name: "Button on seat 2"
    },
    layout3: {
        src: "../static/images/tables/poker_table_pot_btn_chips3.png",
        name: "Button on seat 3"
    },
    layout4: {
        src:  "../static/images/tables/poker_table_pot_btn_chips4.png",
        name: "Button on seat 4"
    },
    layout5: {
        src: "../static/images/tables/poker_table_pot_btn_chips5.png",
        name: "Button on seat 5"
    },
    layout6: {
        src:  "../static/images/tables/poker_table_pot_btn_chips6.png",
        name: "Button on seat 6"
    }
};

let currentLayout = 'layout1';

function getSelectedOption() {
    const dropdown = document.getElementById("btn_ptn");
    const value = dropdown.value;
    return value; 
}

function swapImage() {
    const imageElement = document.getElementById('pokerTable');
    const viewElement = document.getElementById('currentView');

    // Only proceed if elements exist (i.e., we are on the form page)
    if (!imageElement || !viewElement) {
        return; 
    }

    const btnPosition = parseInt(getSelectedOption()); // Parse to integer (1-6)

    // Define the fixed order of roles clockwise, starting with BTN
    const rolesClockwiseFromButton = ["BTN", "SB", "BB", "UTG", "HJ", "CO"];

    // Determine the physical seat number that has the BTN role for the current btnPosition.
    // This maps the dropdown value (btnPosition) to the physical seat where the button image is.
    // Dropdown 1 -> Physical Seat 6 (bottom-left)
    // Dropdown 2 -> Physical Seat 1 (top-left)
    // Dropdown 3 -> Physical Seat 2 (top-middle)
    // Dropdown 4 -> Physical Seat 3 (top-right)
    // Dropdown 5 -> Physical Seat 4 (bottom-right)
    // Dropdown 6 -> Physical Seat 5 (bottom-middle)
    const btnPhysicalSeat = (btnPosition === 1) ? 6 : (btnPosition - 1);

    let newLayout = 'layout' + btnPosition;

    imageElement.style.opacity = '0.7';
    setTimeout(() => {
        imageElement.src = tableImages[newLayout].src;
        viewElement.textContent = tableImages[newLayout].name;
        imageElement.style.opacity = '1';
        currentLayout = newLayout;
    }, 150);
}

document.addEventListener('DOMContentLoaded', (event) => {
    const currentViewElement = document.getElementById('currentView');
    if (currentViewElement) {
        // Initialize the current view text and seat labels on page load
        currentViewElement.textContent = tableImages[currentLayout].name;
        // Call swapImage once to set initial labels based on default dropdown value
        swapImage();
    }
});