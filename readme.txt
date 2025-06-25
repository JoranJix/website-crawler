webcrawler_app/
├── webcrawler.py        ← the crawler logic (translated to English)
├── crawler_gui.py       ← the Streamlit user interface
├── requirements.txt     ← with all your dependencies

python -m venv venv
.\venv\Scripts\activate     # On Windows




pip install -r requirements.txt

python -m pip install streamlit

python -m streamlit run crawler_gui.py

pyinstaller --noconfirm --onefile --windowed crawler_gui.py


🗂️ Project Structure
webcrawler_project/
├── crawler_cli.py
├── crawler_gui.py
├── webcrawler.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml


- The gui service gives you a browser interface at http://localhost:8501
- The cli service will run the crawler once and exit — perfect for automation

📦 How to Use It
- Build & run all services:
docker-compose up --build
- Want to run only the GUI?
docker-compose up gui
- Want to run only the CLI job?
docker-compose run --rm cli
- Stop services:
docker-compose down



📁 Saving Output Files
By default, output CSVs are saved inside the container. If you'd like to access them from your host system, update your cli service in docker-compose.yml like this:
    volumes:
      - ./output:/app/output


And update your crawler_cli.py to save files in output/filename.csv.


🔧 Step 1: Prepare Your Project
Make sure your project folder contains:
crawler-app/
├── crawler_cli.py
├── crawler_gui.py
├── webcrawler.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml


If you followed the setup I shared earlier, you're all set.

🚀 Step 2: Zip and Upload to Portainer
- Compress your project folder into a .zip file on your local machine.
- Log into Portainer.
- Go to Stacks → Add Stack.
- Give your stack a name (e.g. webcrawler).
- In the Web editor, paste the contents of your docker-compose.yml.
- Scroll down to “Advanced container settings” and upload the zipped project using the “Upload resources” option.
- Click Deploy the stack.

🖥️ Step 3: Access Your Services
- For the GUI, Portainer will expose port 8501 by default — access it via http://your-server-ip:8501.
- The CLI crawler will run on startup and exit. You can re-run it anytime from the Containers view.

✅ Optional Enhancements
- Mount a volume for persistent CSV output:
volumes:
  - webcrawler_data:/app/output
- Add environment variables or schedules via Portainer’s built-in options.


