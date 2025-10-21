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

   This project requires specific Python libraries.  
   A virtual environment ensures that all dependencies are isolated and managed correctly.

   ```bash
   # 'venv' will be the name of the environment folder
   python -m venv venv
   ```

3. **Activate the Virtual Environment**

   - **On Windows (cmd or PowerShell):**

     ```bash
     .\venv\Scripts\activate
     ```

   - **On macOS/Linux:**

     ```bash
     source venv/bin/activate
     ```

     > (You should see `(venv)` at the beginning of your terminal prompt.)

4. **Install Dependencies**

   With the `venv` active, install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

---

## 3. Configure Webots

You must configure Webots to use the Python interpreter from your new virtual environment; otherwise, it won’t find the installed libraries.

1. Open **Webots**.
2. Go to the top menu: `Tools` → `Preferences...`.
3. In the **General** tab, find the **python command** field.
4. Click **Select...**.
5. Navigate to your project folder → `venv` →
   - **Windows:** `venv\Scripts\python.exe`
   - **macOS/Linux:** `venv/bin/python`
6. Click **OK** or **Apply**.
7. **Restart Webots** for the change to take effect.

> ⚠️ **Note:** In some cases, Webots may request the _absolute path_ to the Python executable.  
> Make sure to provide the full path to the `python.exe` inside your virtual environment (e.g.  
> `C:\Users\<username>\Documents\webots\echoarm\venv\Scripts\python.exe`).

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
