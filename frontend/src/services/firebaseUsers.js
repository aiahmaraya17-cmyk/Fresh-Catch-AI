import { doc, getDoc, setDoc, serverTimestamp } from 'firebase/firestore';
import { firestore } from './firebase';

export async function getOrCreateUserProfile(user, name = '') {
  const ref = doc(firestore, 'users', user.uid);
  const snapshot = await getDoc(ref);
  const stored = snapshot.exists() ? snapshot.data() : {};
  const profile = {
    uid: user.uid,
    name: stored.name || name || user.displayName || user.email?.split('@')[0] || 'FreshCatch User',
    email: user.email,
    role: stored.role || 'consumer',
    createdAt: stored.createdAt || serverTimestamp(),
    updatedAt: serverTimestamp()
  };
  await setDoc(ref, profile, { merge: true });
  return { ...profile, createdAt: stored.createdAt || new Date() };
}

export async function updateUserProfile(user, values) {
  const ref = doc(firestore, 'users', user.uid);
  await setDoc(ref, { ...values, updatedAt: serverTimestamp() }, { merge: true });
  return (await getDoc(ref)).data();
}
