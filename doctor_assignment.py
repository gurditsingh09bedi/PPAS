import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import logging

logging.basicConfig(filename='doctor_assignment.log', level=logging.ERROR)

def load_doctor_data(file_path):
    try:
        doctor_data = pd.read_csv(file_path)
        print("Doctor data loaded successfully.")
        return doctor_data
    except Exception as e:
        logging.error(f"Error loading doctor data: {e}")
        print(f"Error loading doctor data: {e}")
        return None

def train_doctor_model(doctor_data):
    try:
        required_columns = ['Specialization', 'SubSpecialization', 'Experience', 'Department']
        
        X = doctor_data[required_columns]
        y = doctor_data['Name']

        label_encoders = {}
        for column in X.columns:
            if X[column].dtype == 'object':
                le = LabelEncoder()
                X.loc[:, column] = le.fit_transform(X[column])
                label_encoders[column] = le

        y_encoder = LabelEncoder()
        y = y_encoder.fit_transform(y)
        
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        knn = KNeighborsClassifier()
        param_grid = {
            'n_neighbors': range(1, 20),
            'weights': ['uniform', 'distance'],
            'metric': ['euclidean', 'manhattan', 'minkowski']
        }
        
        stratified_kfold = StratifiedKFold(n_splits=3)
        
        grid_search = GridSearchCV(knn, param_grid, cv=stratified_kfold, scoring='accuracy')
        grid_search.fit(X_train, y_train)
        
        best_model = grid_search.best_estimator_
        print(f"Best KNN Parameters: {grid_search.best_params_}")
        
        y_pred = best_model.predict(X_test)
        accuracy = best_model.score(X_test, y_test)
        print(f"Model Accuracy after tuning: {accuracy:.2f}")
        
        labels = best_model.classes_
        print_classification_report(y_test, y_pred, y_encoder, labels)
        print_confusion_matrix(y_test, y_pred, y_encoder, labels)
        
        return best_model, label_encoders, y_encoder, required_columns, scaler
    except Exception as e:
        logging.error(f"Error in training doctor model: {e}")
        print(f"Error in training doctor model: {e}")
        return None, None, None, None, None

def assign_doctor(specialization, model, label_encoders, y_encoder, doctor_data, feature_names, scaler):
    try:
        most_common_sub_specialization = doctor_data['SubSpecialization'].mode()[0]
        most_common_department = doctor_data['Department'].mode()[0]
        most_common_experience = doctor_data['Experience'].mean()

        input_data = pd.DataFrame([{
            'Specialization': specialization,
            'SubSpecialization': most_common_sub_specialization,
            'Experience': most_common_experience,
            'Department': most_common_department
        }])

        input_data = input_data[feature_names]

        for column in input_data.columns:
            if column in label_encoders:
                input_data.loc[:, column] = label_encoders[column].transform(input_data[column].astype(str))
        
        input_data = scaler.transform(input_data)
        
        predicted_label = model.predict(input_data)
        
        predicted_doctor_name = y_encoder.inverse_transform(predicted_label)[0]
        
        doctor_info = doctor_data[doctor_data['Name'] == predicted_doctor_name].iloc[0]
        
        return {
            'DoctorID': doctor_info['DoctorID'],
            'Name': doctor_info['Name'],
            'Specialization': doctor_info['Specialization'],
            'SubSpecialization': doctor_info['SubSpecialization']
        }
    except Exception as e:
        logging.error(f"Error in assigning doctor: {e}")
        print(f"Error in assigning doctor: {e}")
        return {
            'DoctorID': 'Unknown',
            'Name': 'Unknown',
            'Specialization': 'Unknown',
            'SubSpecialization': 'Unknown'
        }

def print_confusion_matrix(y_test, y_pred, y_encoder, labels):
    try:
        cm = confusion_matrix(y_test, y_pred, labels=labels)
        print("Confusion Matrix:")
        print(cm)
    except Exception as e:
        logging.error(f"Error printing confusion matrix: {e}")
        print(f"Error printing confusion matrix: {e}")

def print_classification_report(y_test, y_pred, y_encoder, labels):
    try:
        target_names = y_encoder.inverse_transform(labels)
        report = classification_report(y_test, y_pred, labels=labels, target_names=target_names)
        print("Classification Report:")
        print(report)
    except Exception as e:
        logging.error(f"Error printing classification report: {e}")
        print(f"Error printing classification report: {e}")
