import { useEffect, useState } from "react";

import { subscribeToPushNotifications } from "../utils/pushSubscription";

const API_BASE =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:9000";

export default function PushNotificationPrompt() {
  const [supported, setSupported] = useState(false);

  const [permission, setPermission] =
    useState<NotificationPermission>("default");

  const [saving, setSaving] = useState(false);

  const [message, setMessage] = useState("");

  useEffect(() => {
    if ("Notification" in window && "serviceWorker" in navigator) {
      setSupported(true);
      setPermission(Notification.permission);
    }
  }, []);

  async function saveSubscription(
    subscription: PushSubscription
  ) {
    const token = localStorage.getItem("access_token");

    const response = await fetch(
      `${API_BASE}/push-subscriptions`,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",

          ...(token
            ? {
                Authorization: `Bearer ${token}`,
              }
            : {}),
        },

        body: JSON.stringify(subscription),
      }
    );

    if (!response.ok) {
      throw new Error(
        "Failed to save push subscription."
      );
    }
  }

  async function requestPermission() {
    if (!supported) return;

    setSaving(true);
    setMessage("");

    try {
      const result =
        await Notification.requestPermission();

      setPermission(result);

      if (result !== "granted") {
        setMessage(
          "Notifications were not enabled."
        );

        return;
      }

      const subscription =
        await subscribeToPushNotifications();

      await saveSubscription(subscription);

      new Notification(
        "Rentalink alerts enabled",
        {
          body:
            "You are ready to receive rental intelligence alerts.",

          icon: "/icons/icon-192.png",
        }
      );

      setMessage(
        "Rentalink alerts are enabled."
      );
    } catch (error) {
      console.error(
        "Failed to enable push notifications",
        error
      );

      setMessage(
        "Could not enable notifications. Please try again."
      );
    } finally {
      setSaving(false);
    }
  }

  if (
    !supported ||
    permission === "granted"
  ) {
    return null;
  }

  return (
    <div className="rounded-2xl border border-cyan-800 bg-cyan-500/10 p-5">
      <p className="text-sm font-semibold text-cyan-300">
        Enable Rentalink Alerts
      </p>

      <p className="mt-2 text-sm text-gray-300">
        Allow browser notifications so Rentalink can
        notify you about overdue rent, payment risk,
        critical tenant alerts and operational events.
      </p>

      {message ? (
        <p className="mt-3 text-sm text-yellow-300">
          {message}
        </p>
      ) : null}

      <button
        type="button"
        onClick={requestPermission}
        disabled={saving}
        className="mt-4 rounded-xl border border-cyan-700 bg-cyan-500 px-4 py-2 text-sm font-semibold text-black disabled:opacity-60"
      >
        {saving
          ? "Enabling..."
          : "Enable Notifications"}
      </button>
    </div>
  );
}
