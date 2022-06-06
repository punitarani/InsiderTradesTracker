# Main file

import sys
from streamlit import cli as stcli

if __name__ == '__main__':
    # Run Streamlit App
    sys.argv = ["streamlit", "run", "streamlit_app.py"]
    sys.exit(stcli.main())
