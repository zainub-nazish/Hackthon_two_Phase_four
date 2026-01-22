import { redirect } from "next/navigation";

export default function DashboardHome() {
  // Redirect to tasks page
  redirect("/tasks");
}
