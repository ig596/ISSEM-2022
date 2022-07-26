
# Lab 7
### Group Members: (Andrew Quijano, afq2003), (Isaiah Genis | ig596), (Jamie Leach | jhl925), (Yevhen Pankevych | yp2525)

### Summary of Vulnerability
During a static code review a vulnerability was discovered in the application’s communication layer which allows for a replay attack which can compromise the incubator as an attacker who is intercepting a legitimate client’s traffic connection to the application/server could fraudulently delay, misdirect, or replay commands issued by the client. Based on [FDA guidelines](https://www.fda.gov/media/119933/download) page 29 medical devices should: “Implement anti-replay measures in critical communications such as potentially harmful commands. This can be accomplished with the use of cryptographic nonces (an arbitrary number used only once in a cryptographic communication)”
Risk Assessment
This vulnerability is considered a critical severity vulnerability as it affects the legitimacy of configuration settings/commands run by the user.

### How it could be exploited
Should a user with his token send a SET_DEGF request, and someone listens to this traffic, since the token remains valid, even though the traffic is encrypted, the attacker would be able to resend the intercepted packet and the system will think that the authenticated user is requesting to execute SET_DEGF again.  

### Remediation approach
#### Note our remediation was built on top of fixes we made in Lab 6 prior to clarification, but is still relevant with respect to client tokens with or without our implementation. For details on those changes please see [changes.md](changes.md)


We implement a patch which can regenerate the token used in communications between the client and server function to a nonce. We will modify server response’s to client requests so that it contains a new token which replaces the current session key and is sent encrypted to the client; therefore when the real client makes requests again the attacker cannot get a new token even if he intercepts the traffic.
