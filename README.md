# Garmin Planner
This is a Python program reads a YAML configuration file to create and schedule workouts on Garmin Connect. It remove the needs of manual workout management on the garmin connect web by automating the creation and scheduelling processes in bulk. 

## Motivation
Garmin users would know how much of a pain in the A it is to create and manage workouts on garmin connect, especially when you are following a structured marathon plan. I wrote this Garmin Planner to simplify the planning and scheduling of workouts, so we all can hit our PBs.


## Features

- **Workout Creations**: Create various types of workouts (e.g., intervals, easy runs) with associated details like warmup and cooldown periods on garmin connect.
- **Scheduling**: Schedulling workouts created on garmin connect.

## Input YAML Structure

Your YAML configuration should include the following sections:

1. **User Credentials**:
   - `email`: Your Garmin Connect email address.
   - `password`: Your Garmin Connect password.

2. **Settings**:
   - `deleteSameNameWorkout`: A boolean indicating whether to delete existing workouts with the same name during creation of workout.

3. **Definitions** (optional):
   - A set of predefined values can be used in workout creation, this is optional you can use raw value instead of using this.

4. **Workouts**:
   - Define each workout details for workout creation.

5. **Schedule Plan**:
   - Specify the start date and the sequence of workouts for workout schedulling. 
   - (This will get all the workouts created on garmin connect, schedule them based on the workout name, if the workout is not found on garmin connect it will skip the day) 

### Sample YAML Structure

```yaml
email: "example@gmail.com"
password: "password"

settings:
  deleteSameNameWorkout: true

definitions:
  GA: 6:35-7:00
  Threshold: 5:20-5:45
  VO2MaxP: 3:30-4:00

workouts:
  interval_Vo2Max:
    - warmup: 15min @H(z2)
    - repeat(8):
      - run: 30sec @P($VO2MaxP) # can use definition here or raw value 3:30-4:00
      - recovery: 1200m
    - cooldown: 15min @H(z2)

schedulePlan:
  start_from: 2024-10-08
  workouts: 
    - interval_Vo2Max   # will be schedule on 2024-10-08
    - ga_5k             # will be schedule on 2024-10-09
    - rest              # if no "rest" workout found on garmin connect, skip this day
```

The interval_Vo2Max defined above translate to garmin plan below:
![garmin plan of interval_Vo2Max](image.png)

## Installation

Follow these steps to set up the project locally:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/your_project.git

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt

3. **Run the program:**
    ```bash
    python -m garmin_planner sampleInput.yaml