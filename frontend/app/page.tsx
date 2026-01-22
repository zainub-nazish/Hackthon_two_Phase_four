import { redirect } from "next/navigation";

export default function Home() {
  // Redirect to login page (auth guard will redirect to tasks if authenticated)
  redirect("/login");
}
