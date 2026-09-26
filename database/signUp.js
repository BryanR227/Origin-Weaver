import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth } from "./firebase";

const email = "test@example.com";
const password = "password123";

createUserWithEmailAndPassword(auth, email, password)
  .then((userCredential) => {
    console.log("User created:", userCredential.user);
  })
  .catch((error) => {
    console.error(error.message);
  });
