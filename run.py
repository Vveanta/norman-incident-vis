import sys
import os
from waitress import serve  # type: ignore

# Add the project directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    # app.run(debug=True, host="0.0.0.0", port=5200)
    port = int(os.environ.get('PORT', 8000))
    if os.environ.get('FLASK_ENV') == 'production':
        serve(app, host='0.0.0.0', port=port)
    else:
        app.run(debug=True, host='0.0.0.0', port=port)
    # serve(app, host="0.0.0.0", port=5200)
    # app.run(debug=True)  
