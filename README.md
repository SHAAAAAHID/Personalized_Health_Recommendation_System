# Personalized Health Recommendation System

This repository contains the code and data for the Personalized Health Recommendation System project. The project aims to develop a health website capable of harnessing individual health data to generate personalized health recommendations, fostering early detection and more effective management of health issues. The system leverages various Machine Learning (ML) algorithms to predict diseases like arrhythmia, sleep apnea, insomnia, and stroke.

## Disease Prediction Performance Metrics

### Heart Arrhythmia
- **Model:** Logistic Regression
  - Precision: 90.0
  - Recall: 94.5
  - F1 Score: 91.5
  - Accuracy: 93.5
  - Cross Validation: 94.7

### Sleep Apnea
- **Model:** Random Forest Classifier
  - Precision: 90.33
  - Recall: 83.67
  - F1 Score: 85.67
  - Accuracy: 91.07
  - Cross Validation: 91.4

### Stroke
- **Models:** 
  - **Random Forest Classifier**
    - Precision: 92.18
    - Recall: 95.9
    - F1 Score: 94
    - Accuracy: 93.83
  - **Decision Tree**
    - Precision: 95.75
    - Recall: 94.67
    - F1 Score: 95.2
    - Accuracy: 95.19
  - **Voting Classifier**
    - Precision: 96
    - Recall: 96
    - F1 Score: 96
    - Accuracy: 95.68
    - Cross Validation: 95.96

## Usage

1. **Arrhythmia Prediction:**
   - The prediction model for arrhythmia uses Logistic Regression.
   - Navigate to the `arrhythmia` folder.
   - Follow the instructions in the README file within the folder to preprocess the data and run the prediction models.

2. **Sleep Apnea Prediction:**
   - The prediction model for sleep apnea uses a Random Forest Classifier.
   - Navigate to the `sleep_apnea` folder.
   - Follow the instructions in the README file within the folder to preprocess the data and run the prediction models.

3. **Stroke Prediction:**
   - The prediction models for stroke include Random Forest Classifier, Decision Tree, and Voting Classifier.
   - Navigate to the `stroke` folder.
   - Follow the instructions in the README file within the folder to preprocess the data and run the prediction models.

4. **Website Interaction:**
   - Once the Flask server is running, open your web browser and go to `http://127.0.0.1:5000`.
   - Create a health profile, upload data from smart devices, and receive personalized health recommendations.
   - Get recommendations for nearby healthcare facilities based on the predictions.

## Contributions

Contributions are welcome! If you have any ideas for improvements or new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgements

I would like to express my gratitude to my team members for their invaluable contributions to this project:

- Ibrahim Parkar
- Sakshi Jadhav
- Anand Tripathi
- Tanishque Prajapati
- Dr. Vaqar Ansari
