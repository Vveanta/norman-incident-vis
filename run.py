import sys
import os
from waitress import serve  # type: ignore

# Add the project directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=5200)
    # app.run(debug=True)  
