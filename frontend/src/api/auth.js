import { API_URL } from "../config";
export async function getMe() {
  const res = await fetch(`${API_URL}/auth/me`, {
    credentials: "include",
  });
  console.log("auth/me response stuff", res.json());
  return res.json();
}