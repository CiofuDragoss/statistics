# Statistics: .NET, Flask, Celery

## Description

The application verifies the accuracy and efficiency (execution time) of five algorithms: **NN, K-NN, eigenFaces, K-eigenFaces, Cod**.

It allows the download of results (charts or CSV files) as archives, and it features a user notification system that informs when the result processing is complete (which can take a long time, especially for K-NN).

![front Page](https://github.com/user-attachments/assets/8bd84082-44ab-4096-ac17-d03acb33db84)


**The query feature (interogare ) has not been implemented. It is intended to allow the user to arbitrarily upload a picture and then check it against the uploaded database to see if a match is found.**
## Files

- **app**  
  ASP.NET server and front end. This component is responsible for organization, data processing and handling, and communication with Flask.
  
- **python_alg**  
  Flask & Celery implementation. Contains the necessary algorithms, data processing, plotting & CSV generation, and handles communication with .NET for displaying the results.
![Statistics options](https://github.com/user-attachments/assets/dd3356ef-e873-4d50-b8f4-c545855bb97b)
## Main Features

- **Database Verification:**  
  Checks the input database (e.g., ORL) and its format. It also displays the chosen settings in the format that is sent to Flask.  
  ![erori](https://github.com/user-attachments/assets/92562ac2-c8c3-41da-a939-44285d873b04)

- **Error Handling:**  
  Ensures that all required settings are provided before proceeding.  
  ![image](https://github.com/user-attachments/assets/a1c6a7f2-6813-438f-987f-a11a494dbb09)

- **Session-Based Operation:**  
  Operates on a session basis without requiring user accounts.

- **Asynchronous Processing & Notifications:**  
  Heavy operations are managed asynchronously using Celery, with notifications sent via SignalR.  
  ![notificare](https://github.com/user-attachments/assets/97506351-ea0b-4ebe-89cf-fc6d32627aa7)  
  ![image](https://github.com/user-attachments/assets/ee02652c-7ea7-47e1-939a-2a2e4a5facca)

- **Time Display Option:**  
  When enabled, this option displays charts with timing information.  
  ![image](https://github.com/user-attachments/assets/176e5776-83b9-45bb-bafd-2fa3e17594ec)










