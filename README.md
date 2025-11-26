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
      py -3.11 -m venv robot_venv
   ```

   - **On macOS/Linux:**

   ```bash
      python3.11 -m venv robot_venv
   ```

   If Python 3.11.9 is already your default version, you can simply run:

   ```bash
      python -m venv robot_venv
   ```

   > ⚠️ **Important**: Make sure you're using Python 3.11.9 to create the virtual environment, as other versions may cause compatibility issues.

3. **Activate the Virtual Environment**

   - **On Windows (cmd or PowerShell):**

     ```bash
     .\robot_venv\Scripts\activate
     ```

   - **On macOS/Linux:**

     ```bash
     source robot_venv/bin/activate
     ```

     > (You should see `(robot_venv)` at the beginning of your terminal prompt.)

4. **Verify Python Version in Virtual Environment**

   With the `(robot_venv)` active, check the Python version:

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
   python -c "import mediapipe, cv2, numpy, ikpy; print('All packages are installed correctly.')"
   ```

   If no errors appear, the installation was successful.

---

## 3. Configure Webots

You must configure Webots to use the Python interpreter from your new virtual environment; otherwise, it won’t find the installed libraries.

1. Open **Webots**.
2. Go to the top menu: `Tools` → `Preferences...`.
3. In the **General** tab, find the **python command** field.
4. Click **Select...**.
5. Navigate to your project folder → `robot_venv` →
   - **Windows:** `robot_venv\Scripts\python.exe`
   - **macOS/Linux:** `robot_venv/bin/python`
6. Click **OK** or **Apply**.
7. **Restart Webots** for the change to take effect.

> ⚠️ **Note:** In some cases, Webots may request the _absolute path_ to the Python executable.  
> Make sure to provide the full path to the `python.exe` inside your virtual environment (e.g.  
> `C:\Users\<username>\Documents\webots\echoarm\robot_venv\Scripts\python.exe`).

---

## 4. Run the Simulation

The system consists of two parts: the Webots Simulator (Server) and the Python GUI (Client). Follow this specific order to establish the connection.

### Step 1: Open the World
1. Launch Webots.

2. Go to File → Open World....

3. Select simulation.wbt located in the worlds/ directory.

4. Pause the simulation if it starts automatically.

### Step 2: Launch the GUI
1. Open a terminal/command prompt.

2. Activate the virtual environment (see Section 2).
3. Run the GUI script
   ```python
      python gui.py
   ```
4. The GUI window will open. The status indicator should show "DISCONNECTED" (or Red) because the simulation is not running yet.

### Step 3: Start Simulation & Connect

1. Return to the Webots window.

2. Click the Play button (▶) in the top toolbar.

3. Watch the GUI window:

4. Within a few seconds, the status indicator should turn GREEN / "CONNECTED".

5. The Webots console output should display: >>> GUI connected.

### Step 4: Test the System
1. Scan Phase: Wait for the robot camera to scan the patient (watch the percentage overlay in the 3D view).

2. Command: Once the scan is complete, click a button on the GUI (e.g., "TESTA" or "BRACCIO_DX").

3. Action:

   - The GUI log will confirm: Target sent: ...

   - The robot in Webots will perform the desired movement

---

## 5. Troubleshooting

### **Error: "Module not found" in Webots**

- Verify Webots is using the correct Python from your virtual environment
- Restart Webots after changing the Python path

### **Webots doesn't recognize the Python path**

- Use absolute paths instead of relative paths
- Make sure the virtual environment is activated when checking the Python path

### **Error: "Module not found" in Webots console**
- This means Webots is using the wrong Python interpreter.
- Double-check Section 3 and ensure the path points to `robot_venv` and not the system Python.
- Restart Webots after changing the path.

### **Error: "ModuleNotFoundError: No module named 'tkinter'"**
This error occurs when launching `gui.py` if the system-level Tkinter library is missing (required by CustomTkinter).
