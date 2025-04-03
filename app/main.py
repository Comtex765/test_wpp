from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hola_mundo():
    return render_template('holaflask.html')
    

    
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=1111)