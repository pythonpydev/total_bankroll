import os
from total_bankroll import create_app, db
from total_bankroll.models import Article
from datetime import datetime, UTC

def seed_articles(app, md_directory):
    with app.app_context():
        if not os.path.exists(md_directory):
            print(f"Error: Directory {md_directory} does not exist")
            return
        for filename in os.listdir(md_directory):
            if filename.endswith('.md'):
                with open(os.path.join(md_directory, filename), 'r', encoding='utf-8') as f:
                    content_md = f.read()
                    title = filename.replace('.md', '').replace('-', ' ').title()
                    article = Article(
                        title=title,
                        content_md=content_md,
                        date_published=datetime.now(UTC)
                    )
                    db.session.add(article)
        db.session.commit()
        print("Articles seeded successfully")

if __name__ == '__main__':
    app = create_app()
    md_dir = '/home/ed/MEGA/total_bankroll/resources/articles/markdown'
    seed_articles(app, md_dir(.venv) ed@ed-ThinkPad-L450:~/MEGA/total_bankroll$ flask run
DEBUG:passlib:registered 'bcrypt' handler: <class 'passlib.handlers.bcrypt.bcrypt'>
DEBUG:passlib:registered 'argon2' handler: <class 'passlib.handlers.argon2.argon2'>
DEBUG:passlib:registered 'des_crypt' handler: <class 'passlib.handlers.des_crypt.des_crypt'>
DEBUG:passlib:registered 'pbkdf2_sha256' handler: <class 'passlib.handlers.pbkdf2.pbkdf2_sha256'>
DEBUG:passlib:registered 'pbkdf2_sha512' handler: <class 'passlib.handlers.pbkdf2.pbkdf2_sha512'>
DEBUG:passlib:registered 'sha256_crypt' handler: <class 'passlib.handlers.sha2_crypt.sha256_crypt'>
DEBUG:passlib:registered 'sha512_crypt' handler: <class 'passlib.handlers.sha2_crypt.sha512_crypt'>
DEBUG:passlib:registered 'plaintext' handler: <class 'passlib.handlers.misc.plaintext'>
DEBUG:passlib:registered 'hex_md5' handler: <class 'passlib.handlers.digests.hex_md5'>
INFO:total_bankroll:Successfully loaded optimized PLO hand data from /home/ed/MEGA/total_bankroll/src/total_bankroll/data/plo_hands_rankings.feather (270725 rows)
 * Serving Flask app 'total_bankroll'
 * Debug mode: off
INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
INFO:werkzeug:Press CTRL+C to quit
ERROR:total_bankroll:Exception on / [GET]
Traceback (most recent call last):
  File "/home/ed/MEGA/total_bankroll/.venv/lib/python3.12/site-packages/flask/app.py", line 1511, in wsgi_app
    response = self.full_dispatch_request()
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ed/MEGA/total_bankroll/.venv/lib/python3.12/site-packages/flask/app.py", line 919, in full_dispatch_request
    rv = self.handle_user_exception(e)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ed/MEGA/total_bankroll/.venv/lib/python3.12/site-packages/flask/app.py", line 917, in full_dispatch_request
    rv = self.dispatch_request()
         ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ed/MEGA/total_bankroll/.venv/lib/python3.12/site-packages/flask/app.py", line 902, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ed/MEGA/total_bankroll/src/total_bankroll/routes/home.py", line 15, in home
    return render_template("index.html",
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ed/MEGA/total_bankroll/.venv/lib/python3.12/site-packages/flask/templating.py", line 150, in render_template
    return _render(app, template, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ed/MEGA/total_bankroll/.venv/lib/python3.12/site-packages/flask/templating.py", line 131, in _render
    rv = template.render(context)
         ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ed/MEGA/total_bankroll/.venv/lib/python3.12/site-packages/jinja2/environment.py", line 1295, in render
    self.environment.handle_exception()
  File "/home/ed/MEGA/total_bankroll/.venv/lib/python3.12/site-packages/jinja2/environment.py", line 942, in handle_exception
    raise rewrite_traceback_stack(source=source)
  File "/home/ed/MEGA/total_bankroll/src/total_bankroll/templates/index.html", line 2, in top-level template code
    {% from "_macros.html" import page_header %}
    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ed/MEGA/total_bankroll/src/total_bankroll/templates/base.html", line 73, in top-level template code
    <li><a class="dropdown-item" href="{{ url_for('articles.articles_page') }}">Articles</a></li>
    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ed/MEGA/total_bankroll/.venv/lib/python3.12/site-packages/flask/app.py", line 1121, in url_for
    return self.handle_url_build_error(error, endpoint, values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ed/MEGA/total_bankroll/.venv/lib/python3.12/site-packages/flask/app.py", line 1110, in url_for
    rv = url_adapter.build(  # type: ignore[union-attr]
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ed/MEGA/total_bankroll/.venv/lib/python3.12/site-packages/werkzeug/routing/map.py", line 924, in build
    raise BuildError(endpoint, values, method, self)
werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'articles.articles_page'. Did you mean 'charts.charts_page' instead?
INFO:werkzeug:127.0.0.1 - - [21/Oct/2025 09:21:23] "GET / HTTP/1.1" 500 -
)