import flask
import csv
import os
from flask import Flask, render_template, request, redirect, Response, send_file, url_for, jsonify
import pickle
import pandas as pd
from sklearn.preprocessing import QuantileTransformer
import shutil


app = flask.Flask(__name__)
# Load models
arrhythmia_model = pickle.load(open('model/Ha_lr.pickle', 'rb'))
sleep_model = pickle.load(open('model/SA_I_rf.pickle', 'rb'))
stroke_model = pickle.load(open('model/vc_stroke.pickle', 'rb'))

# Define feature arrays for each model
arrhythmia_features = ["Bpm", "Sleep", "Intensity"]
sleep_features = ["sex", "Age", "Sleep Duration", "Bpm", "Daily Steps", "Systolic_BP", "Diastolic_BP"]
stroke_features = ["sex", "age", "hypertension", "heart_disease", "ever_married", "Residence_type", "bmi",
                   "smoking_status", "work_type_Govt job", "work_type_Private", "work_type_Self-employed"]


@app.route('/get_results', methods=['POST'])
def get_results():

    # Load the data from the CSV file
    data = pd.read_csv(r'merged/merged_data.csv')

    # Apply the models and generate diagnosis results
    arrhythmia_pred = arrhythmia_model.predict(data[arrhythmia_features])
    sleep_pred = sleep_model.predict(data[sleep_features])
    stroke_pred = stroke_model.predict(data[stroke_features])

    # Calculate diagnosis messages
    messages = []

    # Calculate arrhythmia percentage
    arrhythmia_percentage = (arrhythmia_pred == 1).mean() * 100
    if arrhythmia_percentage >= 80:
        messages.append("You might have arrhythmia. Consult a doctor.")

    # Count occurrences of Sleep apnea and Insomnia
    sleep_counts = pd.Series(sleep_pred).value_counts()

    # Determine the class predicted more
    most_predicted_class = sleep_counts.idxmax()

    if most_predicted_class == 'Sleep Apnea':
        messages.append("You might have Sleep apnea; consult a medical practitioner.")
    elif most_predicted_class == 'Insomnia':
        messages.append("You might have Insomnia; consult a medical practitioner.")

    # Calculate stroke percentage
    stroke_percentage = (stroke_pred == 1).mean() * 100
    if stroke_percentage >= 80:
        messages.append("You might have had a stroke. Consult a doctor.")

    # If no conditions are met, the person is healthy
    if not messages:
        messages.append("You are healthy, but consult a medical practitioner if concerned about your health.")

    # Return the diagnosis messages as JSON
    return jsonify({"messages": messages})


@app.route('/submit_profile', methods=['POST'])
def submit_profile():
    # Extract form data
    first_name = request.form['First Name']
    last_name = request.form['Last Name']
    age = request.form['age']
    gender = request.form['gender']
    marital_status = request.form['maritalStatus']
    work_type = request.form['workType']
    residence_type = request.form['residenceType']
    heart_disease = request.form['heartDisease']
    bmi = request.form['bmi']
    smoking_status = request.form['smokingStatus']
    physical_activity = request.form['physicalActivity']
    stroke_history = request.form['strokeHistory']
    family_stroke_history = request.form['familyStrokeHistory']
    hypertension = request.form['hypertension']  # Extract hypertension from form data

    # Convert age to a float so it can be standardized
    age = float(age)

    # Convert BMI to float and transform it using the transform_new_bmi function
    bmi = float(bmi)
    transformed_bmi = transform_bmi(bmi)

    # Apply the standard_scaler function to the age
    standardized_age = standard_scaler(pd.Series([age]))
    standardized_age = standardized_age.values[0]

    # Map categorical values to numerical values
    gender_mapping = {'Male': 1, 'Female': 0}
    marital_status_mapping = {'Married': 1, 'Single': 0, 'Divorced': 0}
    work_type_mapping = {
        'Government Job': {'work_type_Govt job': 'TRUE'},
        'Private': {'work_type_Private': 'TRUE'},
        'Self-employed': {'work_type_Self-employed': 'TRUE'},
        'Never worked': {'work_type_Never worked': 'TRUE'}
    }
    residence_type_mapping = {'Urban': 0, 'Rural': 1}
    heart_disease_mapping = {'Yes': 1, 'No': 0}
    smoking_status_mapping = {'Currently Smokes': 1, 'Formerly Smoked': 0, 'Non-smoker': 0}
    stroke_history_mapping = {'Yes': 1, 'No': 0}
    family_stroke_history_mapping = {'Yes': 1, 'No': 0}
    hypertension_mapping = {'Yes': 1, 'No': 0}  # Hypertension mapping

    # Map values
    gender = gender_mapping[gender]
    marital_status = marital_status_mapping[marital_status]
    residence_type = residence_type_mapping[residence_type]
    heart_disease = heart_disease_mapping[heart_disease]
    smoking_status = smoking_status_mapping[smoking_status]
    stroke_history = stroke_history_mapping[stroke_history]
    family_stroke_history = family_stroke_history_mapping[family_stroke_history]
    hypertension = hypertension_mapping[hypertension]  # Map hypertension

    # Create work type columns dictionary
    work_type_columns = {'work_type_Govt job': 'False', 'work_type_Private': 'False',
                         'work_type_Self-employed': 'False', 'work_type_Never worked': 'False'}
    if work_type in work_type_mapping:
        work_type_columns.update(work_type_mapping[work_type])

    # Create CSV file
    filename = f"profiles/{first_name}.csv"
    with open(filename, mode='w', newline='') as file:
        # Write the header, including all work type columns and hypertension
        header = 'first_name,last_name,age,Age,sex,ever_married,Residence_type,heart_disease,hypertension,bmi,smoking_status,physical_activity,stroke_history,family_stroke_history,' + ','.join(
            work_type_columns.keys())
        file.write(header + '\n')

        # Write the data
        data = f"{first_name},{last_name},{standardized_age},{age},{gender},{marital_status},{residence_type},{heart_disease},{hypertension},{transformed_bmi},{smoking_status},{physical_activity},{stroke_history},{family_stroke_history},{','.join(str(work_type_columns[key]) for key in work_type_columns)}"
        file.write(data + '\n')

    return redirect('/dataform')


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/about')
def about():
    return flask.render_template('about.html')


@app.route('/contact')
def contact():
    return flask.render_template('contact.html')


@app.route('/results')
def results():
    return flask.render_template('results.html')


@app.route('/signup')
def signup():
    return flask.render_template('signup.html')


@app.route('/dataform')
def dataform():
    return flask.render_template('dataform.html')


@app.route('/login')
def login():
    return flask.render_template('login.html')


@app.route('/diagnosis')
def diagnosis():
    return flask.render_template('diagnosis.html')


uploads_folder = 'uploads'
profiles_folder = 'profiles'
merged_folder = 'merged'


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        filename = file.filename
        file.save(os.path.join(uploads_folder, filename))

        # Merge the data after file upload
        merge_data(filename)

        return jsonify({'message': 'File uploaded successfully', 'filename': filename})
    return jsonify({'error': 'Unknown error'})


def merge_data(filename):
    # Get the filenames in profiles folder
    profile_filename = os.listdir(profiles_folder)[0]

    # Read data from uploaded and profile CSV files
    uploaded_data = pd.read_csv(os.path.join(uploads_folder, filename))
    profile_data = pd.read_csv(os.path.join(profiles_folder, profile_filename))

    # Duplicate profile data rows to match the number of rows in the uploaded data
    num_rows_to_duplicate = len(uploaded_data) // len(profile_data)
    duplicated_profile_data = pd.concat([profile_data] * num_rows_to_duplicate, ignore_index=True)

    # Merge the duplicated profile data with the uploaded data
    merged_data = pd.concat([uploaded_data, duplicated_profile_data], axis=1)

    # Save the merged data to a new CSV file in the merged folder
    merged_data.to_csv(os.path.join(merged_folder, 'merged_data.csv'), index=False)

    print("Merge complete. Merged data saved in the 'merged' folder.")


@app.route('/merge_files', methods=['POST'])
def merge_files():
    # Define paths to folders
    profiles_folder = 'profiles'
    uploads_folder = 'uploads'
    merged_folder = 'merged'

    # Create merged folder if it doesn't exist
    if not os.path.exists(merged_folder):
        os.makedirs(merged_folder)

    # Get the CSV file from the uploads folder
    upload_files = os.listdir(uploads_folder)
    if len(upload_files) != 1 or not upload_files[0].endswith('.csv'):
        return jsonify({'message': 'Invalid upload file'})

    upload_file = os.path.join(uploads_folder, upload_files[0])

    # Copy the upload CSV file to the merged folder
    shutil.copy(upload_file, merged_folder)

    # Get the CSV file from the profiles folder
    profile_files = os.listdir(profiles_folder)
    if len(profile_files) != 1 or not profile_files[0].endswith('.csv'):
        return jsonify({'message': 'Invalid profile file'})

    profile_file = os.path.join(profiles_folder, profile_files[0])

    # Read the profiles CSV file
    with open(profile_file, 'r') as profile_csv:
        profile_reader = csv.reader(profile_csv)
        profiles_data = list(profile_reader)

    # Read the upload CSV file
    with open(upload_file, 'r') as upload_csv:
        upload_reader = csv.reader(upload_csv)
        upload_data = list(upload_reader)

    # Duplicate profile rows to match the number of rows in the upload file
    num_upload_rows = len(upload_data)
    num_profile_rows = len(profiles_data)
    if num_profile_rows < num_upload_rows:
        profiles_data *= (num_upload_rows // num_profile_rows + 1)

    # Write merged data to a new CSV file
    merged_file = os.path.join(merged_folder, 'merged.csv')
    with open(merged_file, 'w', newline='') as merged_csv:
        writer = csv.writer(merged_csv)
        writer.writerows(profiles_data)

    return jsonify({'message': 'Files merged successfully!'})


def standard_scaler(data):
    # Calculate the mean and standard deviation for each feature
    mean = 51.331127
    std_dev = 21.661450

    # Apply standardization: (value - mean) / standard deviation
    data_scaled = (data - mean) / std_dev

    return data_scaled


# Load the existing BMI data from bmi.csv file
existing_bmi_data = pd.read_csv(r'bmi.csv')

# Create a QuantileTransformer with desired parameters
qt = QuantileTransformer(n_quantiles=500, output_distribution='normal')

# Fit the QuantileTransformer on the existing BMI data
qt.fit(existing_bmi_data[['bmi']])

# Transform the existing BMI data
existing_bmi_data['bmi_transformed'] = qt.transform(existing_bmi_data[['bmi']])


# Function to transform new BMI values
def transform_bmi(new_bmi):
    # Convert new_bmi to a DataFrame
    new_bmi_df = pd.DataFrame({'bmi': [new_bmi]})

    # Apply the transformation to the new BMI value
    transformed_bmi = qt.transform(new_bmi_df)

    # Return the transformed value
    return transformed_bmi[0, 0]


if __name__ == '__main__':
    app.run(debug=True)