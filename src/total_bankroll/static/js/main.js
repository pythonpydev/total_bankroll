const tableImages = {
    layout1: { src: "../static/images/tables/poker_table_pot_btn_chips1.png", name: "Button on seat 1" },
    layout2: { src: "../static/images/tables/poker_table_pot_btn_chips2.png", name: "Button on seat 2" },
    layout3: { src: "../static/images/tables/poker_table_pot_btn_chips3.png", name: "Button on seat 3" },
    layout4: { src: "../static/images/tables/poker_table_pot_btn_chips4.png", name: "Button on seat 4" },
    layout5: { src: "../static/images/tables/poker_table_pot_btn_chips5.png", name: "Button on seat 5" },
    layout6: { src: "../static/images/tables/poker_table_pot_btn_chips6.png", name: "Button on seat 6" }
};

function updateSeatLabels(btnPosition) {
    const rolesClockwiseFromButton = ["BTN", "SB", "BB", "UTG", "HJ", "CO"];
    const btnPhysicalSeat = (btnPosition === 1) ? 6 : (btnPosition - 1);
    
    for (let i = 1; i <= 6; i++) {
        const seatIndex = (i - btnPhysicalSeat + 6) % 6;
        const role = rolesClockwiseFromButton[seatIndex];
        const seatElement = document.getElementById(`seat-${i}`);
        if (seatElement) {
            const positionLabel = seatElement.querySelector('.position-label');
            if (positionLabel) {
                positionLabel.textContent = role;
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', (event) => {
    const currentViewElement = document.getElementById('currentView');
    
    if (currentViewElement) {
        const match = currentViewElement.textContent.match(/Button on seat (\d)/);
        const btnPosition = match ? parseInt(match[1]) : 1;
        updateSeatLabels(btnPosition);
    }

    const buttons = document.querySelectorAll('.button-group button');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const btnPosition = parseInt(button.value);
            updateSeatLabels(btnPosition); // Update labels immediately
        });
    });
});