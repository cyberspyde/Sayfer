from flask import Flask,request,json

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
	if request.method == 'POST':
		print(request.json)
		return 'Test Success', 200
	else:
		abort(400)

if __name__ == '__main__':
    app.run(debug=True)