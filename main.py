from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'across_secret_key'


@app.route('/')
def main_page():
    return render_template('main_page.html')


def main():
    app.run()


if __name__ == '__main__':
    main()
