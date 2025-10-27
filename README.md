# Simulation Setup Guide

This guide explains how to configure the necessary Python environment and run the Webots simulation.

---

## 1. Prerequisites

- Webots (R2025a or later recommended)
- Python 3.11.9
- Git

---

## 2. Initial Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/andrebellu/echoarm.git
   cd echoarm
   ```

2. **Create the Virtual Environment (`venv`)**

   This project requires Python 3.11.9 specifically.
   A virtual environment ensures that all dependencies are isolated and managed correctly.

   ```bash
   # Check your current Python version
   python --version
   # It should show: Python 3.11.9
   ```

   If you have multiple Python versions installed, create the virtual environment explicitly with Python 3.11:

   - **On Windows:**

   ```bash
      py -3.11 -m venv .venv
   ```

   - **On macOS/Linux:**

   ```bash
      python3.11 -m venv .venv
   ```

   If Python 3.11.9 is already your default version, you can simply run:

   ```bash
      python -m venv .venv
   ```

   > ⚠️ **Important**: Make sure you're using Python 3.11.9 to create the virtual environment, as other versions may cause compatibility issues.

3. **Activate the Virtual Environment**

   - **On Windows (cmd or PowerShell):**

     ```bash
     .\.venv\Scripts\activate
     ```

   - **On macOS/Linux:**

     ```bash
     source .venv/bin/activate
     ```

     > (You should see `(.venv)` at the beginning of your terminal prompt.)

4. **Verify Python Version in Virtual Environment**

   With the `(.venv)` active, check the Python version:

   ```bash
   python --version
   ```

   This should show: `Python 3.11.9`

5. **Install Required Packages**

   ```bash
   pip install -r requirements.txt
   ```

6. **Verify Installation**

   To ensure everything is set up correctly, run:

   ```bash
   python -c "import mediapipe, cv2, numpy; print('All packages are installed correctly!')"
   ```

   If no errors appear, the installation was successful.

---

## 3. Configure Webots

You must configure Webots to use the Python interpreter from your new virtual environment; otherwise, it won’t find the installed libraries.

1. Open **Webots**.
2. Go to the top menu: `Tools` → `Preferences...`.
3. In the **General** tab, find the **python command** field.
4. Click **Select...**.
5. Navigate to your project folder → `.venv` →
   - **Windows:** `.venv\Scripts\python.exe`
   - **macOS/Linux:** `.venv/bin/python`
6. Click **OK** or **Apply**.
7. **Restart Webots** for the change to take effect.

> ⚠️ **Note:** In some cases, Webots may request the _absolute path_ to the Python executable.  
> Make sure to provide the full path to the `python.exe` inside your virtual environment (e.g.  
> `C:\Users\<username>\Documents\webots\echoarm\.venv\Scripts\python.exe`).

---

## 4. Run the Simulation

1. Open the desired world file (`.wbt`) in Webots.
2. In the Scene Tree (left panel), select your robot node.
3. Ensure the `controller` field is set to the correct Python script (e.g., `echoarm`).
4. Click **Reload** (or press `Ctrl+R`) and then **Play** to start the simulation.

Depending on which world you open:

- In the **motor test world**, the robot will move around to verify the correct behavior of its motors.
- In the **camera test world**, a fixed camera will stream video processed through **OpenCV** and **MediaPipe**, allowing you to verify the computer vision pipeline.

---

## 5. Troubleshooting

### **Error: "Module not found" in Webots**

- Verify Webots is using the correct Python from your virtual environment
- Restart Webots after changing the Python path

### **Webots doesn't recognize the Python path**

- Use absolute paths instead of relative paths
- Make sure the virtual environment is activated when checking the Python path
