const TOKEN_KEY = "rentalink_token";
const LEGACY_TOKEN_KEY = "linelink_token";

let memoryToken: string | null = null;

function getStorage(): Storage | null {
  try {
    if (typeof window === "undefined" || !window.localStorage) return null;
    const testKey = "__rentalink_storage_test__";
    window.localStorage.setItem(testKey, "1");
    window.localStorage.removeItem(testKey);
    return window.localStorage;
  } catch {
    return null;
  }
}

export const tokenStorage = {
  get() {
    const storage = getStorage();
    const token = storage?.getItem(TOKEN_KEY) ?? storage?.getItem(LEGACY_TOKEN_KEY) ?? memoryToken;
    if (token && storage?.getItem(LEGACY_TOKEN_KEY) && !storage.getItem(TOKEN_KEY)) {
      storage.setItem(TOKEN_KEY, token);
      storage.removeItem(LEGACY_TOKEN_KEY);
    }
    return token;
  },
  set(token: string) {
    memoryToken = token;
    const storage = getStorage();
    storage?.setItem(TOKEN_KEY, token);
  },
  remove() {
    memoryToken = null;
    const storage = getStorage();
    storage?.removeItem(TOKEN_KEY);
    storage?.removeItem(LEGACY_TOKEN_KEY);
  }
};
