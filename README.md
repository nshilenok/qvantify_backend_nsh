# qvantify-back
A light backend for qvantify. It takes care of userID creation and handles interviews. It switches topics based on topics table. Note that fields 'sequence' and 'lenght' are required, while 'quit_after' will later be removed. Currently uses projects2, records2 and respondets2 tables instead of the original ones to keep the compatibility with the current approach.

# Endpoints

## Respondent

Used to collect email and consent from the user and returns a generated unique UUID.

**URL** : `/api/respondent/`

**Method** : `POST`

**projectID required** : yes, in headers: `projectId:[projectid]`

**externalId optional** : in headers: `externalId:[string]`


**Data constraints**

It currently does not validate emails, but it will in the future.

```json
{
	"email": "valid email",
	"consent": "plain text"
}
```

**Payload example**

```json
{
    "email": "iloveauth@example.com",
    "consent": "I agree"
}
```

### Success Response - returns a UUID

**Code** : `200 OK`

**Content example**
This pair of values must be referenced in headers and used for other endpoints for a semi-authentication.

```json
{
    "projectId": "2dc9a74a-93ad-4a50-b78b-58bc83533c44",
    "uuid": "c3259778-5cba-497d-9cf9-7eddee9c942e"
}
```

### Error Response

**Condition** : If project ID does not exist

**Code** : `500 Server error`

## Interview

A GET request to initialize the interview and return the first question. This must be called before attepmting to submit replies.

**URL** : `/api/interview/`

**Method** : `GET`

**UUID must have a relation with project ID, that is project ID must correspond to the provided uuid in respondets table**
**projectID required** : yes, in headers: `projectId:[projectid]`
**UUID required** : yes, in headers: `uuid:[userID]`

### First Answer

Optional GET parameter to define the first answer.

**Example** : `/api/interview/?first_answer=text`

This will automatically submit the first answer and output the response from GPT. Everything will be saved to the database.

IMPORTANT. It will only work if 'first question' is set in the database. Leaving the parameter with no value will be considered as null.

### Success Response

**Code** : `200 OK`

**Content example - interview is open**

```json
{
    "response": "That's great to hear that the technology has helped bring more structure to your caregiving responsibilities. What other tools have you used in your journey?",
    "status": "open"
}
```

**Content example - interview is closed**

```json
{
    "response": "That's great to hear that the technology has helped bring more structure to your caregiving responsibilities. I appreciate you sharing your experience and the challenges you've faced. Your dedication to your father-in-law's wellbeing is commendable. Thank you for your time and cooperation during this interview. If you have any other experiences or thoughts you'd like to share in the future, please feel free to do so. Have a great day!",
    "status": "closed"
}
```

### Error Response

**Condition** : If project ID or UUID, or relation does not exist

**Code** : `500 Server error`

## Reply

Used to chat with the bot and receive responses.

**URL** : `/api/reply/`

**Method** : `POST`

**UUID must have a relation with project ID, that is project ID must correspond to the provided uuid in respondets table**
**projectID required** : yes, in headers: `projectId:[projectid]`
**UUID required** : yes, in headers: `uuid:[userID]`


**Payload example**

```json
{
	"message": "I became more structured"
}
```


### Success Response - returns a UUID

**Code** : `200 OK`

**Content example of an ongoing interview**
This pair of values must be referenced in headers and used for other endpoints for a semi-authentication.

```json
{
    "response": "That's wonderful, homemade pancakes must be a real treat for your relatives. Shifting the conversation to another important aspect of caregiving, could you elaborate on how you use technology, services, or devices to aid you in your caregiving roles?",
    "status": "open"
}
```


**Content example of a closed interview**
This pair of values must be referenced in headers and used for other endpoints for a semi-authentication.

```json
{
    "response": "Thank you for sharing your experiences with me, and I had good laughs as well. Your dedication to traditional methods while still making use of technology where comfortable is admirable. Enjoy your pancake-making, hopefully with new recipes to try! Thanks again for your time.",
    "status": "closed"
}
```

### Error Response

**Condition** : If project ID, uuid, or relation does not exist. 

**Code** : `500 Server error`

**Condition** : If JSON is not valid

**Code** : `400 Server error`

## Project Details

A GET request to get project details

**URL** : `/api/project/`

**Method** : `GET`

**projectID required** : yes, in headers: `projectId:[projectid]`


### Success Response

**Code** : `200 OK`

**Content example - interview is open**

```json
{
    "answer_placeholder": "Enter answer...",
    "answer_title": "Answer",
    "collect_email": true,
    "colour": "#7D1BCA",
    "consent": "By proceeding, I hereby acknowledge and agree that I have read, understand, and consent to the collection and use of my personal information by Qvantify, as outlined in the",
    "consent_link": "https://www.qvantify.com/privacypolicy",
    "cta_abort": "Abort",
    "cta_next": "Next",
    "cta_reply": "Reply",
    "cta_restart": "Start a new session",
    "email_placeholder": "Enter e-mail",
    "email_title": "E-mail",
    "loading": "Loading...",
    "logo": "https://lwwyepvurqddbcbggdvm.supabase.co/storage/v1/object/public/logos/qvantifylogo%20(1).png",
    "name": "Health Demo",
    "question_title": "Question",
    "success_message": "Thank you for participating in the interview. We will be in touch to discuss potential compensation details in the coming days. Should you have any questions in the meantime, please feel free to contact us at help@domain.com.",
    "success_title": "Complete",
    "welcome_message": "We appreciate your involvement in this AI-led questionnaire for senior caregivers in the United Kingdom. Rest assured, this interview is completely confidential. Our aim is simply to understand your views and requirements. The interview is expected to last about 25 min (4 min in demo) and is split into 3 topics",
    "welcome_second_message": "As a token of our appreciation for your time and effort, we will be sending you a £0.00 gift card, applicable for local use, to your email.",
    "welcome_second_title": "Compensation",
    "welcome_title": "Welcome (Demo)"
}
```

### Error Response

**Condition** : If projectId is not valid or does not exist. 

**Code** : `500 Server error`
