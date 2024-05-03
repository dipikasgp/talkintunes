# TalkinTunes

 End to end encrypted Messaging App made using flask and postgres and cryptographic libraries to send messages in crypted tunes

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Detailed Description](#detailed_description)
- [Future Scope](#future_scope)
  
## Installation

1. Clone the repository:

    ```bash
    gh repo clone dipikasgp/talkintunes
    ```

2. Navigate to the project directory:

    ```bash
    cd talkintunes
    ```

3. Install dependencies using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables (if any).

## Usage

1. Start the Flask server:

    ```bash
    python talkintunes.py
    ```

2. Open your web browser and go to `http://localhost:5000` to view the application.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes and commit them: `git commit -am 'Add new feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Detailed Description
This is an end-to-end encrypted messaging app where a user sends a message encrypting with the 
receiver's public key and the receiver then decrypts the message with their own private key. 

### Signup: 
The app has a signup page where an user can signup with their username and email.  
![image](https://github.com/dipikasgp/talkintunes/assets/13978786/2f33c79a-0d94-4de1-aae7-f9cf2a9109c4)

### Login:
User can login with their email and password.  
![image](https://github.com/dipikasgp/talkintunes/assets/13978786/0acdbaf7-5399-410a-b85e-13dcaf9b2246)

 
### Account:
In the account page the user has an option to change their profile picture.    
![image](https://github.com/dipikasgp/talkintunes/assets/13978786/808c6576-b1d9-4cfd-866b-3e50db0be1ec)

 
### Reset Password:
Upon forgetting their password, user can request for a forgot password link which will be sent to their mailbox.                                            
![image](https://github.com/dipikasgp/talkintunes/assets/13978786/159da939-17f6-442c-b09f-e47128bb8093)

 
### Home page:
After an user logs in, he sees the homepage where he can see the list of users he has talked to. Also, he can see the list of users registered in the app.                                                
![image](https://github.com/dipikasgp/talkintunes/assets/13978786/0cbf226f-d39b-49e8-b42f-66c2996b13df)

Upon selecting an user, he can see the messages sent between them. He can only see the messages sent by the other user. Messages sent by him is not visible to the sender once it’s sent.  
 ![image](https://github.com/dipikasgp/talkintunes/assets/13978786/9e7646f1-5c44-4eb5-8bf0-e8c69a0cbfac)

### The messaging Logic: 
When a user signs up in the app, it generates a set of public and private key for that user. The private keys are stored in private_key folder (In future, will make it stored in user’s system location). And the public key is stored in db which all the other users in the network is able to see. 

### Message Send Logic: 
When a message is sent, it is first encrypted using RSA from python cryptography library and stored in db. 
Also, the message is then converted into a tune using music21 library and a midi file is generated. We convert this midi file to a mp3 file(For showing it in the webpage) by temporarily converting it to wav using fluidsynth and then Mp3 using pydub library, which is then stored in static folder following a naming convention – (User_id + timestamp). The path of this file is stored along with the message in the db.

### Message Receive Logic: 
In the receiving end, the messages are fetched and showed to the user in a mp3 format. On click on view message, the user will be able to see the message.
On click on view message the corresponding message is fetched from the db and decrypted with the receiver’s private key and shown to the receiver. 

## Future Scope
### 1. Create unique pairs of send and receiver note mapping
Create unique pairs of note mapping once a user starts a conversation with another user and store it in user_note_mapping table. This note mapping will then be unique to the pair of users. Also, the users should be able to regenrate the note mapping

### 2. Private Key storing in user's system and add a configuration where user can specify the file location 
Private keys are now stored in the service itself. Once the user registers for the app, the user should be able to download and store the private key with them. Which can be used to upload when the user wants to decrypt and view the message
