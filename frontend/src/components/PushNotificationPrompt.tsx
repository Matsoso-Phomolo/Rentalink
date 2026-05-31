import { useEffect, useState } from "react";

export default function PushNotificationPrompt() {
  const [supported, setSupported] = useState(false);
  const [permission, setPermission] =
    useState<NotificationPermission>("default");

  useEffect(() => {
    if ("Notification" in window && "serviceWorker" in navigator) {
      setSupported(true);
      setPermission(Notification.permission);
    }
  }, []);

  async function requestPermission() {
    if (!supported) return;

    const result = await Notification.requestPermission();
    setPermission(result);

    if (result === "granted") {
      new Notification("Rentalink alerts enabled", {
        body: "You will be ready to receive rental intelligence alerts.",
        icon: "/icons/icon-192.png",
      });
    }
  }

  if (!supported || permission === "granted") {
    return null;
  }

  return (
    <div className="rounded-2xl border border-cyan-800 bg-cyan-500/10 p-5">
      <p className="text-sm font-semibold text-cyan-300">
        Enable Rentalink Alerts
      </p>

      <p className="mt-2 text-sm text-gray-300">
        Allow browser notifications so Rentalink can notify you about overdue
        rent, payment risk, critical tenant alerts and operational events.
      </p>

      <button
        type="button"
        onClick={requestPermission}
        className="mt-4 rounded-xl border border-cyan-700 bg-cyan-500 px-4 py-2 text-sm font-semibold text-black"
      >
        Enable Notifications
      </button>
    </div>
  );
}
