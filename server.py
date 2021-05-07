from waitress import serve
import W
serve(W.app, host='0.0.0.0', port=8080)