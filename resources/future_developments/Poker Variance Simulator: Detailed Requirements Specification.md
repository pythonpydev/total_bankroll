Poker Variance Tool

### **Poker Variance Simulator: Detailed Requirements Specification**

#### **1. Overview**

The Poker Variance Simulator is a web-based tool designed to help poker players understand the impact of statistical variance on their bankroll over a specified number of hands. By inputting their estimated performance metrics, users will receive a visual simulation and a detailed statistical breakdown of potential outcomes, illustrating the difference between long-term expectation (EV) and short-term results.

#### **2. Data Inputs (User-Provided Parameters)**

The user interface will present a form requiring the following inputs. All fields must be numeric.

- **Winrate (BB/100)**
  
  - **Description:** The user's estimated or "true" win rate, expressed in big blinds won per 100 hands. This is the central metric for calculating expected value.
  - **Type:** Required, Floating-Point Number (e.g., `2.5`, `-1.5`).
  - **Default Value:** `2.5`

- **Standard Deviation (BB/100)**
  
  - **Description:** A measure of the volatility of the user's results, expressed in big blinds per 100 hands. Higher values indicate larger swings. The UI should provide examples (e.g., "Typical values: 80-120 for NLHE, 120-150 for PLO").
  - **Type:** Required, Floating-Point Number (e.g., `100.0`).
  - **Default Value:** `100.0`

- **Number of Hands**
  
  - **Description:** The total number of hands to be simulated. This represents the sample size over which the variance will be projected.
  - **Type:** Required, Integer (e.g., `100000`).
  - **Default Value:** `100000`

- **Observed Winrate (BB/100)**
  
  - **Description:** The user's actual, measured win rate over the specified number of hands. This allows for probabilistic analysis comparing a short-term result to a long-term expectation.
  - **Type:** Optional, Floating-Point Number (e.g., `10.0`).
  - **Default Value:** None (empty).

#### **3. Processes (Backend Calculations & Simulation)**

Upon form submission, the backend will perform the following processes:

1. **Input Validation:**
   
   - Verify that all required inputs are present and can be converted to the correct numeric types (float or integer).
   - If validation fails, the page should be re-rendered with an appropriate error message (e.g., "Invalid input. Please enter valid numbers.").

2. **Core Statistical Calculations:**
   
   - **Expected Winnings (Total BB):** Calculate the total expected profit over the sample.
     - *Formula:* `(Winrate / 100) * Number of Hands`
   - **Total Standard Deviation (Total BB):** Calculate the standard deviation for the entire sample of hands.
     - *Formula:* `Standard Deviation (BB/100) * sqrt(Number of Hands / 100)`

3. **Confidence Interval Calculation:**
   
   - Calculate the range of outcomes for 70% and 95% confidence levels. This is done by finding the margin of error around the expected winnings.
   - **70% Confidence Interval:** `Expected Winnings ± (Z-score_70 * Total Standard Deviation)` where `Z-score_70` is approx. 1.04.
   - **95% Confidence Interval:** `Expected Winnings ± (Z-score_95 * Total Standard Deviation)` where `Z-score_95` is approx. 1.96.

4. **Probabilistic Calculations:**
   
   - **Probability of Loss:** Calculate the chance that the user's total winnings will be less than zero after the specified number of hands. This is derived from the normal distribution's cumulative distribution function (CDF).
     - *Formula:* `norm.cdf(0, loc=Expected Winnings, scale=Total Standard Deviation)`
   - **Probability of Running At or Above Observed Winrate:** If an observed winrate is provided, calculate the probability of achieving that result or better, given the "true" winrate.
     - *Process:* Calculate the Z-score for the observed outcome and find the area under the curve above that score.
   - **Minimum Bankroll for <5% Risk of Ruin:** Calculate the suggested bankroll size needed to have a less than 5% chance of going broke, assuming the user plays indefinitely with the specified win rate and standard deviation.
     - *Formula (Approximation):* `-(Standard Deviation^2 / (2 * Winrate)) * ln(0.05)`

5. **Graph Data Simulation (Monte Carlo Method):**
   
   - Generate a fixed number of sample paths (e.g., 20 simulations).
   - For each simulation:
     - Initialize a `current_bankroll` at 0.
     - Loop from 1 to `Number of Hands`. In each iteration, simulate a single hand's result using a random number drawn from a normal distribution with a mean of `(Winrate / 100)` and a standard deviation of `(Std Dev / sqrt(100))`.
     - Add the hand's result to `current_bankroll` and store the `(hand_number, current_bankroll)` coordinate pair.
   - Generate a separate data set for the **Expected Value (EV) Line**, which is a straight line from (0, 0) to `(Number of Hands, Expected Winnings)`.

#### **4. Outputs (Results Presented to User)**

After the processes are complete, the page will reload to display the following outputs:

1. **Graphical Simulation:**
   
   - A line chart will be displayed.
   - **X-Axis:** "Number of Hands".
   - **Y-Axis:** "Winnings (in Big Blinds)".
   - **Data Series:**
     - 20 semi-transparent, multi-colored lines, each representing one simulated bankroll journey.
     - One prominent, dashed green line representing the straight path of Expected Value (EV).
   - **Interactivity:** The chart will feature tooltips that appear on hover, showing the specific hand number and winnings in BB for each sample path.

2. **Numerical Analysis Table ("Variance in Numbers"):**
   
   - A clearly formatted table will display the key statistical results, with values formatted for readability (e.g., using commas for thousands and rounding to 2-4 decimal places).
   - **Expected Winnings:** Displayed in total BB.
   - **Standard Deviation:** Displayed in total BB over the sample and as a BB/100 rate.
   - **70% Confidence Interval:** Displayed as a range in total BB and as a BB/100 rate.
   - **95% Confidence Interval:** Displayed as a range in total BB and as a BB/100 rate.
   - **Probability of Loss:** Displayed as a percentage.
   - **Probability of Running At or Above Observed WR:** (Displayed only if an observed winrate was provided). Displayed as a percentage.
   - **Minimum Bankroll for <5% Risk of Ruin:** Displayed in total BB.

This specification provides a comprehensive blueprint for building the Poker Variance Simulator, ensuring all functional and user-facing requirements are clearly defined.

Building a Poker Variance Simulator is a fantastic project that combines web development with interesting statistical concepts. It's a powerful educational tool.

Based on your request and the example provided, here is a step-by-step plan outlining what needs to be done to build this feature. I will describe each step without providing any code changes at this stage.

---

### **Step 1: Create the Backend Foundation (Flask Blueprint and Route)**

**Description:** The first step is to set up the server-side structure that will power the tool. We will create a new, dedicated Python file for a Flask Blueprint. This keeps the simulator's logic separate from other parts of your application, making the code cleaner and easier to maintain. Inside this file, we'll define a new route (e.g., `/tools/variance-simulator`) that will listen for user requests. This route will be responsible for two things:

1. Handling `GET` requests to display the initial, empty simulator page to the user.
2. Handling `POST` requests when the user fills out the form and clicks "Run Simulation".

### **Step 2: Design the Frontend User Interface (HTML Template)**

**Description:** Next, we need to create the webpage that the user will interact with. This involves creating a new HTML template file. This template will contain:

1. **An Input Form:** A form with fields for the user to enter the required parameters: "Winrate (BB/100)", "Standard Deviation (BB/100)", "Number of Hands", and an optional "Observed Winrate (BB/100)".
2. **A "Run Simulation" Button:** To submit the form to the backend route we created in Step 1.
3. **Result Placeholders:** Designated areas on the page where the results will be displayed after the calculation is complete. This includes a `<canvas>` element for the graph and a `<table>` structure for the "Variance in Numbers" section. This page will extend your site's main `base.html` to ensure it has the same navigation, header, and footer as the rest of your site.

### **Step 3: Implement the Core Statistical Calculations (Backend Logic)**

**Description:** This is the heart of the tool. When the user submits the form, the Flask route will execute Python code to perform all the necessary statistical calculations based on the user's input. This logic will include:

1. **Calculating Expected Winnings:** A simple calculation: `(Winrate / 100) * Number of Hands`.
2. **Calculating Total Standard Deviation:** Determine the standard deviation over the entire sample of hands.
3. **Calculating Confidence Intervals:** Use statistical libraries (like SciPy) to find the 70% and 95% confidence intervals, which show the likely range of outcomes.
4. **Calculating Probability of Loss:** Determine the statistical chance that a player will end up with a negative result after the specified number of hands.
5. **Calculating Risk of Ruin:** Implement a formula to estimate the bankroll size needed to keep the risk of going broke below 5%.
6. **Calculating Observed Winrate Probability:** If the user provides an observed winrate, calculate the probability of achieving that result (or better) given their stated "true" winrate.

All of these calculated values will be packaged into a results object to be sent back to the frontend.

### **Step 4: Generate the Graph Data (Backend Simulation)**

**Description:** To create the compelling visual graph, the backend needs to run a Monte Carlo simulation. This involves:

1. Creating a function that simulates a series of random bankroll journeys (e.g., 20 different samples).
2. For each sample, it will loop through the total number of hands, generating a random outcome for each hand based on the user's win rate and standard deviation.
3. It will track the cumulative winnings at each step.
4. This process generates the data points (x, y coordinates) for each of the wavy lines on the graph.
5. A separate, straight line representing the "Expected Value" (EV) will also be generated. This data will be passed to the frontend along with the statistical results from Step 3.

### **Step 5: Visualize the Results (Frontend JavaScript)**

**Description:** With the data provided by the backend, the final step is to render it on the user's screen. This will be done with JavaScript in the HTML template created in Step 2.

1. **Render the Graph:** Using the Chart.js library (which is already part of your project), we will write JavaScript to take the simulation data and draw the line chart on the `<canvas>` element. This includes plotting the 20 sample paths and the EV line, and configuring the chart axes and tooltips.
2. **Display Numerical Data:** The statistical results (confidence intervals, probability of loss, etc.) will be dynamically inserted into the "Variance in Numbers" table using Jinja2 template syntax. The page will conditionally show the results section only after a simulation has been run.

### **Step 6: Integrate the Tool into the Website**

**Description:** The final step is to make the new tool discoverable. This involves editing the main "Tools" page (`tools.html`) to add a new card or link that directs users to the `/tools/variance-simulator` page, completing the integration of the new feature into your site.

Following these steps in order will result in a fully functional and integrated Poker Variance Simulator.
