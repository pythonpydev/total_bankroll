"""PLO hand evaluation and spr quiz."""

import algo


@app.route('/tables')
def tables():
    """Tables page route"""
    return render_template('tables.html', title='Tables')


@app.route('/form')
def form():
    """Form page route"""
    return render_template('form.html', title='Form')

@app.route('/hand_details', methods=['POST', 'GET'])
def submit_form():
    """Handles form submission and processes data."""
    if request.method == 'POST':
        form_data = algo.process_hand_data(request.form)
        session['form_data'] = form_data

    else: # GET request
        form_data = session.get('form_data', {})
        
    return render_template('hand_details.html', form_data=form_data)

@app.route('/hand_evaluation', methods=['GET'])
def hand_evaluation():
    form_data = session.get('form_data', {})
    hero_eval = form_data.get('hero_eval')
    opp_eval = form_data.get('opp_eval')
    hero_hand_name = form_data.get('hero_hand_name')
    opp_hand_name = form_data.get('opp_hand_name')
    return render_template('hand_evaluation.html', form_data=form_data, hero_eval=hero_eval, opp_eval=opp_eval, hero_hand_name=hero_hand_name, opp_hand_name=opp_hand_name)

@app.route('/decisions')
def decisions():
    """Decisions page route"""
    return render_template('decisions.html', title='Decisions')

@app.route('/spr_strategy')
def spr_strategy():
    """SPR Strategy page route"""
    return render_template('spr_strategy.html', title='SPR Strategy')

