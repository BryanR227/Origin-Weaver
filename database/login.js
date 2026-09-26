import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "./firebase";

signInWithEmailAndPassword(auth, email, password)
  .then((userCredential) => {
    console.log("Logged in:", userCredential.user);
  })
  .catch((error) => {
    console.error(error.message);
  });
