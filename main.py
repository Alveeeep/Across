from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'across_secret_key'


@app.route('/')
def main_page():
    return render_template('main_page.html')


@app.route('/categories')
def categories_page():
    return render_template('categories_page.html')


@app.route('/new')
def new_page():
    return render_template('new_page.html')


@app.route('/categories/shoes')
def shoes_page():
    return render_template('shoes_page.html')


@app.route('/categories/clothes')
def clothes_page():
    return render_template('clothes_page.html')


@app.route('/categories/custom')
def custom_page():
    return render_template('custom_page.html')


def main():
    app.run()


if __name__ == '__main__':
    main()
